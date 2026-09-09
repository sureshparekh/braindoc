# Python API

Everything the settings file does is available directly.

---

## A minimal fit

```python
import brain_settings as bs
import brainv1

settings = bs.load("brain_setup.yaml")
settings["spectrum"] = "data/mygalaxy.spec"
settings["nebular_mode"] = "continuum"

cfg = bs.to_config(settings)
cfg.output_summary  = "out/mygalaxy_summary.txt"
cfg.output_spectrum = "out/mygalaxy_fitted.txt"

brainv1.run(cfg)
```

Starting from the defaults instead of a file:

```python
settings = dict(bs.DEFAULTS)
settings.update(spectrum="data/mygalaxy.spec",
                wavelength_min=3700.0, wavelength_max=6900.0,
                reddening_law="CAL")
bs.validate(settings)
```

---

## The modules

### `brain_settings`

Reading, validating and translating settings.

| Function | Does |
|---|---|
| `DEFAULTS` | Dictionary of every setting and its default |
| `load(path)` | Read a YAML settings file |
| `validate(s, path=None)` | Check consistency; raises `SystemExit` listing every problem |
| `to_config(s)` | Turn a settings dict into a `Config` object |
| `read_catalogue(folder)` | Parse a template `CATALOGUE.txt` |
| `build_base_list(s, ssp, extra)` | Select templates by age and metallicity |

### `brainv1`

The pipeline.

| Function | Does |
|---|---|
| `run(cfg)` | Fit one spectrum and write the outputs |

### `optimizer`

| Class | Does |
|---|---|
| `SpectralFitter` | Holds the problem and runs the optimisation |

### `fast_engine`

The compiled forward model. `ForwardConstants` and `ForwardShapes` carry
everything the kernels need; shapes are static, constants are traced.

### `solver`

| Function | Does |
|---|---|
| `solve_active_set(ATA, ATb, cvec, ...)` | Exact non-negative least squares, Lawson–Hanson |

### `reddening_laws`

| Object | Does |
|---|---|
| `LAWS` | The registry: key → (reference, description) |
| `LAW_NAMES` | Tuple of valid keys |
| `get_k_lambda(wl, law_name)` | The curve, normalised to $k(5500) \approx 1$ |
| `describe(key)` | One-line summary |

```python
import numpy as np
import reddening_laws as R

wl = np.linspace(3700, 6900, 500)
k = R.get_k_lambda(wl, "CCM")
```

### `nebular`

| Object | Does |
|---|---|
| `NebularModel(lam, Te, ne, Y_He, Z_gas, f_esc)` | The nebular continuum |
| `compute_qh_ratios(ages, metals, norms, ...)` | Ionising photon output per template |

### `gas_diagnostics`

| Function | Does |
|---|---|
| `electron_density(ratio)` | $n_e$ from [S II] λ6716/λ6731 |
| `electron_temperature(ratio, ne)` | $T_e$ from [O III] λ4363/λ5007 |
| `measure_conditions(...)` | Both, from a fitted line set |
| `classify_bpt(...)` | Star-forming, composite, AGN or undetermined |
| `allowed_mode(...)` | Whether `full` is defensible for this spectrum |

### `io_utils`

| Function | Does |
|---|---|
| `load_spectrum(path)` | Read a four-column spectrum |
| `load_ssp_templates(folder, bases, target_wl, norm)` | Load and resample templates |
| `load_mask(path, wl)` | Per-pixel weights from a mask file |
| `write_summary(...)` | The summary file |
| `write_fitted_spectrum(...)` | The seven-column fit file |

### `brain_cache`

| Function | Does |
|---|---|
| `enable_jax_cache(verbose=True)` | Turn on the on-disk kernel cache |
| `load_ssp_templates_cached(...)` | Memoised template loading |
| `ssp_cache_key(...)` | Cache key for a template selection |

---

## The GUI modules

| Module | Holds |
|---|---|
| `brain_gui` | The application window and the fit thread |
| `brain_theme` | Palettes, fonts, drawn icons, the stylesheet |
| `brain_qwidgets` | The range slider and segmented control |

```python
from PySide6.QtWidgets import QApplication
import brain_gui

app = QApplication([])
win = brain_gui.Brain()
win.show()
app.exec()
```

---

## Speed notes

Enable the kernel cache before importing JAX-using modules:

```python
import brain_cache
brain_cache.enable_jax_cache(verbose=False)

import jax
jax.config.update("jax_enable_x64", True)   # BRAIN needs float64
```

To reuse resampled templates across many fits, wrap the loader:

```python
import io_utils, brainv1, brain_cache

raw, memo = io_utils.load_ssp_templates, {}

def cached(folder, bases, target_wl, norm):
    key = brain_cache.ssp_cache_key(folder, bases, target_wl, norm)
    if key not in memo:
        memo[key] = brain_cache.load_ssp_templates_cached(
            folder, bases, target_wl, norm, raw)
    return memo[key]

io_utils.load_ssp_templates = cached
brainv1.load_ssp_templates = cached
```
