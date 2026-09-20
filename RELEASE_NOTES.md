# DNG Safe JPEG Converter v1.0.1

First public-ready Windows release.

## Highlights

- Safety-first DNG and Apple ProRAW to JPEG batch conversion
- Source files are never modified or deleted
- Existing JPEGs are never overwritten
- 10-file test mode before full conversion
- EXIF/XMP transfer through user-supplied ExifTool
- Capture date, GPS, camera, lens, and orientation verification
- Before/after size summary and cancellation support
- False GPS-altitude warnings from harmless EXIF rounding are suppressed

## Before using

1. Download ExifTool from <https://exiftool.org/>.
2. Keep an independent backup of irreplaceable DNG originals.
3. Run the 10-file test and inspect the output before processing the full folder.

The Windows executable is unsigned and may trigger a SmartScreen prompt. ExifTool is not bundled.

