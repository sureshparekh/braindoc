# Welcome to BRAIN-v1

**BRAIN (Bayesian/Broadening Resolver for Astronomical IFU Networks)** is a native python, open-source pipeline for advanced Stellar Population Synthesis (SPS) and direct pixel-fitting.

`brainv1` incorporates advanced non-linear kinematics solvers, robust continuum geometry mapping via Legendre polynomials, and rigid FADO-style multiplet constraints to rigorously solve physical gas/star decoupling in complex galaxy spectra.

---

## Quick Links

- [Explore the Core Methodology](methodology.md) to unbox the mathematics and the Levenberg-Marquardt driven non-linear architecture behind the fits.
- [View Performance & Results](performance.md) to see how `brainv1` handles complex features like the NGC 1022 composite spectrum.

---

## Quickstart Installation

You can clone the central Github repository and install the minimal required scientific wrapper libraries inside a python 3 environment natively:

```bash
git clone https://github.com/sureshparekh/brainv1.git
cd brainv1
pip install numpy scipy matplotlib
```

## Running Your First Fit
```bash
python brainv1.py
```
This triggers the `SpectralOptimizer` pipeline to load `BC03BasesDir` templates, apply logarithmic pixel-rebinning, and begin the iterative Fourier-space convolution to find the optimal line-of-sight velocity parameters.
