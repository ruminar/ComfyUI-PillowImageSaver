import tempfile
import unittest
from pathlib import Path
from unittest import mock

import numpy as np
from PIL import Image

import nodes


class _FakeTensor:
    def __init__(self, array):
        self._array = array

    def cpu(self):
        return self

    def numpy(self):
        return self._array


class _FailingImage:
    def save(self, file_handle, **_kwargs):
        file_handle.write(b"partial")
        raise OSError("simulated save failure")


class CounterTests(unittest.TestCase):
    def test_counter_continues_after_five_digits(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            Path(temp_dir, "image_9999.jpg").touch()
            Path(temp_dir, "image_10000.jpg").touch()

            self.assertEqual(nodes._next_counter(temp_dir, "image"), 10001)

    def test_counter_matches_stem_case_insensitively(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            Path(temp_dir, "Cat_0001.jpg").touch()

            self.assertEqual(nodes._next_counter(temp_dir, "cat"), 2)


class CommentTests(unittest.TestCase):
    def test_long_multibyte_comment_remains_valid_utf8(self):
        normalized = nodes._normalize_comment("祭" * 30000)

        self.assertLessEqual(len(normalized), nodes.MAX_JPEG_COMMENT_BYTES)
        self.assertEqual(normalized.decode("utf-8"), "祭" * (len(normalized) // 3))


class ExclusiveSaveTests(unittest.TestCase):
    def test_collision_retries_without_overwriting_existing_file(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            existing_path = Path(temp_dir, "image_0001.jpg")
            existing_path.write_bytes(b"keep")
            image = Image.new("RGB", (1, 1))

            used_counter = nodes._save_jpeg_exclusive(
                image,
                temp_dir,
                "image",
                1,
                {"format": "JPEG"},
            )

            self.assertEqual(used_counter, 2)
            self.assertEqual(existing_path.read_bytes(), b"keep")
            self.assertTrue(Path(temp_dir, "image_0002.jpg").is_file())

    def test_failed_save_removes_partial_file(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            with self.assertRaises(OSError):
                nodes._save_jpeg_exclusive(
                    _FailingImage(),
                    temp_dir,
                    "image",
                    1,
                    {"format": "JPEG"},
                )

            self.assertFalse(Path(temp_dir, "image_0001.jpg").exists())

    def test_node_retries_if_file_appears_after_counter_scan(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            existing_path = Path(temp_dir, "image_0001.jpg")
            existing_path.write_bytes(b"keep")
            tensor = _FakeTensor(np.zeros((1, 1, 3), dtype=np.float32))

            with mock.patch.object(nodes, "_next_counter", return_value=1):
                result = nodes.PillowImageJpegSave().save_images(
                    [tensor],
                    "image",
                    "none",
                    "none",
                    80,
                    "4:2:2",
                    False,
                    output_dir=temp_dir,
                )

            self.assertEqual(result, {})
            self.assertEqual(existing_path.read_bytes(), b"keep")
            self.assertTrue(Path(temp_dir, "image_0002.jpg").is_file())


if __name__ == "__main__":
    unittest.main()
