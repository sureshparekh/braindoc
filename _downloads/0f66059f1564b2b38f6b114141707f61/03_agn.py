"""Tutorial 3: an active nucleus, fitted without and with AGN templates.

Run:  python 03_agn.py
"""
import json
import brainsp

folder = brainsp.mock.write_examples("examples")
spectrum = f"{folder}/spectra/mock_seyfert_agn.spec"
truth = json.load(open(spectrum.replace(".spec", ".truth.json")))

common = dict(quiet=True, nebular_mode="espop", wavelength_scale="vacuum")
plain = brainsp.fit_spectrum(spectrum, output_dir="fits/no_agn", **common)
# include_power_law adds 7 featureless AGN continua (light, no mass).
agn = brainsp.fit_spectrum(spectrum, output_dir="fits/agn",
                           include_power_law=True, **common)

print("                     no AGN templates   with AGN templates   truth")
print(f"AGN light fraction  {plain.agn_fraction:12.1f} %   "
      f"{agn.agn_fraction:12.1f} %     {100 * truth['agn_fraction']:.0f} %")
print(f"<log age>_L         {plain.mean_log_age_light:12.2f}     "
      f"{agn.mean_log_age_light:12.2f}       {truth['mean_log_age_light']:.2f}")
print(f"A_V                 {plain.av:12.3f}     {agn.av:12.3f}       {truth['av']:.2f}")
print(f"chi2/N              {plain.chi2:12.3f}     {agn.chi2:12.3f}")

# Without AGN templates, young stars imitate the blue power law.
def young_light(r):
    p = r.populations
    return p[(p["age"] < 1e8) & p["stellar"]]["x"].sum()
print(f"\nlight in stars < 100 Myr: {young_light(plain):.1f} % without, "
      f"{young_light(agn):.1f} % with")

# Only the sum (agn_fraction) is a measurement, not the split between these.
print("\nAGN components used:")
for row in agn.populations[~agn.populations["stellar"]]:
    if row["x"] > 0:
        print(f"  {row['name']:22s} {row['x']:6.2f} %")

brainsp.plots.sfh(plain, "t03_sfh_no_agn.png")
brainsp.plots.sfh(agn, "t03_sfh_agn.png")
