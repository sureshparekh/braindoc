"""Tutorial 7: maps, spaxels and diagnostics from a fitted megacube.

Run:  python 07_megacube.py    (after 06_datacube.py)
"""
import os
from astropy.io import fits
import brainsp

path = "cube_out/mock_cube-BRAIN_MEGACUBE.fits"
if not os.path.exists(path):
    raise SystemExit("Run 06_datacube.py first; it writes " + path)
c = brainsp.read_megacube(path)
P = brainsp.plots

# Maps: one, then six on a page.
P.map(c, "vrot_star", "t08_velocity.png", cmap="RdBu_r", scale="full",
      title="stellar velocity [km/s]")
P.maps(c, ["vrot_star", "Sigma_star", "Av", "Mage_L", "xo_light",
           "Halpha_6563  flux"], "t08_page.png")

# Single spaxels (row, column) and a star formation history.
P.spaxel(c, 8, 8, "t08_spaxel_centre.png")
P.spaxel(c, 8, 12, "t08_spaxel_ring.png", xlim=(6480, 6780))
P.sfh(c, "t08_sfh_centre.png", y=8, x=8)

# Line diagnostics, as diagrams and as a map.
P.diagnostic(c, "BPT [N II]", "t08_BPT_N_II.png")
P.diagnostic(c, "BPT [S II]", "t08_BPT_S_II.png")
P.diagnostic(c, "WHAN", "t08_WHAN.png")
P.map(c, "BPT [N II]", "t08_bpt_map.png")

# Maps as PNG, PDF and FITS (with sky coordinates) for papers or other tools.
for f in P.export_maps(c, "maps", ["vrot_star", "Sigma_star", "Av"],
                       formats=("png", "pdf", "fits")):
    print(f)

# One spaxel's populations against the truth.
light, mass = c.populations(8, 8)
truth = fits.open("examples/cube/mock_cube.truth.fits")
print(f"\ncentre, light older than 5 Gyr: {light[c.ages[:len(light)] > 5e9].sum():.1f} %"
      f"   truth: {100 * truth['OLD'].data[8, 8]:.1f} %")
