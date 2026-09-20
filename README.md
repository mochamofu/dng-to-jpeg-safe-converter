# DNG Safe JPEG Converter

[日本語](#日本語) | [English](#english)

A safety-first Windows desktop app that batch-converts DNG/Apple ProRAW files to lightweight JPEGs while preserving writable EXIF/XMP metadata through ExifTool.

> The app never deletes or modifies the source DNG files. Existing JPEGs are never overwritten.

## 日本語

### これは何？

大容量のDNG・Apple ProRAW写真を軽量JPEGへ一括変換するWindows用GUIです。撮影日時、GPS、カメラ機種、レンズ、向きなど、JPEGへ書き込めるEXIF/XMP情報をExifToolで引き継ぎます。

### 主な機能

- DNGフォルダと出力先をGUIで選択
- JPEG品質60〜100（既定92）
- 最初の10枚だけテスト
- 全件一括変換
- 変換前後の合計容量を表示
- サブフォルダ構造を維持
- 主要メタデータを変換後に読み戻して確認
- 途中停止対応
- 公式ExifTool 13.59（64-bit）をEXE内に内蔵
- ExifToolの別途ダウンロード・インストール・場所指定は不要

### 安全設計

- 元DNGは読み取りだけで、変更・削除しません。
- 出力先に同名JPEGがある場合はスキップします。
- JPEG生成とExifTool処理が完了するまで、一時ファイルとして扱います。
- アプリに自動アップロード、クラウド同期、元ファイル削除機能はありません。
- 写真、GPS、設定情報を外部へ送信する通信機能はありません。

### Windowsで使う

1. Releasesから `DNG-to-JPEG-Windows-Portable.zip` をダウンロードして展開します。
2. `DNG-to-JPEG.exe` を起動します。
3. DNGフォルダと出力先を指定します。
4. 最初に「最初の10枚をテスト」を実行します。
5. 画質・日時・位置情報・向きを確認してから全件変換します。

ExifToolは配布EXE内に内蔵されているため、別途準備する必要はありません。実行時に写真やGPS情報をネットワークへ送信することもありません。

配布EXEは現時点ではコード署名されていません。そのためWindows SmartScreenが初回起動時に確認を表示する場合があります。署名のないEXEを使いたくない場合は、公開ソースから `scripts/build-exe.bat` で自身のPC上にビルドしてください。

### ソースから起動

Python 3.10以降を用意し、`scripts/run.bat` をダブルクリックします。ソースから直接起動する場合は外部ExifToolが必要です。`scripts/build-exe.bat` は公式ExifToolの固定バージョンをハッシュ検証し、内蔵済みポータブル版を作成します。

### JPEG画質について

品質92は容量と見た目のバランスを重視した設定です。保存重視なら95を推奨します。JPEGはDNGのRAW編集耐性を保持しないため、元DNGは外付けドライブなどへ別途保管してください。

Apple写真アプリ独自のProRAW現像とは処理が異なるため、色・明るさ・HDR表現が完全に同じにならない場合があります。全件変換前に必ずテストしてください。

### ライセンスと商用利用

アプリ本体のソースコードは **GNU GPL v3.0 only** です。商用利用・販売は禁止していませんが、改変版を配布する場合はGPL-3.0の条件に従い、対応するソースコードを同じライセンスで提供する必要があります。

導入支援、カスタマイズ、保守、独自パッケージなどの有償サービスを提供することもできます。第三者ソフトウェアの条件は [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) を確認してください。

## English

### What it does

DNG Safe JPEG Converter is a Windows GUI for batch-developing DNG and Apple ProRAW files into smaller JPEG files. It uses ExifTool to transfer writable EXIF/XMP metadata such as capture time, GPS, camera model, lens, and orientation.

### Safety guarantees

- Source DNG files are read-only and are never deleted or modified.
- Existing JPEG files are skipped rather than overwritten.
- Each output remains temporary until image encoding and metadata transfer succeed.
- There is no automatic cloud upload or source-file deletion.
- There is no telemetry or photo upload.

### Quick start

1. Download and extract `DNG-to-JPEG-Windows-Portable.zip` from Releases.
2. Run `DNG-to-JPEG.exe`.
3. Select the source and output folders.
4. Run the 10-file test first, inspect the output, and only then run the full batch.

Official ExifTool 13.59 (64-bit) is embedded in the release executable. No separate ExifTool download, installation, or path selection is required. The app does not upload photos or GPS data at runtime.

The release executable is currently unsigned, so Windows SmartScreen may display a warning on first launch. Users who prefer not to run an unsigned release can inspect the source and build locally with `scripts/build-exe.bat`.

### Build from source

Install Python 3.10 or newer, then run:

```powershell
scripts\run.bat
```

To build the standalone executable:

```powershell
scripts\build-exe.bat
```

The build script downloads the pinned official ExifTool archive, verifies its SHA-256 digest, and embeds it in the executable. Running directly from source still requires an external ExifTool executable.

### License

The application source is licensed under **GNU GPL v3.0 only**. Commercial use is allowed. Distribution of modified versions must comply with GPL-3.0, including corresponding-source obligations. See [LICENSE](LICENSE) and [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).

## Important disclaimer

This project is not affiliated with or endorsed by Apple Inc. or Phil Harvey/ExifTool. Always keep an independent backup of irreplaceable source photos. The software is provided without warranty; see the GPL license for details.
