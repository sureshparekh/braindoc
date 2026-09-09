# Input data

## Spectrum files

A plain text file with four columns:

```
# wavelength   flux        error       flag
3541.0000      0.695938    1.229688    0
3541.6980      0.712344    1.221907    0
3542.3963      0.698112    1.230114    1
```

| Column | Meaning |
|---|---|
| 1 | Wavelength in **Ångström**, in the observed frame |
| 2 | Flux, in any consistent unit |
| 3 | Flux uncertainty, same unit. Must be positive for a pixel to be used |
| 4 | Quality flag — **`0` means the pixel is good** |

Lines beginning with `#` are ignored.

!!! danger "The flag convention catches everyone once"
    `0` = **use this pixel**. Any non-zero value rejects it.

    This is the STARLIGHT convention. If your pipeline writes `1` for good
    pixels, invert the column first, or every pixel will be thrown away and
    the log will read `Fitting 0/3199 pixels`.

Columns three and four are optional. Without errors, BRAIN weights every pixel
equally and you should set `has_errorbars: false`. Without flags, every pixel
is treated as good.

---

## Template libraries

A template library is a folder containing spectra and a `CATALOGUE.txt` that
describes them:

```
# AGE_YR      Z        FILENAME                   SHORT_NAME     MSTARS  KIND
1.000000e+06  0.00370  Mun1.30Zm0.71T00.0001.K    ageGe_00_z004  1.0000  ssp
5.620000e+06  0.00370  Mun1.30Zm0.71T00.0056.K    age04_z004     0.9431  ssp
1.000000e+00  0.00000  PowerOpt_150.dat           Power_150      1.0000  powerlaw
```

| Column | Meaning |
|---|---|
| `AGE_YR` | Population age in years |
| `Z` | Metallicity as a mass fraction (0.019 is solar) |
| `FILENAME` | The spectrum file, relative to the catalogue |
| `SHORT_NAME` | A label used in the output table |
| `MSTARS` | Surviving stellar mass fraction at that age |
| `KIND` | `ssp` or `powerlaw` |

Each referenced file is two columns: wavelength and flux.

To see what is available:

```bash
python run_brain.py --templates
```

### The library that ships with BRAIN

`BasesGM/` holds 84 simple stellar populations — 21 ages from 1 Myr to 12.6 Gyr
across 4 metallicities — plus one power-law component for AGN continuum.

**It covers 3540–6996 Å.** Outside that range every template is zero, so the
model there is identically zero. BRAIN detects this, drops those pixels, and
warns you:

```
   412 pixels lie outside the template coverage (6996-7400 A) and were
   dropped. Narrow the fitting range or use a base library that reaches
   further.
```

The desktop interface prevents the situation entirely by bounding the range
slider to the intersection of your data and the templates.

### Using your own library

Point `base_folder` at any directory with a valid `CATALOGUE.txt`. BRAIN
resamples the templates onto your spectrum's grid at load time, so they do not
need to share a wavelength sampling with your data.

---

## Masks

An optional text file listing regions to exclude or emphasise:

```
# start     end       weight
3710.00     3744.00   0.00
5150.00     5250.00   2.00
```

The weight is optional and defaults to `0`, which keeps two-column mask files
from older tools working unchanged. See [Masks and weights](masks.md).

---

## Datacubes

BRAIN reads FITS datacubes for spaxel-by-spaxel fitting through
`fit_datacube.py`. See [Batch and datacubes](batch.md).
