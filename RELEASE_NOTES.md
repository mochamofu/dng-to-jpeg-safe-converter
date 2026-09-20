# DNG Safe JPEG Converter v1.1.0

Fully portable Windows release.

## Highlights

- Safety-first DNG and Apple ProRAW to JPEG batch conversion
- Source files are never modified or deleted
- Existing JPEGs are never overwritten
- 10-file test mode before full conversion
- Official ExifTool 13.59 (64-bit) embedded in the executable
- No separate ExifTool download, installation, or path selection
- Pinned upstream archive with SHA-256 verification during builds
- Capture date, GPS, camera, lens, and orientation verification
- Before/after size summary and cancellation support
- False GPS-altitude warnings from harmless EXIF rounding are suppressed

## Quick start

1. Extract `DNG-to-JPEG-Windows-Portable.zip`.
2. Run `DNG-to-JPEG.exe`.
3. Choose the DNG and output folders.
4. Run the 10-file test and inspect the output before processing the full folder.

Keep an independent backup of irreplaceable DNG originals. The Windows executable is unsigned and may trigger a SmartScreen prompt.
