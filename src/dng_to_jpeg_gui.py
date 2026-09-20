# SPDX-License-Identifier: GPL-3.0-only
# Copyright (C) 2026 mochamofu

from __future__ import annotations

import json
import os
import queue
import subprocess
import sys
import threading
import tkinter as tk
import traceback
from collections.abc import Callable, Iterable
from dataclasses import dataclass
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

import rawpy
from PIL import Image

APP_NAME = "DNG → JPEG 安全一括変換"
APP_VERSION = "1.0.1"
SUPPORTED_SUFFIXES = {".dng"}
METADATA_TAGS = (
    "DateTimeOriginal",
    "CreateDate",
    "ModifyDate",
    "GPSLatitude",
    "GPSLongitude",
    "GPSAltitude",
    "Make",
    "Model",
    "LensModel",
    "Orientation",
)


def app_data_dir() -> Path:
    base = os.environ.get("APPDATA") or str(Path.home())
    return Path(base) / "DNG-to-JPEG"


SETTINGS_FILE = app_data_dir() / "settings.json"


def human_size(value: int) -> str:
    size = float(max(value, 0))
    units = ("B", "KB", "MB", "GB", "TB")
    for unit in units:
        if size < 1024 or unit == units[-1]:
            if unit == "B":
                return f"{int(size):,} {unit}"
            return f"{size:,.2f} {unit}"
        size /= 1024
    return f"{value:,} B"


def windows_hidden_process_kwargs() -> dict:
    if os.name != "nt":
        return {}
    startupinfo = subprocess.STARTUPINFO()
    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    return {
        "startupinfo": startupinfo,
        "creationflags": subprocess.CREATE_NO_WINDOW,
    }


def run_exiftool(executable: Path, args: list[str]) -> subprocess.CompletedProcess[str]:
    """Run either exiftool.exe or the distributed exiftool(-k).exe safely.

    The (-k) build waits for Enter before closing. Supplying a newline through
    stdin lets the GUI support the download as-is without showing a console.
    """
    return subprocess.run(
        [str(executable), *args],
        input="\n",
        text=True,
        capture_output=True,
        encoding="utf-8",
        errors="replace",
        timeout=120,
        check=False,
        **windows_hidden_process_kwargs(),
    )


def validate_exiftool(executable: Path) -> tuple[bool, str]:
    if not executable.is_file():
        return False, "ExifToolの実行ファイルが見つかりません。"
    try:
        result = run_exiftool(executable, ["-ver"])
    except (OSError, subprocess.SubprocessError) as exc:
        return False, f"ExifToolを起動できません: {exc}"
    version = result.stdout.replace("-- press ENTER --", "").strip()
    if result.returncode != 0 or not version:
        detail = (result.stderr or result.stdout).strip()
        return False, f"ExifToolの確認に失敗しました。{detail}"
    return True, version.splitlines()[-1].strip()


def detect_exiftool() -> str:
    """Find common ExifTool download layouts without scanning the whole PC."""
    app_folder = (
        Path(sys.executable).parent if getattr(sys, "frozen", False) else Path(__file__).parent
    )
    direct_candidates = [
        app_folder / "exiftool.exe",
        app_folder / "exiftool(-k).exe",
    ]
    for candidate in direct_candidates:
        if candidate.is_file():
            return str(candidate)

    downloads = Path.home() / "Downloads"
    if downloads.is_dir():
        try:
            candidates = sorted(
                downloads.glob("exiftool*/**/exiftool*.exe"),
                key=lambda path: path.stat().st_mtime,
                reverse=True,
            )
            if candidates:
                return str(candidates[0])
        except OSError:
            pass
    return ""


def find_dng_files(source: Path, recursive: bool) -> list[Path]:
    iterator: Iterable[Path] = source.rglob("*") if recursive else source.iterdir()
    files = [
        path for path in iterator if path.is_file() and path.suffix.lower() in SUPPORTED_SUFFIXES
    ]
    return sorted(files, key=lambda item: str(item).casefold())


def output_path_for(source_file: Path, source_root: Path, output_root: Path) -> Path:
    relative = source_file.relative_to(source_root)
    return (output_root / relative).with_suffix(".jpg")


