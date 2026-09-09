# Troubleshooting

---

## `Fitting 0/3199 pixels`

**Every pixel was rejected.** Almost always the flag column convention.

BRAIN uses **`0` to mean a good pixel**, following STARLIGHT and FADO. If your
pipeline writes `1` for good pixels, invert column four.

Also check that column three (the error) is positive everywhere — a zero or
negative error rejects the pixel too.

---

## The fit is flat zero above some wavelength

The templates do not reach that far. `BasesGM/` covers **3540–6996 Å**; outside
that every template column is zero, so the model is identically zero.

BRAIN detects this and warns:

```
412 pixels lie outside the template coverage (6996-7400 A) and were dropped.
```

Narrow `wavelength_max`, or use a library that reaches further. The desktop
interface prevents the situation by bounding the range slider.

---

## The velocity is wrong, or the fit looks shifted

`velocity_range` must **contain** the galaxy's actual velocity. If you know the
redshift $z$, it is roughly $z \times 300\,000$ km/s.

A range of `[-2000, 5000]` covers $z \lesssim 0.017$. Beyond that, widen it.

---

## Nearly all populations are zero

That is correct. The solver enforces non-negativity and finds a sparse
solution — typically 10–20 non-zero populations out of 84. Stellar population
fitting is degenerate, and a sparse answer is the honest one.

If you want a smoother history, raise `smoothness`.

---

## `chi2/Nl_eff` is far below 1

Your error bars are probably overestimated. $\chi^2/N \approx 0.5$ means the
model is fitting the data twice as well as the quoted uncertainties suggest is
possible.

This does not affect the fitted parameters, but it does mean that Monte Carlo
error bars derived from those uncertainties will be too large.

---

## `A_V` and the nebular continuum disagree with expectations

If your range starts redward of 3646 Å, the Balmer jump is outside it and the
nebular continuum is nearly degenerate with dust reddening. BRAIN warns:

```
Nebular continuum is weakly constrained: Balmer jump (3646 A) lies outside
the fitted range. It may trade against A_V.
```

Extend the range below 3646 Å if your data allow it. Otherwise treat $A_V$ and
the nebular strength as a joint constraint.

---

## `full` mode silently became `continuum`

By design. The BPT gate found that the gas is not obviously photoionised by
stars:

```
BPT class: undetermined — dropping 'full' to 'continuum'
```

The ionising budget of a stellar population is only a valid constraint if stars
are what ionise the gas. See [Nebular modes](modes.md).

---

## Emission lines vanished from the fit

Check the gas dispersion floor message:

```
sigma_gas lower bound raised 10.0 -> 58.4 km/s (velocity sampling)
```

If you disabled `floor_gas_dispersion_at_pixel_width`, the optimiser can pin
$\sigma_{\rm gas}$ below one pixel. A line narrower than the grid cannot be
represented, and the NNLS drives its amplitude to zero. Leave the floor on.

---

## Every run recompiles

You are changing something that alters array shapes — the wavelength range, the
template selection, or the nebular mode. Fix them across a batch. See
[Performance](performance.md).

Also confirm the cache is enabled and writable:

```python
import brain_cache
brain_cache.enable_jax_cache(verbose=True)
```

---

## Edits to the settings file seem to have no effect

Stale bytecode. BRAIN sets `sys.dont_write_bytecode = True` for this reason,
but if you have imported the modules some other way, clear it:

```bash
find . -name __pycache__ -type d -exec rm -rf {} +
```

---

## The GUI will not start

```
ModuleNotFoundError: No module named 'PySide6'
```

```bash
pip install PySide6
```

On a headless machine there is no display to open a window on. Use
`run_brain.py` instead, or forward X11.

---

## Fonts look wrong in the GUI

BRAIN uses Qt precisely because Tk on many Linux builds cannot reach the
system's TrueType fonts at all. If faces still look wrong, check what Qt
resolved:

```python
from PySide6.QtWidgets import QApplication
app = QApplication([])
import brain_theme
print(brain_theme.font_report())
```

It falls back gracefully through a preference list, so a missing font is
cosmetic, never fatal.

---

## Timings are much worse than documented

Check the machine load. On a shared server, competing jobs inflate every
measurement several-fold. `benchmark.py` samples the load first and tells you
when the numbers cannot be trusted.

---

## Still stuck

Run the validator, which reports every inconsistency at once:

```bash
python run_brain.py --check
```

Then open an issue at
[github.com/sureshparekh/brainv1/issues](https://github.com/sureshparekh/brainv1/issues)
with that output and the log of the failing run.
