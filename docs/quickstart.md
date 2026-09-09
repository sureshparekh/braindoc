# Your first fit

The repository ships with five example spectra and a template library, and
`brain_setup.yaml` already points at one of them. So the shortest possible
first run is:

```bash
python run_brain.py
```

---

## What happens

```
BRAIN - Direct Pixel Fitting
  Loading examples/spectra/10517-9102_10_19.spec
   Log-rebinned: 3201 pixels, velscale = 58.42 km/s/pix
   Mask: 11 regions, 467/3201 pixels masked (14.6%)
   Fitting 2677/3199 pixels (83.7%)
   84 templates loaded and directly mapped to log grid
  LM optimization from: Av=0.30, sig_star=150.0, v0_star=206.1
   Completed in 4.92s (50 evaluations)
   Av = 0.2089, sigma* = 49.14 km/s, v0* = 186.03 km/s
   chi2/Neff = 0.5878, ADEV = 17.321%
  DONE in 10.5s
```

Most of the first run is JAX compiling the model. That work is cached on disk
and reused by every later run, so the second fit is much faster.

---

## What you get

Two files land in `brain_out/`:

=== "`*_summary.txt`"

    The fitted parameters and the full population table.

    ```
      5.58653E-01                             [chi2/Nl_eff]
         20.45878                             [adev (%)]
        100.00000                             [sum-of-x (%)]
      3.51890E+03                             [Mini_tot (Msun)]
      188.21                                  [v0_min  (km/s)]
       40.70                                  [vd_min  (km/s)]
     0.0747                                   [AV_min  (mag)]

    # j     x_j(%)      Mini_j(%)   age_j(yr)    Z_j     ...
      1   21.0944     4.6185E-05   1.000000E+00 0.00000  ...
    ```

=== "`*_fitted.txt`"

    Seven columns of the fit itself.

    ```
    # Wavelength Flux_Obs Total_Fit Stellar_Fit Emission_Fit Err Resid
    3.541000e+03 6.959377e-01 9.943693e-01 9.943693e-01 0.0e+00 1.23e+00 -2.98e-01
    ```

Both are described in [Understanding the output](output.md).

---

## Fitting your own spectrum

Open `brain_setup.yaml` and change one line:

```yaml
spectrum: path/to/your/spectrum.spec
```

Then check before you commit to a long run:

```bash
python run_brain.py --check
```

This validates every setting, confirms the templates exist, and reports the
wavelength range it will actually use — without starting a fit.

!!! warning "The flag column"
    BRAIN's input format uses **`0` to mark a good pixel**, following
    STARLIGHT and FADO. If your data uses the opposite convention, every pixel
    will be rejected and the log will say `Fitting 0/3199 pixels`. See
    [Input data](input.md).

---

## Three things worth changing early

```yaml
wavelength_min: 3700.0     # trim the noisy ends of your spectrum
wavelength_max: 6900.0

velocity_range: [-2000.0, 5000.0]   # must contain your galaxy's velocity

nebular_mode: "off"        # 'continuum' if the emission lines are strong
```

The velocity range is the one that most often goes wrong. If you know the
redshift $z$, the velocity is roughly $z \times 300\,000$ km/s, and the range
must contain it.

---

## Doing this with the interface instead

Everything above is available as a window, with the spectrum in front of you:

```bash
python brain_gui.py
```

See [The desktop interface](gui.md).
