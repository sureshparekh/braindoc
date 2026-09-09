# Settings reference

Everything BRAIN does is controlled by `brain_setup.yaml`. The file is
commented in place; this page is the complete reference.

```bash
python run_brain.py --check    # validate without running
```

The validator checks types, ranges, that files exist and that requested
templates are in the catalogue — and reports **every** problem at once rather
than stopping at the first.

---

## 1. What to fit

| Setting | Default | Meaning |
|---|---|---|
| `spectrum` | — | Path to the spectrum. Accepts a wildcard for batch runs |
| `mask` | — | Optional mask file. Blank for none |

```yaml
spectrum: examples/spectra/10517-9102_10_19.spec
mask: examples/mask_10517-9102_10_19.txt
```

---

## 2. Wavelength range

| Setting | Default | Meaning |
|---|---|---|
| `wavelength_min` | — | Lower limit in Å. Blank uses everything |
| `wavelength_max` | — | Upper limit in Å |

Changing these changes the size of the problem, so JAX recompiles once. Keeping
one range across a batch keeps every run fast.

---

## 3. Stellar templates

| Setting | Default | Meaning |
|---|---|---|
| `base_folder` | `BasesGM/` | Directory holding `CATALOGUE.txt` |
| `ages` | `all` | List of ages in **years**, or `all` |
| `metallicities` | `all` | List of mass fractions, or `all` |
| `include_power_law` | `false` | Add a featureless AGN continuum |

```yaml
ages: [1e6, 1e7, 1e8, 1e9, 5.01e9, 1.26e10]
metallicities: [0.0076, 0.0190]
```

Values must match the catalogue exactly. If one does not, BRAIN lists the
nearest available.

---

## 4. Dust

| Setting | Default | Meaning |
|---|---|---|
| `reddening_law` | `CCM` | One of twelve — see [Extinction laws](extinction.md) |
| `dust_range` | `[0.0, 5.0]` | Bounds on $A_V$ in magnitudes |
| `young_extra_dust_range` | `[0.0, 5.0]` | Extra $A_V$ on young populations. `[0,0]` disables |

---

## 5. Stellar kinematics

| Setting | Default | Meaning |
|---|---|---|
| `velocity_range` | `[-2000, 5000]` | km/s. **Must contain your galaxy's velocity** |
| `dispersion_range` | `[10, 500]` | km/s. Typical galaxies are 50–300 |

If you know the redshift $z$, the velocity is roughly $z \times 300\,000$ km/s.

---

## 6. Gas emission lines

| Setting | Default | Meaning |
|---|---|---|
| `fit_emission_lines` | `true` | Only has effect when `nebular_mode` is not `off` |
| `gas_velocity_range` | `[-2000, 5000]` | The gas often moves differently from the stars |
| `gas_dispersion_range` | `[10, 500]` | |

!!! note "The dispersion floor"
    BRAIN raises the lower end of `gas_dispersion_range` to your spectrum's
    pixel width. A line narrower than one pixel cannot be drawn on the grid;
    allowing it lets the optimiser pin there and silently drive the line
    amplitudes to zero, destroying the Balmer decrement. Controlled by
    `floor_gas_dispersion_at_pixel_width`, and it only ever raises the bound.

---

## 7. Nebular physics

| Setting | Default | Meaning |
|---|---|---|
| `nebular_mode` | `off` | `off`, `continuum` or `full` — see [Nebular modes](modes.md) |
| `gas_temperature` | `10000.0` | Kelvin. Used when $T_e$ cannot be measured |
| `gas_density` | `100.0` | cm⁻³. Used when $n_e$ cannot be measured |
| `gas_metallicity` | `0.02` | Mass fraction; 0.02 is solar |

---

## 8. Fit quality vs speed

| Setting | Default | Meaning |
|---|---|---|
| `smoothness` | `1.0` | Regularisation. Higher gives smoother histories |
| `error_samples` | `0` | Monte Carlo resamples for error bars. `0` skips them |
| `reject_outliers` | `true` | Clip pixels the model cannot explain, then refit |
| `decompose_line_profiles` | `false` | Fit multiple kinematic components per line |
| `smoothness_order` | `1` | First or second differences in the regulariser |

Error bars are the expensive option — each resample is a complete refit.
Leave `error_samples` at 0 while exploring and turn it up for final runs.

---

## 9. Output

| Setting | Default | Meaning |
|---|---|---|
| `output_folder` | `brain_out` | Where results go |
| `make_plot` | `true` | Also write a PDF figure |

---

## 10. Speed

| Setting | Default | Meaning |
|---|---|---|
| `linear_solver` | `active_set` | `active_set` (exact) or `fista` (iterative) |
| `coarse_to_fine_grid` | `true` | Two-stage velocity grid search |
| `central_differences` | `false` | Central rather than forward differences in the Jacobian |
| `enforce_simplex` | `false` | Hard constraint that weights sum to 1 |
| `use_cached_engine` | `true` | Reuse compiled JAX kernels across runs |
| `use_cached_templates` | `true` | Reuse resampled templates |
| `device` | `auto` | `auto`, `cpu` or `gpu` |

!!! danger "Leave `linear_solver` on `active_set`"
    `fista` is an iterative approximation that stops before convergence. On the
    bundled example it put 51 populations at non-zero weight where the exact
    solver finds 15, with individual weights wrong by up to 97%. It exists for
    benchmarking, not for science.

!!! note "`enforce_simplex`"
    The normalisation flux is itself fitted within bounds, so the light
    fractions do not sum to exactly 1 before renormalisation. Forcing
    $\sum x = 1$ as a hard constraint costs $\chi^2$ and pins $\sigma_\star$.
    BRAIN renormalises the reported fractions to 100% regardless, so this is
    off by default.

---

## 11. Advanced

| Setting | Default | Meaning |
|---|---|---|
| `has_errorbars` | `true` | Set false if column 3 is absent or meaningless |
| `normalisation_wavelength` | `5500.0` | Where the spectrum and templates are normalised |
| `av_start`, `dispersion_start`, `v0_start` | | Starting guesses for the optimiser |
| `velocity_grid_step` | `150.0` | km/s spacing of the initial velocity search |
| `fit_tolerance` | `1e-5` | Convergence tolerance |
| `max_iterations` | `200` | Optimiser iteration cap |
| `outlier_threshold` | `3.0` | Sigma-clipping threshold |
| `ssp_flux_unit` | `Lsun` | `Lsun` or `cgs` — how the templates are normalised |
| `helium_abundance` | `0.25` | Mass fraction, for the nebular continuum |
| `lyman_escape_fraction` | `0.0` | Fraction of ionising photons escaping |
| `nebular_iterations` | `4` | Fixed-point iterations in `continuum` mode |
| `sc_max_iterations` | `5` | Self-consistency iterations in `full` mode |
| `sc_tolerance` | `0.15` | Self-consistency convergence threshold |
| `sc_damping` | `0.5` | Damping on the self-consistency update |

!!! warning "YAML and scientific notation"
    YAML 1.1 parses `1e6` as a **string**, not a number. BRAIN installs a
    custom resolver so both `1e6` and `1.0e+6` work as you expect. If you
    write your own loader, do not assume the same.
