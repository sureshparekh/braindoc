# Comparison with FADO

BRAIN implements the same physical method as
[FADO](https://www.spectralsynthesis.org/) (Gomes & Papaderos 2017). This page
sets out where the two agree and where they differ.

---

## What is the same

**The model.** The observed spectrum is a non-negative linear combination of
simple stellar populations, broadened and Doppler-shifted, reddened by a
physical extinction curve. No polynomials.

**The three modes.** BRAIN's `off`, `continuum` and `full` correspond to FADO's
`Self_Con` values 0, 1 and 2 — stellar-only, nebular continuum, and full
self-consistency between the ionising photon budget and the gas emission.

**Emission lines only when the gas is modelled.** In `off` mode the lines are
masked and not fitted at all, exactly as FADO's stellar-only mode does.

**Light fractions summing to 100%.** Reported fractions are renormalised, as
FADO does.

**Output format.** The summary file is laid out for STARLIGHT-compatible
readers, as FADO's is.

**Nebular physics.** Case B recombination, free-free, free-bound and two-photon
continuum, with the Balmer jump at 3646 Å.

---

## What differs

### The optimiser

| | FADO | BRAIN |
|---|---|---|
| Non-linear parameters | Differential evolution | Levenberg–Marquardt |
| Linear weights | — | Nested exact non-negative least squares |
| Derivatives | — | Analytic, via JAX |

FADO uses differential evolution, a global stochastic search. BRAIN uses
Levenberg–Marquardt on the eight non-linear parameters with the population
weights solved exactly at every step by an active-set NNLS.

The consequence is speed. Differential evolution needs many thousands of
function evaluations; LM with exact derivatives converges in tens. This is the
single largest difference between the two codes.

The trade is robustness against local minima. BRAIN mitigates it with a
coarse-to-fine velocity grid search before the LM step, which is where the
multi-modality actually lives.

### The linear solver

BRAIN solves the non-negative least squares problem **exactly**, by
Lawson–Hanson active set with masked KKT solves. An iterative approximation
(FISTA) is available for benchmarking and should not be used for science — on
the bundled example it placed 51 populations at non-zero weight where the exact
solver finds 15.

### Implementation

| | FADO | BRAIN |
|---|---|---|
| Language | Fortran | Python + JAX |
| Parallelism | MPI | Vectorised kernels, CPU or GPU |
| Compilation | Ahead of time | JIT, cached on disk |

### Error bars

FADO derives uncertainties from the differential-evolution population. BRAIN
uses Monte Carlo resampling, controlled by `error_samples`. This is off by
default because each resample is a complete refit.

---

## What BRAIN adds

- **Twelve extinction curves** selectable at runtime, against FADO's smaller set
- **Measured gas conditions** — $n_e$ from [S II] and $T_e$ from [O III],
  per spectrum, rather than assumed
- **A BPT gate on `full` mode**, so the ionising budget constraint is only
  applied where stellar photoionisation is a defensible assumption
- **An identifiability warning** when the Balmer jump falls outside the fitting
  range and the nebular continuum becomes degenerate with dust
- **A template coverage guard** that drops pixels no template can model, rather
  than fitting zeros
- **A desktop interface** with interactive masking and weighting

---

## Cross-checks performed

| Check | Result |
|---|---|
| Nebular strength, `continuum` vs `full` | $Q_{\rm eff} = 1.21\times10^{14}$ vs $1.18\times10^{14}$ — agree to 3% |
| Extinction curves | All twelve normalise to $k(5500\,\text{Å}) \approx 1$ |
| `CAL` / `CCC` / `HZ5` | Identical in the optical, as they should be |
| Balmer decrement recovery | Hα/Hβ = 4.36 recovered with the dispersion floor active |

!!! note "Calibration is ongoing"
    A direct spectrum-by-spectrum comparison against FADO on a common
    calibration set is in progress. Until that is published, treat BRAIN's
    absolute values as provisional and its relative trends as sound.

---

## References

- Gomes J. M., Papaderos P. (2017), *FADO: Spectral population synthesis
  through genetic optimization under self-consistency boundary conditions*,
  A&A 603, A63
- Cid Fernandes R. et al. (2005), *Semi-empirical analysis of SDSS galaxies —
  I. Spectral synthesis method*, MNRAS 358, 363
- Osterbrock D. E., Ferland G. J. (2006), *Astrophysics of Gaseous Nebulae and
  Active Galactic Nuclei*, 2nd ed.
