# Understanding the output

Every fit writes two text files into the output folder.

---

## The summary file

`*_summary.txt` is laid out in a format STARLIGHT readers can parse: a value,
then the key in square brackets.

### Fit quality

```
  5.58653E-01                             [chi2/Nl_eff]
     20.45878                             [adev (%)]
```

| Key | Meaning |
|---|---|
| `chi2/Nl_eff` | $\chi^2$ per effective degree of freedom. Near 1 is a good fit; well below 1 usually means the errors are overestimated |
| `adev` | Mean absolute deviation between model and data, as a percentage |

### Totals

```
    100.00000                             [sum-of-x (%)]
  7.03171E-02                             [Flux_tot]
  3.51890E+03                             [Mini_tot (Msun)]
  2.46611E+03                             [Mcor_tot (Msun)]
```

| Key | Meaning |
|---|---|
| `sum-of-x` | Light fractions, summing to 100% by construction |
| `Flux_tot` | Total model flux at the normalisation wavelength |
| `Mini_tot` | Total mass **initially formed** |
| `Mcor_tot` | Mass **still in stars** today, after mass loss |

`Mcor_tot` is always the smaller of the two. Use it when comparing against a
dynamical mass; use `Mini_tot` when comparing against an integrated
star-formation history.

### Parameters

```
  188.21                                  [v0_min  (km/s)]
   40.70                                  [vd_min  (km/s)]
 0.0747                                   [AV_min  (mag)]
 0.0000                                   [YAV_min (mag)]
```

| Key | Meaning |
|---|---|
| `v0_min` | Systemic velocity of the stars |
| `vd_min` | Stellar velocity dispersion $\sigma_\star$ |
| `AV_min` | Extinction in magnitudes, against the chosen law |
| `YAV_min` | Extra extinction applied to the youngest populations only |

### The population table

One row per template:

```
# j    x_j(%)    Mini_j(%)   Mcor_j(%)   age_j(yr)     Z_j     (L/M)_j  YAV?  Mstars  component_j
  1   21.0944   4.6185E-05  6.5901E-05  1.000000E+00  0.00000  9.787E+00  0   1.0000  Power_150
  2    0.0000   0.0000E+00  0.0000E+00  1.000000E+06  0.00370  3.171E-03  0   1.0000  ageGe_00_z004
```

| Column | Meaning |
|---|---|
| `x_j` | **Light** fraction at the normalisation wavelength, in per cent |
| `Mini_j` | **Initial mass** fraction |
| `Mcor_j` | **Surviving mass** fraction |
| `age_j`, `Z_j` | Age in years and metallicity |
| `(L/M)_j` | Light-to-mass ratio for that population |
| `Mstars` | Surviving stellar mass fraction at that age |

!!! warning "Light fractions are not mass fractions"
    A 1 Myr population can carry 20% of the light and a millionth of the mass.
    Young stars are enormously more luminous per unit mass. Always be explicit
    about which fraction you are quoting.

Most rows will be exactly zero. That is expected and correct: the solver
enforces non-negativity and finds a sparse solution, typically 10–20 non-zero
populations out of 84. It is not a failure to converge.

### Reading it in Python

```python
import numpy as np

def read_summary(path):
    scalars, rows = {}, []
    in_table = False
    for line in open(path):
        if line.startswith("# j"):
            in_table = True
            continue
        if in_table:
            parts = line.split()
            if not parts or not parts[0].isdigit():
                break                    # stop at the first non-data row
            rows.append(parts)
        elif "[" in line and "]" in line:
            key = line.split("[")[1].split("]")[0].split("(")[0].strip()
            scalars[key] = line.split("[")[0].strip()
    return scalars, rows

vals, table = read_summary("brain_out/mygalaxy_summary.txt")
print(float(vals["AV_min"]), float(vals["chi2/Nl_eff"]))

age = np.array([float(r[4]) for r in table])
light = np.array([float(r[1]) for r in table])
print("light-weighted log age:",
      np.sum(light * np.log10(age)) / np.sum(light))
```

!!! note
    Stop at the first non-numeric row. In `continuum` and `full` mode extra
    sections follow the population table, and a naive "read every numeric line"
    loop will swallow them.

---

## The fitted spectrum

`*_fitted.txt` has seven columns on the log-rebinned grid the fit actually used:

```
# Wavelength Flux_Obs Total_Fit Stellar_Fit Emission_Fit Err Resid
3.541000e+03 6.959377e-01 9.943693e-01 9.943693e-01 0.000000e+00 1.229688e+00 -2.984316e-01
```

| Column | Meaning |
|---|---|
| `Wavelength` | Ångström, observed frame |
| `Flux_Obs` | The observation, normalised |
| `Total_Fit` | The complete model |
| `Stellar_Fit` | Stellar component alone |
| `Emission_Fit` | Emission lines alone — zero in `off` mode |
| `Err` | Uncertainty used in the fit |
| `Resid` | `Flux_Obs − Total_Fit` |

```python
import numpy as np
import matplotlib.pyplot as plt

wl, obs, tot, star, emis, err, res = np.loadtxt(
    "brain_out/mygalaxy_fitted.txt", unpack=True)

fig, (a, b) = plt.subplots(2, sharex=True, height_ratios=[3, 1])
a.plot(wl, obs, lw=0.6, color="0.6", label="observed")
a.plot(wl, tot, lw=1.2, label="fit")
a.legend()
b.plot(wl, res, lw=0.6)
b.axhline(0)
plt.show()
```

---

## Gas diagnostics

In `continuum` and `full` mode the summary carries extra measurements:

| Quantity | From |
|---|---|
| Electron density $n_e$ | [S II] λ6716/λ6731 ratio |
| Electron temperature $T_e$ | [O III] λ4363/λ5007 ratio |
| Balmer decrement | Hα/Hβ |
| $A_V$ of the gas | The Balmer decrement against Case B |
| BPT classification | Star-forming, composite, AGN or undetermined |

Line fluxes and equivalent widths for every fitted line are listed underneath.
