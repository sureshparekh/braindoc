# BRAIN

<p align="center">
  <img src="img/logo.png" alt="BRAIN" width="150">
</p>

**BRAIN** takes a galaxy spectrum and works out what mix of stars produced it —
their ages, their chemical composition, how much dust sits in front of them, and
how fast they are moving. It can also model the glowing gas between the stars,
both the emission lines and the smooth nebular continuum they sit on.

It follows the same physical method as
[FADO](https://www.spectralsynthesis.org/), rewritten in Python on top of
[JAX](https://docs.jax.dev/), and it is fast enough to fit an integral-field
datacube without a cluster.

!!! quote "The one rule that shapes everything else"
    **No additive or multiplicative polynomials are ever applied to the
    spectrum.** The continuum shape comes from the stellar population weights
    and a physical extinction curve, and from nothing else. A polynomial that
    absorbs a mismatch between model and data also absorbs the signal you were
    trying to measure — and it does so silently.

---

## What you get from a fit

- A **star-formation history**: how much light and mass sits in each age and
  metallicity of the template library
- **Dust**: $A_V$ against a choice of twelve extinction curves
- **Kinematics**: systemic velocity and velocity dispersion, for the stars and
  independently for the gas
- **Emission lines**: fluxes, equivalent widths and the Balmer decrement
- **Gas conditions**: electron density and temperature, and a BPT
  classification, measured per spectrum
- **A nebular continuum** consistent with the ionising output of the young
  populations the fit found

---

## Where to start

<div class="grid cards" markdown>

- :material-download: **[Installation](install.md)** — three lines, then check it works
- :material-play: **[Your first fit](quickstart.md)** — a result in about thirty seconds
- :material-monitor: **[The desktop interface](gui.md)** — everything, with a plot
- :material-cog: **[Settings reference](settings.md)** — every option, explained
- :material-function-variant: **[Method](method.md)** — the mathematics
- :material-compare: **[Comparison with FADO](fado.md)** — what matches, what differs

</div>

---

## At a glance

| | |
|---|---|
| **Speed** | ~1.3 CPU-seconds per spectrum in stellar-only mode |
| **Templates** | Any SSP library with a catalogue file; 84 ship with the code |
| **Extinction** | 12 curves — Milky Way, starburst, LMC and SMC |
| **Gas** | Emission lines and nebular continuum, tied to the ionising budget |
| **Hardware** | Runs on a laptop CPU; uses a GPU when one is present |
| **Interface** | A settings file, a Python API, or a desktop application |
| **Output** | Text, in a format compatible with STARLIGHT readers |
