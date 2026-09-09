# Performance and JAX

## Where the time goes

Measured per spectrum on **one uncontended core**, with the compilation cache
warm:

| Mode | CPU-seconds |
|---|---|
| `off` | 1.3 |
| `continuum` | 2.8 |
| `full` | 6.3 |

`full` costs what it does because its self-consistency loop runs the entire
Levenberg–Marquardt optimisation up to five times. That outer loop is about 89%
of its total cost.

To measure on your own machine:

```bash
python benchmark.py                  # all three modes
python benchmark.py off continuum    # a subset
python benchmark.py --reps 5         # more repeats, median reported
```

!!! warning "Measure on an idle machine"
    On a shared server, competing jobs inflate every number here, sometimes by
    a factor of several, without a single line of BRAIN changing. `benchmark.py`
    samples the machine load first and tells you when the numbers are not
    trustworthy.

---

## JAX compilation

The first run on a new machine compiles roughly **180 JAX kernels**, which
takes about 18 seconds. That is a one-time cost: the result is written to an
on-disk cache and reused by every later run, including after a reboot.

### What reuses the cache

Changing any of these costs nothing — the compiled engine is reused as-is:

- `dust_range`, `velocity_range`, `dispersion_range`
- `smoothness`, `fit_tolerance`, `max_iterations`
- all starting guesses
- `normalisation_wavelength`
- **a different spectrum**, as long as it has the same pixel count after
  rebinning

### What forces a rebuild

These change the **shape** of the arrays, and JAX compiles per shape:

| Change | Extra kernels |
|---|---|
| Wavelength range | ~105 |
| Age or metallicity selection | ~50 |
| `nebular_mode` | ~47 |
| `reddening_law` | ~2, once per law |

This is why keeping one wavelength range and one template selection across a
batch matters so much. Vary them per spectrum and you pay the compilation cost
over and over.

---

## Batch runs are where this pays off

```yaml
spectrum: data/*.spec
```

In a batch, the compilation and the template loading happen **once** and every
subsequent spectrum costs only the fit itself. A hundred spectra cost far less
than a hundred separate invocations of `run_brain.py`.

The per-spectrum cost in a batch is the "fit total" row from `benchmark.py`,
not the wall clock of a single cold run.

!!! note "A single spectrum is not made faster by this"
    Caching removes a fixed startup cost. It does not make an individual fit
    faster. If your workflow is one spectrum at a time from a cold process, you
    pay Python and JAX import time (~5 s) on every one of them.

---

## CPU or GPU

| Situation | Recommendation |
|---|---|
| Single spectra, interactive work | CPU. Transfer overhead dominates on a problem this small |
| Datacubes, large batches | GPU, if you have one |
| No CUDA toolkit | CPU. The default JAX wheel |

```yaml
device: auto     # auto | cpu | gpu
```

`auto` uses a GPU whenever JAX can see one.

---

## Making it faster

Things that genuinely help, in rough order of effect:

1. **Use `off` mode** when you do not need the gas. It is 5× cheaper than
   `full`.
2. **Fewer templates.** 84 templates is generous. A well-spread set of 24 fits
   noticeably faster and is less degenerate — at the cost of a coarser history.
3. **A narrower wavelength range**, if the ends carry no information.
4. **Keep `error_samples: 0`** until final runs. Each resample is a full refit.
5. **Batch**, so compilation and template loading are amortised.

Things that do **not** help:

- Switching `linear_solver` to `fista`. It is faster per iteration and wrong.
- Turning off `coarse_to_fine_grid`. The coarse-to-fine search is already
  1.8× faster than the flat grid it replaced.

---

## Design notes

A few decisions that shaped the current speed:

**Dead parameter elimination.** Of eight non-linear parameters, five have
exactly zero effect in `off` mode — `YAV` when no template is flagged young,
and the four gas kinematic parameters when lines are not fitted. Ten of
seventeen Jacobian evaluations were computing exact zeros. Skipping them was
worth 2.9×.

**Forward differences.** Verified to give an identical $\chi^2$ to central
differences on the bundled example, at 1.44× the speed. Central differences
remain available via `central_differences: true`.

**Coarse-to-fine velocity search.** 28 evaluations at finer effective
resolution, against 47 for the flat grid it replaced.

**Hoisted Fourier transforms.** The template FFTs do not depend on the fitted
parameters, so they are computed once outside the optimisation loop rather than
at every function evaluation.
