import sys
import tempfile
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from dng_to_jpeg_gui import (  # noqa: E402
    find_dng_files,
    human_size,
    metadata_mismatches,
    output_path_for,
)


class HelperTests(unittest.TestCase):
    def test_human_size(self):
        self.assertEqual(human_size(1024 * 1024), "1.00 MB")

    def test_output_path_preserves_subfolders(self):
        result = output_path_for(
            Path("C:/photos/trip/IMG_0001.DNG"),
            Path("C:/photos"),
            Path("D:/jpeg"),
        )
        self.assertEqual(result, Path("D:/jpeg/trip/IMG_0001.jpg"))

    def test_find_dng_files_is_case_insensitive(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "a.DNG").touch()
            (root / "b.dng").touch()
            (root / "ignore.jpg").touch()
            self.assertEqual(len(find_dng_files(root, recursive=False)), 2)

    def test_exif_rational_altitude_rounding_is_not_a_mismatch(self):
        source = {"GPSAltitude": 227.5271199}
        destination = {"GPSAltitude": 227.5271186}
        self.assertEqual(metadata_mismatches(source, destination), [])

    def test_real_metadata_difference_is_reported(self):
        source = {"Model": "iPhone 14 Pro"}
        destination = {"Model": "Different Camera"}
        self.assertEqual(metadata_mismatches(source, destination), ["Model"])


if __name__ == "__main__":
    unittest.main()
