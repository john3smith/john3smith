"""Command-line ORB comparison; use your own source and target image paths."""
from image_matching import main

if __name__ == "__main__":
    raise SystemExit(main(default_mode="orb"))