"""Tutorial 1: fit one spectrum of an old stellar population.

Run:  python 01_first_spectrum.py
"""
import json
import brainsp

# Mock spectra and a cube with known answers (written once, then reused).
folder = brainsp.mock.write_examples("examples")
spectrum = f"{folder}/spectra/mock_old_population.spec"

# Fit with the defaults: stars only (spop), BasesGM, 3700-6900 A.
result = brainsp.fit_spectrum(spectrum, output_dir="fits", quiet=True)
print(result)

# The main numbers.
print(f"v0        = {result.v0:8.2f} km/s")
print(f"sigma     = {result.sigma:8.2f} km/s (observed)")
print(f"A_V       = {result.av:8.3f} mag")
print(f"<log age>_L = {result.mean_log_age_light:6.3f}")
print(f"<log age>_M = {result.mean_log_age_mass:6.3f}")
print(f"<Z>_L     = {result.mean_metallicity_light:8.4f}")
print(f"chi2/N    = {result.chi2:8.3f}")

# Compare with the values the mock was built with.
truth = json.load(open(spectrum.replace(".spec", ".truth.json")))
print("truth: v0 = {v}, sigma = {sigma}, A_V = {av}, "
      "<log age>_L = {mean_log_age_light:.3f}".format(**truth))

# The population vector: light (x) and mass fractions per template, in %.
p = result.populations
print("\n  x_j(%)  mass_j(%)   age (yr)      Z")
for row in p[p["x"] > 0.5]:
    print(f"  {row['x']:6.2f}  {row['mcor']:8.2f}  {row['age']:10.3g}  {row['Z']:.4f}")

# Files written by the fit.
print("\nfiles:", result.summary_file, result.fitted_file, sep="\n  ")

# Figures: the fit, a zoom on Mg b, the star formation history.
brainsp.plots.spectrum(result, "t01_spectrum.png")
brainsp.plots.spectrum(result, "t01_zoom.png", xlim=(5100, 5400), residuals=False)
brainsp.plots.sfh(result, "t01_sfh.png")
