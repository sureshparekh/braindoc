"""Tutorial 2: a star-forming galaxy with emission lines (espop).

Run:  python 02_emission_lines.py
"""
import json
import numpy as np
import brainsp
from brainsp.megacube import bpt_nii_class

folder = brainsp.mock.write_examples("examples")
spectrum = f"{folder}/spectra/mock_star_forming_lines.spec"
truth = json.load(open(spectrum.replace(".spec", ".truth.json")))

# espop fits the stars and the emission lines together.
# Line fitting needs to know air or vacuum; the mocks are in vacuum.
r = brainsp.fit_spectrum(spectrum, output_dir="fits", quiet=True,
                         nebular_mode="espop", wavelength_scale="vacuum")
print(r)
print(f"stars: v0 = {r.v0:.1f} km/s, sigma = {r.sigma:.1f} km/s, A_V = {r.av:.3f}")
print(f"gas:   v  = {r.v_gas:.1f} km/s, sigma = {r.sigma_gas:.1f} km/s "
      f"(truth {truth['v_gas']}, {truth['sigma_gas']})")

# Line fluxes: as written (dereddened, normalised) and as observed.
written = r.lines
observed = r.line_fluxes(units="normalised", observed=True)
print("\n line              written   observed     truth")
for name, true_flux in truth["lines"].items():
    print(f" {name:16s} {written[name][0]:8.3f}   {observed[name][0]:8.3f}   {true_flux:8.3f}")

# In the units of the input spectrum times A.
physical = r.line_fluxes(units="input", observed=True)
print(f"\nH-alpha, input units: {physical['Halpha_6563'][0]:.4g}")

# BPT class from the observed ratios.
n2 = np.log10(observed["[N II]_6583"][0] / observed["Halpha_6563"][0])
o3 = np.log10(observed["[O III]_5007"][0] / observed["Hbeta_4861"][0])
cls = int(bpt_nii_class(np.array([n2]), np.array([o3]))[0])
print(f"log [N II]/Ha = {n2:.2f}, log [O III]/Hb = {o3:.2f} -> "
      f"{['', 'star forming', 'composite', 'LINER', 'Seyfert'][cls]}")

# Figures: the whole fit, then H-alpha and H-beta.
brainsp.plots.spectrum(r, "t02_spectrum.png")
brainsp.plots.spectrum(r, "t02_halpha.png", xlim=(6500, 6760), residuals=False)
brainsp.plots.spectrum(r, "t02_hbeta.png", xlim=(4820, 5040), residuals=False)
