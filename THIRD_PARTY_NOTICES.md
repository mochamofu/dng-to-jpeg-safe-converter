# Third-Party Notices

The standalone Windows executable is built with the components below. Their licenses apply to their respective components and are reproduced in the `licenses/` directory.

| Component | Version used for v1.1.0 | License | Project |
|---|---:|---|---|
| Python | 3.13.12 | PSF License and bundled notices | <https://www.python.org/> |
| rawpy | 0.27.1 | MIT | <https://github.com/letmaik/rawpy> |
| LibRaw | bundled by rawpy | LGPL-2.1 or CDDL-1.0 | <https://www.libraw.org/> |
| NumPy | 2.5.3 | BSD-3-Clause and bundled notices | <https://numpy.org/> |
| Pillow | 12.3.0 | HPND / MIT-CMU style | <https://python-pillow.github.io/> |
| PyInstaller | 6.22.3 | GPL-2.0-or-later with Bootloader Exception | <https://pyinstaller.org/> |
| Tcl/Tk | bundled with Python | BSD-style | <https://www.tcl-lang.org/> |
| ExifTool | 13.59 (official 64-bit Windows package) | Same terms as Perl itself; bundled package notices also apply | <https://exiftool.org/> |

PyInstaller's Bootloader Exception permits distributing executables built with its bootloader under the application's chosen license. LibRaw is used under LGPL-2.1 for this distribution.

The release executable embeds the official, unmodified ExifTool 13.59 Windows distribution. The upstream launcher is renamed from `exiftool(-k).exe` to `exiftool.exe`, as documented by the upstream package, to disable the command-line pause behavior. Its `exiftool_files` directory, source script, license, and Strawberry Perl notices are embedded with it. See `licenses/EXIFTOOL-NOTICE.txt` and the upstream files embedded in the executable.

This notice is informational and is not legal advice.