def render_dng_to_jpeg(source: Path, destination: Path, quality: int) -> None:
    """Develop a DNG without rotating pixels, so copied Orientation stays valid."""
    destination.parent.mkdir(parents=True, exist_ok=True)
    with rawpy.imread(str(source)) as raw:
        rgb = raw.postprocess(
            use_camera_wb=True,
            use_auto_wb=False,
            no_auto_bright=False,
            output_color=rawpy.ColorSpace.sRGB,
            output_bps=8,
            user_flip=0,
        )
    image = Image.fromarray(rgb, mode="RGB")
    image.save(
        destination,
        format="JPEG",
        quality=quality,
        optimize=True,
        progressive=True,
        subsampling="4:2:0",
    )


def copy_metadata(exiftool: Path, source: Path, destination: Path) -> tuple[bool, str]:
    result = run_exiftool(
        exiftool,
        [
            "-overwrite_original",
            "-m",
            "-TagsFromFile",
            str(source),
            "-all:all",
            "-unsafe",
            "-icc_profile",
            str(destination),
        ],
    )
    combined = "\n".join(part for part in (result.stdout, result.stderr) if part)
    combined = combined.replace("-- press ENTER --", "").strip()
    return result.returncode == 0, combined


def read_key_metadata(exiftool: Path, image_path: Path) -> dict:
    result = run_exiftool(
        exiftool,
        ["-j", "-n", *[f"-{tag}" for tag in METADATA_TAGS], str(image_path)],
    )
    if result.returncode != 0:
        return {}
    cleaned = result.stdout.replace("-- press ENTER --", "").strip()
    try:
        values = json.loads(cleaned)
        return values[0] if values else {}
    except (json.JSONDecodeError, TypeError):
        return {}


def metadata_summary(metadata: dict) -> str:
    found = []
    if metadata.get("DateTimeOriginal") or metadata.get("CreateDate"):
        found.append("撮影日時")
    if metadata.get("GPSLatitude") is not None and metadata.get("GPSLongitude") is not None:
        found.append("GPS")
    if metadata.get("Make") or metadata.get("Model"):
        found.append("カメラ")
    if metadata.get("Orientation") is not None:
        found.append("向き")
    return "・".join(found) if found else "主要項目なし（元DNG側に無い可能性）"


def metadata_mismatches(source: dict, destination: dict) -> list[str]:
    mismatches: list[str] = []
    for tag in METADATA_TAGS:
        source_value = source.get(tag)
        if source_value is None or source_value == "":
            continue
        destination_value = destination.get(tag)
        if destination_value is None or destination_value == "":
            mismatches.append(tag)
            continue
        if tag in {"GPSLatitude", "GPSLongitude", "GPSAltitude"}:
            try:
                # EXIF stores GPS values as rational numbers, so ExifTool may
                # round the final decimal very slightly when moving DNG -> JPEG.
                # Coordinates use a ~11 cm tolerance; altitude uses 1 mm.
                tolerance = 0.001 if tag == "GPSAltitude" else 0.000001
                if abs(float(source_value) - float(destination_value)) > tolerance:
                    mismatches.append(tag)
            except (TypeError, ValueError):
                if str(source_value) != str(destination_value):
                    mismatches.append(tag)
        elif str(source_value) != str(destination_value):
            mismatches.append(tag)
    return mismatches


@dataclass
class ConversionStats:
    requested: int = 0
    converted: int = 0
    skipped: int = 0
    failed: int = 0
    input_bytes: int = 0
    output_bytes: int = 0


class ConverterApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title(f"{APP_NAME}  v{APP_VERSION}")
        self.geometry("900x690")
        self.minsize(780, 610)
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        self.events: queue.Queue[tuple[str, object]] = queue.Queue()
        self.worker: threading.Thread | None = None
        self.cancel_event = threading.Event()
        self.cached_files: list[Path] = []
        self.cached_source: Path | None = None

        settings = self.load_settings()
        self.source_var = tk.StringVar(value=settings.get("source", ""))
        self.output_var = tk.StringVar(value=settings.get("output", ""))
        self.exiftool_var = tk.StringVar(value=settings.get("exiftool", "") or detect_exiftool())
        self.quality_var = tk.IntVar(value=int(settings.get("quality", 92)))
        self.recursive_var = tk.BooleanVar(value=bool(settings.get("recursive", True)))
        self.status_var = tk.StringVar(value="フォルダとExifToolを選択してください")
        self.size_var = tk.StringVar(value="変換前: —    変換後: —    削減量: —")
        self.progress_var = tk.DoubleVar(value=0)

        self.build_ui()
        self.after(100, self.process_events)

    def build_ui(self) -> None:
        outer = ttk.Frame(self, padding=16)
        outer.pack(fill="both", expand=True)
        outer.columnconfigure(1, weight=1)
        outer.rowconfigure(9, weight=1)

        ttk.Label(outer, text=APP_NAME, font=("Yu Gothic UI", 17, "bold")).grid(
            row=0, column=0, columnspan=3, sticky="w", pady=(0, 4)
        )
        ttk.Label(
            outer,
            text="DNGを現像してJPEG化し、ExifToolで撮影情報を引き継ぎます。元DNGは変更・削除しません。",
        ).grid(row=1, column=0, columnspan=3, sticky="w", pady=(0, 14))

        self.add_path_row(
            outer, 2, "DNGフォルダ", self.source_var, self.choose_source, directory=True
        )
        self.add_path_row(outer, 3, "出力先", self.output_var, self.choose_output, directory=True)
        self.add_path_row(
            outer,
            4,
            "ExifTool",
            self.exiftool_var,
            self.choose_exiftool,
            directory=False,
        )

        options = ttk.Frame(outer)
        options.grid(row=5, column=0, columnspan=3, sticky="ew", pady=(10, 8))
        ttk.Label(options, text="JPEG品質").pack(side="left")
        self.quality_spin = ttk.Spinbox(
            options, from_=60, to=100, width=6, textvariable=self.quality_var
        )
        self.quality_spin.pack(side="left", padx=(8, 22))
        ttk.Checkbutton(
            options,
            text="サブフォルダも対象（出力先にも同じ構造を作成）",
            variable=self.recursive_var,
            command=self.refresh_scan,
        ).pack(side="left")

        action_bar = ttk.Frame(outer)
        action_bar.grid(row=6, column=0, columnspan=3, sticky="ew", pady=(5, 8))
        self.scan_button = ttk.Button(action_bar, text="DNGを確認", command=self.refresh_scan)
        self.scan_button.pack(side="left")
        self.test_button = ttk.Button(
            action_bar,
            text="最初の10枚をテスト",
            command=lambda: self.start_conversion(10),
        )
        self.test_button.pack(side="left", padx=8)
        self.all_button = ttk.Button(
            action_bar, text="全件を変換", command=lambda: self.start_conversion(None)
        )
        self.all_button.pack(side="left")
        self.cancel_button = ttk.Button(
            action_bar, text="停止", command=self.request_cancel, state="disabled"
        )
        self.cancel_button.pack(side="right")

        ttk.Progressbar(outer, variable=self.progress_var, maximum=100).grid(
            row=7, column=0, columnspan=3, sticky="ew", pady=(4, 5)
        )
        ttk.Label(outer, textvariable=self.status_var).grid(
            row=8, column=0, columnspan=3, sticky="w"
        )

        log_frame = ttk.LabelFrame(outer, text="処理ログ", padding=8)
        log_frame.grid(row=9, column=0, columnspan=3, sticky="nsew", pady=(10, 8))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        self.log_text = tk.Text(log_frame, height=15, wrap="word", state="disabled")
        self.log_text.grid(row=0, column=0, sticky="nsew")
        log_scroll = ttk.Scrollbar(log_frame, orient="vertical", command=self.log_text.yview)
        log_scroll.grid(row=0, column=1, sticky="ns")
        self.log_text.configure(yscrollcommand=log_scroll.set)

        summary = ttk.Frame(outer)
        summary.grid(row=10, column=0, columnspan=3, sticky="ew")
        ttk.Label(summary, textvariable=self.size_var, font=("Yu Gothic UI", 10, "bold")).pack(
            side="left"
        )
        ttk.Button(summary, text="出力先を開く", command=self.open_output).pack(side="right")

        warning = ttk.Label(
            outer,
            text="安全仕様: 元DNGは読み取りのみ／既存JPEGは上書きせずスキップ／途中停止しても完成済みJPEGは残ります。",
            foreground="#8a4b08",
        )
        warning.grid(row=11, column=0, columnspan=3, sticky="w", pady=(8, 0))

    def add_path_row(
        self,
        parent: ttk.Frame,
        row: int,
        label: str,
        variable: tk.StringVar,
        command: Callable[[], None],
        directory: bool,
    ) -> None:
        ttk.Label(parent, text=label, width=13).grid(row=row, column=0, sticky="w", pady=4)
        ttk.Entry(parent, textvariable=variable).grid(
            row=row, column=1, sticky="ew", padx=(4, 8), pady=4
        )
        ttk.Button(
            parent,
            text="フォルダ選択" if directory else "ファイル選択",
            command=command,
        ).grid(row=row, column=2, sticky="e", pady=4)

    def choose_source(self) -> None:
        selected = filedialog.askdirectory(title="DNGが入っているフォルダを選択")
        if selected:
            self.source_var.set(selected)
            if not self.output_var.get().strip():
                self.output_var.set(str(Path(selected).parent / f"{Path(selected).name}_JPEG"))
            self.refresh_scan()

    def choose_output(self) -> None:
        selected = filedialog.askdirectory(title="JPEGの出力先フォルダを選択")
        if selected:
            self.output_var.set(selected)

    def choose_exiftool(self) -> None:
        selected = filedialog.askopenfilename(
            title="exiftool.exe または exiftool(-k).exe を選択",
            filetypes=[("ExifTool", "*.exe"), ("すべてのファイル", "*.*")],
        )
        if selected:
            self.exiftool_var.set(selected)
            ok, detail = validate_exiftool(Path(selected))
            if ok:
                self.append_log(f"ExifTool {detail} を確認しました。")
            else:
                messagebox.showerror("ExifTool確認エラー", detail)

    def refresh_scan(self) -> None:
        if self.worker and self.worker.is_alive():
            return
        source_text = self.source_var.get().strip()
        source = Path(source_text) if source_text else None
        if not source or not source.is_dir():
            self.cached_files = []
            self.cached_source = None
            self.status_var.set("DNGフォルダを選択してください")
            self.size_var.set("変換前: —    変換後: —    削減量: —")
            return
        try:
            self.cached_files = find_dng_files(source, self.recursive_var.get())
            self.cached_source = source
            total = sum(path.stat().st_size for path in self.cached_files)
        except OSError as exc:
            messagebox.showerror("読み取りエラー", str(exc))
            return
        self.status_var.set(f"DNG {len(self.cached_files):,}枚を検出")
        self.size_var.set(f"変換前: {human_size(total)}    変換後: —    削減量: —")
        self.append_log(f"確認: {len(self.cached_files):,}枚 / {human_size(total)}")
        self.save_settings()

    def validate_inputs(self) -> tuple[Path, Path, Path, int] | None:
        source_text = self.source_var.get().strip()
        output_text = self.output_var.get().strip()
        exiftool_text = self.exiftool_var.get().strip()
        if not source_text:
            messagebox.showerror("入力エラー", "DNGフォルダを選択してください。")
            return None
        if not output_text:
            messagebox.showerror("入力エラー", "出力先フォルダを選択してください。")
            return None
        if not exiftool_text:
            messagebox.showerror("入力エラー", "ExifToolの実行ファイルを選択してください。")
            return None
        source = Path(source_text)
        output = Path(output_text)
        exiftool = Path(exiftool_text)
        if not source.is_dir():
            messagebox.showerror("入力エラー", "DNGフォルダを選択してください。")
            return None
        if source.resolve() == output.resolve():
            messagebox.showerror(
                "入力エラー", "出力先はDNGフォルダとは別のフォルダにしてください。"
            )
            return None
        try:
            quality = int(self.quality_var.get())
        except (ValueError, tk.TclError):
            quality = 92
        if not 60 <= quality <= 100:
            messagebox.showerror("入力エラー", "JPEG品質は60〜100で指定してください。")
            return None
        ok, detail = validate_exiftool(exiftool)
        if not ok:
            messagebox.showerror("ExifTool確認エラー", detail)
            return None
        try:
            output.mkdir(parents=True, exist_ok=True)
        except OSError as exc:
            messagebox.showerror("出力先エラー", f"出力先を作成できません: {exc}")
            return None
        return source, output, exiftool, quality

    def start_conversion(self, limit: int | None) -> None:
        if self.worker and self.worker.is_alive():
            return
        validated = self.validate_inputs()
        if not validated:
            return
        source, output, exiftool, quality = validated
        files = find_dng_files(source, self.recursive_var.get())
        if not files:
            messagebox.showinfo("対象なし", "DNGファイルが見つかりませんでした。")
            return
        selected = files[:limit] if limit else files
        mode_name = "10枚テスト" if limit else "全件変換"
        if limit and len(selected) < 10:
            mode_name = f"{len(selected)}枚テスト"
        question = (
            f"{mode_name}を開始します。\n\n"
            f"対象: {len(selected):,}枚\n"
            f"出力先: {output}\n"
            f"JPEG品質: {quality}\n\n"
            "元DNGは変更・削除しません。既存JPEGは上書きしません。"
        )
        if not messagebox.askokcancel("変換の確認", question):
            return

        self.cancel_event.clear()
        self.set_running(True)
        self.progress_var.set(0)
        self.log_text.configure(state="normal")
        self.log_text.delete("1.0", "end")
        self.log_text.configure(state="disabled")
        self.append_log(f"{mode_name}を開始: {len(selected):,}枚")
        self.save_settings()
        self.worker = threading.Thread(
            target=self.convert_worker,
            args=(selected, source, output, exiftool, quality),
            daemon=True,
        )
        self.worker.start()

    def convert_worker(
        self,
        files: list[Path],
        source_root: Path,
        output_root: Path,
        exiftool: Path,
        quality: int,
    ) -> None:
        stats = ConversionStats(
            requested=len(files),
            input_bytes=sum(path.stat().st_size for path in files),
        )
        for index, source_file in enumerate(files, start=1):
            if self.cancel_event.is_set():
                self.events.put(("log", "停止しました。完成済みJPEGはそのまま残っています。"))
                break

            destination = output_path_for(source_file, source_root, output_root)
            self.events.put(("status", f"{index:,}/{len(files):,}  {source_file.name}"))
            if destination.exists():
                stats.skipped += 1
                stats.output_bytes += destination.stat().st_size
                self.events.put(("log", f"スキップ（既存）: {destination.name}"))
                self.events.put(("progress", index / len(files) * 100))
                continue

            temp_name = (
                f".{destination.stem}.dng2jpeg-{os.getpid()}-{threading.get_ident()}.tmp.jpg"
            )
            temp_path = destination.parent / temp_name
            try:
                source_metadata = read_key_metadata(exiftool, source_file)
                render_dng_to_jpeg(source_file, temp_path, quality)
                copied, exif_message = copy_metadata(exiftool, source_file, temp_path)
                if not copied:
                    raise RuntimeError(f"ExifTool: {exif_message}")

                metadata = read_key_metadata(exiftool, temp_path)
                mismatches = metadata_mismatches(source_metadata, metadata)
                destination.parent.mkdir(parents=True, exist_ok=True)
                temp_path.replace(destination)
                size = destination.stat().st_size
                stats.converted += 1
                stats.output_bytes += size
                self.events.put(
                    (
                        "log",
                        f"完了: {source_file.name} → {destination.name} "
                        f"({human_size(size)}) / {metadata_summary(metadata)}",
                    )
                )
                if mismatches:
                    self.events.put(
                        (
                            "log",
                            "  注意: 元DNGと一致を確認できなかった項目: " + ", ".join(mismatches),
                        )
                    )
            except Exception as exc:  # noqa: BLE001 - continue processing later files
                stats.failed += 1
                self.events.put(("log", f"失敗: {source_file.name} / {exc}"))
                if temp_path.exists():
                    try:
                        temp_path.unlink()
                    except OSError:
                        pass
            finally:
                self.events.put(("progress", index / len(files) * 100))

        self.events.put(("done", stats))

    def request_cancel(self) -> None:
        self.cancel_event.set()
        self.cancel_button.configure(state="disabled")
        self.status_var.set("現在の1枚が終わり次第、停止します…")

    def process_events(self) -> None:
        try:
            while True:
                event, payload = self.events.get_nowait()
                if event == "log":
                    self.append_log(str(payload))
                elif event == "status":
                    self.status_var.set(str(payload))
                elif event == "progress":
                    self.progress_var.set(float(payload))
                elif event == "done":
                    self.finish_conversion(payload)
        except queue.Empty:
            pass
        self.after(100, self.process_events)

    def finish_conversion(self, stats: object) -> None:
        if not isinstance(stats, ConversionStats):
            return
        self.set_running(False)
        reduction = stats.input_bytes - stats.output_bytes
        ratio = (reduction / stats.input_bytes * 100) if stats.input_bytes else 0
        self.size_var.set(
            f"変換前: {human_size(stats.input_bytes)}    "
            f"変換後: {human_size(stats.output_bytes)}    "
            f"削減量: {human_size(max(reduction, 0))} ({max(ratio, 0):.1f}%)"
        )
        state = "停止" if self.cancel_event.is_set() else "完了"
        self.status_var.set(
            f"{state}: 変換 {stats.converted:,} / スキップ {stats.skipped:,} / 失敗 {stats.failed:,}"
        )
        detail = (
            f"変換: {stats.converted:,}枚\n"
            f"既存のためスキップ: {stats.skipped:,}枚\n"
            f"失敗: {stats.failed:,}枚\n\n"
            f"変換前: {human_size(stats.input_bytes)}\n"
            f"変換後: {human_size(stats.output_bytes)}"
        )
        if stats.failed:
            messagebox.showwarning(
                "処理結果", detail + "\n\n失敗の詳細は処理ログを確認してください。"
            )
        else:
            messagebox.showinfo("処理結果", detail)

    def set_running(self, running: bool) -> None:
        normal_or_disabled = "disabled" if running else "normal"
        self.scan_button.configure(state=normal_or_disabled)
        self.test_button.configure(state=normal_or_disabled)
        self.all_button.configure(state=normal_or_disabled)
        self.quality_spin.configure(state=normal_or_disabled)
        self.cancel_button.configure(state="normal" if running else "disabled")

    def append_log(self, text: str) -> None:
        self.log_text.configure(state="normal")
        self.log_text.insert("end", text.rstrip() + "\n")
        self.log_text.see("end")
        self.log_text.configure(state="disabled")

    def open_output(self) -> None:
        output_text = self.output_var.get().strip()
        if not output_text:
            return
        output = Path(output_text)
        output.mkdir(parents=True, exist_ok=True)
        try:
            os.startfile(output)  # type: ignore[attr-defined]
        except OSError as exc:
            messagebox.showerror("フォルダを開けません", str(exc))

    def load_settings(self) -> dict:
        try:
            return json.loads(SETTINGS_FILE.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError, TypeError):
            return {}

    def save_settings(self) -> None:
        try:
            SETTINGS_FILE.parent.mkdir(parents=True, exist_ok=True)
            SETTINGS_FILE.write_text(
                json.dumps(
                    {
                        "source": self.source_var.get(),
                        "output": self.output_var.get(),
                        "exiftool": self.exiftool_var.get(),
                        "quality": int(self.quality_var.get()),
                        "recursive": self.recursive_var.get(),
                    },
                    ensure_ascii=False,
                    indent=2,
                ),
                encoding="utf-8",
            )
        except (OSError, ValueError, tk.TclError):
            pass

    def on_close(self) -> None:
        if self.worker and self.worker.is_alive():
            if not messagebox.askyesno(
                "変換中です",
                "変換を停止して閉じますか？\n現在処理中の1枚が終わるまで画面は閉じません。",
            ):
                return
            self.cancel_event.set()
            self.after(250, self.wait_then_close)
            return
        self.save_settings()
        self.destroy()

    def wait_then_close(self) -> None:
        if self.worker and self.worker.is_alive():
            self.after(250, self.wait_then_close)
        else:
            self.save_settings()
            self.destroy()


def show_fatal_error(exc: BaseException) -> None:
    root = tk.Tk()
    root.withdraw()
    messagebox.showerror(
        "起動エラー",
        f"アプリを起動できませんでした。\n\n{exc}\n\n{traceback.format_exc()}",
    )
    root.destroy()


if __name__ == "__main__":
    try:
        ConverterApp().mainloop()
    except Exception as error:  # noqa: BLE001 - last-resort GUI error dialog
        show_fatal_error(error)
