# Changelog

## 1.1.0 - 2026-09-20

- Embedded the official 64-bit ExifTool 13.59 distribution in the Windows executable.
- Removed ExifTool download, installation, and path-selection steps for release users.
- Added a reproducible fetch script with pinned version and SHA-256 verification.
- Added portable ZIP packaging to both the local build and GitHub Actions release.

## 1.0.1 - 2026-09-20

- Added public distribution documentation and third-party notices.
- Added automated helper tests.
- Avoided false GPS altitude mismatch warnings caused by harmless EXIF rational-number rounding.

## 1.0.0 - 2026-09-20

- Initial Windows GUI release.
- Added 10-file test mode, full batch conversion, size summaries, safe skipping, cancellation, and ExifTool metadata transfer.
