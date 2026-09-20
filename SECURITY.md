# Security Policy

## Reporting a vulnerability

Please do not publish an exploit, private photo, GPS coordinate, or personal path in a public issue. Contact the repository owner privately first and provide the smallest reproducible description possible.

## Security model

- The application performs local file processing only.
- It launches only the ExifTool executable selected by the user.
- It does not upload photos or telemetry.
- Source DNG files are never modified or deleted.
- Existing output JPEGs are never overwritten.

Users should download ExifTool only from <https://exiftool.org/> and verify release assets before use.

