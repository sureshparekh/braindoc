"""Tutorial 6: fit a datacube and compare the maps with the truth.

Run:  python 06_datacube.py    (writes cube_out/, used by tutorial 7)
"""
import time
import numpy as np
from astropy.io import fits
import brainsp

cube = brainsp.mock.write_examples("examples") + "/cube/mock_cube.fits"

pipeline = brainsp.CubePipeline(
    cube,
    redshift=0.02,                         # the galaxy's z (required)
    settings=brainsp.Settings(nebular_mode="espop"),
    wavelength_scale="vacuum",             # MaNGA-like cubes are in vacuum
    sn_mask=[3, 10, 20],                   # S/N masks to compute
    fit_sn_threshold=3,                    # fit spaxels with S/N > 3
    output_dir="cube_out")
pipeline.validate()                        # check everything, fit nothing
start = time.time()
written = pipeline.run(log=lambda line: None)   # log=print to see progress
print(f"{written[0]}  in {time.time() - start:.0f} s")

# The megacube: every map, grouped.
c = brainsp.read_megacube(written[0])
for group, names in c.groups.items():
    print(f"{group:15s} {len(names):3d} maps, e.g. {names[:4]}")

# Fitted maps against the maps the mock was built from.
truth = fits.open(cube.replace(".fits", ".truth.fits"))
fitted = np.isfinite(c.plane("vrot_star"))
print(f"\n{fitted.sum()} spaxels fitted")
for label, plane, key in (("velocity", "vrot_star", "V"),
                          ("dispersion", "Sigma_star", "SIGMA"),
                          ("A_V", "Av", "AV")):
    d = (c.plane(plane) - truth[key].data)[fitted]
    print(f"{label:10s}: fit - truth  median {np.median(d):7.3f}, rms {np.sqrt(np.mean(d**2)):6.3f}")

# The same run as one editable file: python run_mock_cube.py
pipeline.export_script("run_mock_cube.py")
