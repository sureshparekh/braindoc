"""Tutorial 4: observed-frame spectra and a batch with a corrections table.

Run:  python 04_many_spectra.py
"""
import time
import brainsp

folder = brainsp.mock.write_examples("examples") + "/spectra"

# One spectrum at z = 0.03 behind Galactic dust E(B-V) = 0.05.
# BRAIN dereddens, moves it to the rest frame, then fits.
r = brainsp.fit_spectrum(f"{folder}/mock_observed_frame.spec",
                         output_dir="fits/observed", quiet=True,
                         spectrum_redshift=0.03, spectrum_in_rest_frame=False,
                         galactic_ebv=0.05)
rest = brainsp.fit_spectrum(f"{folder}/mock_old_population.spec",
                            output_dir="fits/observed", quiet=True)
print(f"observed frame : v0 {r.v0:.2f}  sigma {r.sigma:.2f}  A_V {r.av:.3f}")
print(f"rest-frame twin: v0 {rest.v0:.2f}  sigma {rest.sigma:.2f}  A_V {rest.av:.3f}")

# A table: one spectrum per row with its z, E(B-V), R_V and law.
print("\n" + open(f"{folder}/corrections.csv").read())
table = brainsp.read_corrections_table(f"{folder}/corrections.csv")

# One call fits them all; a batch shares one set of settings, so the
# two spectra with emission lines (which need espop) are left out.
spectra = [p for p in table if "seyfert" not in p and "star_forming" not in p]
start = time.time()
results = brainsp.fit_spectra(spectra, corrections=table,
                              output_dir="fits/batch", quiet=True)
print(f"{len(results)} spectra in {time.time() - start:.1f} s")
for res in results:
    print(f"  {res!r}")
