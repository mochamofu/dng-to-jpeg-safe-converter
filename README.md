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
- ExifToolの公式配布名 `exiftool(-k).exe` をそのまま指定可能
- ダウンロードフォルダ内のExifToolを自動検出

### 安全設計

- 元DNGは読み取りだけで、変更・削除しません。
- 出力先に同名JPEGがある場合はスキップします。
- JPEG生成とExifTool処理が完了するまで、一時ファイルとして扱います。
- アプリに自動アップロード、クラウド同期、元ファイル削除機能はありません。
- 写真、GPS、設定情報を外部へ送信する通信機能はありません。

### Windowsで使う

1. [ExifTool公式サイト](https://exiftool.org/)からWindows版をダウンロードして解凍します。
2. ReleasesからZIPをダウンロードして展開します。
3. `DNG-to-JPEG.exe` を起動します。
4. DNGフォルダ、出力先、ExifToolを指定します。
5. 最初に「最初の10枚をテスト」を実行します。
6. 画質・日時・位置情報・向きを確認してから全件変換します。

ExifTool本体は本リポジトリおよび配布EXEに含まれません。

配布EXEは現時点ではコード署名されていません。そのためWindows SmartScreenが初回起動時に確認を表示する場合があります。署名のないEXEを使いたくない場合は、公開ソースから `scripts/build-exe.bat` で自身のPC上にビルドしてください。

### ソースから起動

Python 3.9以降を用意し、`scripts/run.bat` をダブルクリックします。初回だけ仮想環境と依存パッケージを作成します。

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

1. Download and extract ExifTool from the [official website](https://exiftool.org/).
2. Download and extract the latest Windows release ZIP.
3. Run `DNG-to-JPEG.exe`.
4. Select the source folder, output folder, and ExifTool executable.
5. Run the 10-file test first, inspect the output, and only then run the full batch.

ExifTool is not bundled with this project.

The release executable is currently unsigned, so Windows SmartScreen may display a warning on first launch. Users who prefer not to run an unsigned release can inspect the source and build locally with `scripts/build-exe.bat`.

### Build from source

Install Python 3.9 or newer, then run:

```powershell
scripts\run.bat
```

To build the standalone executable:

```powershell
scripts\build-exe.bat
```

### License

The application source is licensed under **GNU GPL v3.0 only**. Commercial use is allowed. Distribution of modified versions must comply with GPL-3.0, including corresponding-source obligations. See [LICENSE](LICENSE) and [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).

## Important disclaimer

This project is not affiliated with or endorsed by Apple Inc. or Phil Harvey/ExifTool. Always keep an independent backup of irreplaceable source photos. The software is provided without warranty; see the GPL license for details.
