import contextlib
import io
import unittest
from unittest.mock import Mock, patch

from PIL import Image

import image_matching as matching


class PixelMatchingTests(unittest.TestCase):
    def test_last_row_and_column_are_searched(self):
        source = Image.new("RGB", (5, 4), "black")
        target = Image.new("RGB", (2, 2), "red")
        source.paste(target, (3, 2))
        self.assertEqual(matching.find_image(source, target), (3, 2))

    def test_same_size_and_one_pixel_targets(self):
        image = Image.new("RGB", (1, 1), "blue")
        self.assertEqual(matching.find_image(image, image), (0, 0))

    def test_rgb_and_rgba_compare_the_same_visible_channels(self):
        self.assertEqual(matching.find_image(Image.new("RGB", (2, 2), "red"),
                                             Image.new("RGBA", (2, 2), (255, 0, 0, 128))), (0, 0))

    def test_missing_match_and_larger_target(self):
        self.assertIsNone(matching.find_image(Image.new("RGB", (2, 2), "red"),
                                             Image.new("RGB", (2, 2), "blue")))
        self.assertIsNone(matching.find_image(Image.new("RGB", (1, 1)), Image.new("RGB", (2, 2))))

    def test_tolerance_boundary_is_inclusive(self):
        source = Image.new("RGB", (2, 2), (30, 0, 0))
        target = Image.new("RGB", (2, 2))
        self.assertEqual(matching.find_image(source, target, tolerance=30), (0, 0))
        self.assertIsNone(matching.find_image(source, target, tolerance=29))

    def test_bad_inputs_fail_without_showing_a_window(self):
        for tolerance in (-1, 256, True):
            with self.assertRaises(ValueError):
                matching.find_image(Image.new("RGB", (1, 1)), Image.new("RGB", (1, 1)), tolerance=tolerance)
        with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as error:
            matching.main(["missing-synthetic-source.png", "missing-synthetic-target.png"])
        self.assertEqual(error.exception.code, 2)


class OrbMatchingTests(unittest.TestCase):
    def test_binary_distance_and_short_neighbor_rows(self):
        cv2 = Mock()
        descriptors = object()
        cv2.ORB_create.return_value.detectAndCompute.side_effect = [([], descriptors), ([], descriptors)]
        good, second = Mock(distance=1), Mock(distance=10)
        cv2.BFMatcher.return_value.knnMatch.return_value = [[], [good], [good, second]]
        with patch.dict("sys.modules", {"cv2": cv2}):
            result = matching.orb_matches(Mock(size=1), Mock(size=1))
        cv2.BFMatcher.assert_called_once_with(cv2.NORM_HAMMING, crossCheck=False)
        self.assertEqual(result[2], [[good]])

    def test_featureless_images_have_no_matches(self):
        cv2 = Mock()
        cv2.ORB_create.return_value.detectAndCompute.return_value = ([], None)
        with patch.dict("sys.modules", {"cv2": cv2}):
            self.assertEqual(matching.orb_matches(Mock(size=1), Mock(size=1))[2], [])
            with self.assertRaises(ValueError):
                matching.orb_matches(None, Mock(size=1))
        cv2.BFMatcher.assert_not_called()


class ActualOpenCvTests(unittest.TestCase):
    def setUp(self):
        try:
            import cv2
            import numpy
        except ImportError:
            self.skipTest("optional OpenCV/NumPy runtime is not installed")
        self.cv2, self.numpy = cv2, numpy

    def test_synthetic_texture_produces_real_hamming_matches(self):
        image = self.numpy.random.default_rng(20261026).integers(0, 256, (256, 256), dtype=self.numpy.uint8)
        points, target_points, good = matching.orb_matches(image, image.copy())
        self.assertGreater(len(points), 0)
        self.assertGreater(len(target_points), 0)
        self.assertGreater(len(good), 0)
        self.assertTrue(all(pair[0].distance == 0 for pair in good))

    def test_real_featureless_images_are_an_empty_result(self):
        image = self.numpy.zeros((128, 128), dtype=self.numpy.uint8)
        self.assertEqual(matching.orb_matches(image, image)[2], [])
        with self.assertRaises(ValueError):
            matching.orb_matches(None, image)


if __name__ == "__main__":
    unittest.main()
