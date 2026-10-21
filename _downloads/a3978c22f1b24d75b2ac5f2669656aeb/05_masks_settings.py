"""Tutorial 5: masks, settings files and a run saved as a script.

Run:  python 05_masks_settings.py
"""
import subprocess
import sys
import brainsp

folder = brainsp.mock.write_examples("examples")
spectrum = f"{folder}/spectra/mock_star_forming_lines.spec"
mask = f"{folder}/masks/emission_lines.sm"

# spop has no emission lines in its model, so mask them out.
unmasked = brainsp.fit_spectrum(spectrum, output_dir="fits/nomask", quiet=True)
masked = brainsp.fit_spectrum(spectrum, output_dir="fits/mask", quiet=True, mask=mask)
print(f"no mask    : sigma {unmasked.sigma:6.1f}  A_V {unmasked.av:.3f}  chi2 {unmasked.chi2:.3f}")
print(f"lines out  : sigma {masked.sigma:6.1f}  A_V {masked.av:.3f}  chi2 {masked.chi2:.3f}")

# Your own mask: (start, end, weight, note). Weight 0 excludes, 2 doubles.
brainsp.write_mask("my_mask.sm", [
    (5570.0, 5590.0, 0.0, "sky [O I] 5577"),
    (3910.0, 3990.0, 2.0, "Ca II H and K, double weight"),
] + [(lo, hi, 0.0, "") for lo, hi in brainsp.STANDARD_OPTICAL_MASK])

# Settings: every name is documented and checked.
print(len(brainsp.Settings.names()), "settings")
print(brainsp.Settings.describe("dispersion_range"))
s = brainsp.Settings(nebular_mode="espop", wavelength_scale="vacuum")
s.dust_range = [-1.0, 3.0]
s.ages = [1e7, 1e8, 1e9, 5.01e9, 1.26e10]
print(s)                                   # only what differs from the defaults
try:
    s.dust_rnge = [0, 1]                   # a typo is refused, never ignored
except KeyError as error:
    print("KeyError:", error)

s.copy(spectrum=spectrum).validate()       # check before fitting
s.save("my_settings.yaml")
print("reloaded equal:", brainsp.Settings("my_settings.yaml") == s)

# The whole run as one Python file, each spectrum with its own corrections.
brainsp.write_script("run_my_spectra.py", settings=s, spectra=[
    spectrum,
    (f"{folder}/spectra/mock_observed_frame.spec",
     dict(spectrum_redshift=0.03, spectrum_in_rest_frame=False, galactic_ebv=0.05))])
check = subprocess.run([sys.executable, "run_my_spectra.py", "--check"],
                       capture_output=True, text=True)
print(check.stdout.strip())
