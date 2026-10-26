"""Image matching helpers; importing this module never opens example files or a GUI."""
from __future__ import annotations

import argparse
import json
from pathlib import Path


VERSION = "0.2.0"


def find_image(source, target, *, tolerance=0):
    """Return the first complete RGB match, including the final valid position.

    Alpha is ignored consistently in both inputs. Every candidate position is
    searched so that one-pixel targets and odd final offsets are not skipped.
    """
    from PIL import ImageChops, ImageStat

    if type(tolerance) is not int or not 0 <= tolerance <= 255:
        raise ValueError("tolerance must be an integer from 0 to 255")
    source, target = source.convert("RGB"), target.convert("RGB")
    width, height = target.size
    if width < 1 or height < 1:
        raise ValueError("target must contain at least one pixel")
    if source.width < width or source.height < height:
        return None
    first = target.getpixel((0, 0))
    for y in range(source.height - height + 1):
        for x in range(source.width - width + 1):
            if any(abs(a - b) > tolerance for a, b in zip(source.getpixel((x, y)), first)):
                continue
            difference = ImageChops.difference(source.crop((x, y, x + width, y + height)), target)
            if all(high <= tolerance for _, high in ImageStat.Stat(difference).extrema):
                return x, y
    return None


def orb_matches(source, target, *, ratio=0.65):
    """Return keypoints and Hamming ratio matches for ORB binary descriptors."""
    import cv2

    if source is None or target is None or source.size == 0 or target.size == 0:
        raise ValueError("both images must be readable and nonempty")
    if not 0 < ratio < 1:
        raise ValueError("ratio must be between 0 and 1")
    detector = cv2.ORB_create()
    source_points, source_descriptors = detector.detectAndCompute(source, None)
    target_points, target_descriptors = detector.detectAndCompute(target, None)
    if source_descriptors is None or target_descriptors is None:
        return source_points, target_points, []
    matcher = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=False)
    neighbors = matcher.knnMatch(source_descriptors, target_descriptors, k=2)
    good = [[pair[0]] for pair in neighbors
            if len(pair) == 2 and pair[0].distance < ratio * pair[1].distance]
    return source_points, target_points, good


def main(argv=None, *, default_mode="exact"):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("target", type=Path)
    parser.add_argument("--mode", choices=("exact", "orb"), default=default_mode)
    parser.add_argument("--tolerance", type=int, default=0)
    parser.add_argument("--show", action="store_true", help="open the result image after comparison")
    args = parser.parse_args(argv)
    try:
        if args.mode == "orb":
            import cv2

            source = cv2.imread(str(args.source), cv2.IMREAD_GRAYSCALE)
            target = cv2.imread(str(args.target), cv2.IMREAD_GRAYSCALE)
            points, target_points, matches = orb_matches(source, target)
            result = {"version": VERSION, "mode": "orb", "good_matches": len(matches)}
            if args.show:
                image = cv2.drawMatchesKnn(source, points, target, target_points, matches, None, flags=2)
                cv2.imshow("ORB matches", image)
                cv2.waitKey(0)
                cv2.destroyAllWindows()
        else:
            from PIL import Image, ImageDraw

            with Image.open(args.source) as source, Image.open(args.target) as target:
                position = find_image(source, target, tolerance=args.tolerance)
                result = {"version": VERSION, "mode": "exact", "position": position}
                if args.show and position is not None:
                    output = source.convert("RGB")
                    x, y = position
                    ImageDraw.Draw(output).rectangle(
                        (x, y, x + target.width - 1, y + target.height - 1), outline="red")
                    output.show()
        print(json.dumps(result))
        return 0
    except (OSError, ValueError) as exc:
        parser.exit(2, f"Image comparison failed: {type(exc).__name__}\n")


if __name__ == "__main__":
    raise SystemExit(main())
