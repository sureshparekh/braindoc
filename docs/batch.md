# Batch and datacubes

## Many spectra in one run

Use a wildcard:

```yaml
spectrum: data/*.spec
```

```bash
python run_brain.py
```

Templates, the resampled template matrix and the compiled JAX kernels all stay
loaded between spectra, so the marginal cost of each additional spectrum is
just the fit itself.

| | Cold single run | In a batch |
|---|---|---|
| Python + JAX import | ~5 s | paid once |
| JAX compilation | ~18 s first time | paid once |
| Template loading | ~1 s | paid once |
| **The fit** | 1.3–6.3 CPU-s | **1.3–6.3 CPU-s** |

Each spectrum writes its own pair of output files, named after the input.

!!! tip "Keep the shapes constant"
    Vary the wavelength range or the template selection between spectra and JAX
    recompiles for each new shape, destroying the advantage. Fix both across a
    batch.

---

## Datacubes

```bash
python fit_datacube.py --cube mycube.fits --out results/
```

Fits every spaxel above a signal-to-noise threshold and writes maps of the
fitted parameters.

`fit_megacube_jax.py` is the vectorised variant, which batches many spaxels
into a single set of kernel launches. This is where a GPU earns its place — the
card stays saturated instead of waiting on transfers.

---

## Parallelism and core count

BRAIN's kernels are already vectorised, and JAX will use the cores it is given.
On a shared machine, or when you want to fit several cubes at once, it is
usually more efficient to run **several single-core processes** than one
process with all cores.

```bash
# four spectra at a time, one core each
ls data/*.spec | xargs -P 4 -I{} taskset -c 0-3 \
    python run_brain.py --spectrum {}
```

The metric that matters for planning is **CPU-seconds per spectrum per core**,
not wall clock on an idle machine — because in production you will never have
the whole machine for one spectrum.

---

## From Python

```python
import brain_settings as bs
import brainv1

settings = bs.load("brain_setup.yaml")
settings["nebular_mode"] = "continuum"

for path in sorted(glob.glob("data/*.spec")):
    settings["spectrum"] = path
    cfg = bs.to_config(settings)
    cfg.output_summary  = f"out/{Path(path).stem}_summary.txt"
    cfg.output_spectrum = f"out/{Path(path).stem}_fitted.txt"
    brainv1.run(cfg)
```

Because the settings dictionary is reused, the templates and compiled kernels
are reused too. See the [Python API](api.md).
