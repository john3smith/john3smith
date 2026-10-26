# Image comparison 0.2.0

The comparison entry points now use the independently written `image_matching.py`.
Importing it does not read the repository's example images or open windows.
Provide your own image paths. No example images are needed for tests or releases.

```powershell
python 01BFMatcher.py source.png target.png
python 03Pillow.py source.png target.png
python 03Pillow5.py source.png target.png --tolerance 30
python -m unittest discover -p test_image_matching.py -v
```

Pillow is used for pixel matching; OpenCV and its NumPy dependency are used for
ORB. Both were already used by the older examples. `--show` is optional and
requires a GUI-capable image viewer/OpenCV build. Default execution prints JSON.
Unreadable inputs fail with exit status 2. No result does not mean that images
are equivalent: pixel matching returns a null position and ORB returns zero
good matches. ORB features are not a proof of identity.

Pixel matching checks every valid origin, including the last row/column and
equal-sized images. Both images are converted to RGB, consistently ignoring
alpha. Tolerance is the inclusive maximum difference for each RGB channel.
Large images can take time because the search is exhaustive.

ORB uses Hamming distance for binary descriptors, applies the two-neighbor
ratio filter, and handles featureless images or short neighbor rows. Tests use
synthetic pixels and mocks; actual synthetic OpenCV execution is recorded
separately in the task's verification receipt.

The other historical scripts and images retain their original provenance and
unverified rights status. This change grants no new redistribution license for
those files and does not include them in the comparison-tool release package.
