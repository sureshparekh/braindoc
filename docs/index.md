# BRAIN-v1: Technical Documentation & Mathematical Model

This document serves as a comprehensive reference for **BRAIN-v1**, detailing the mathematical framework, architectural design, and instructions for configuration and extension.

---

## 1. Mathematical Framework & Model Equations

BRAIN-v1 employs a **Direct Pixel-Fitting (DPF)** methodology. The observed spectrum is modeled as a linear combination of physical templates—both stellar (SSPs) and gaseous (emission lines)—which are nonlinearly perturbed by kinematics and dust.

### The Core Objective Function

We seek to minimize the $\chi^2$ statistic between the observed flux $F_{obs}$ and the model flux $F_{model}$:

$$ \chi^2 = \sum_{\lambda} \left[ \frac{F_{obs}(\lambda) - F_{model}(\lambda)}{\sigma_{obs}(\lambda)} \right]^2 + \lambda_{reg} || \mathbf{D} \mathbf{w}_\star ||^2 $$

Where $F_{model}$ is defined as:

$$ F_{model}(\lambda) = \left[ \sum_{j} w_{\star, j} \ M_{\star, j}(\lambda, \sigma_\star, v_{0\star}) + \sum_{k} w_{gas, k} \ M_{gas, k}(\lambda, \sigma_{gas}, v_{0gas}) \right] \times 10^{-0.4 A_V [k(\lambda) - k(\lambda_{norm})]} $$

Notice that **no multiplicative ($P_m$) or additive ($P_a$) polynomials** are present in this equation. The continuum shape is dictated strictly by the SSP weights $w_{\star, j}$ and the physical dust extinction curve $k(\lambda)$.

### Variable Breakdown

1. **Stellar Templates ($M_{\star, j}$):**
   The base SSP spectra are broadened and Doppler-shifted. To do this efficiently, the spectrum is log-rebinned ($d\ln\lambda = \text{const}$) mapping velocity to uniform pixel shifts. The broadening is applied in Fourier space via the Convolution Theorem:
   
   $$ M_{\star, j}(\lambda, \sigma_\star, v_{0\star}) = \mathcal{F}^{-1} \left\{ \mathcal{F}\{ S_j \} \cdot \exp\left( -\frac{1}{2}(\omega \sigma_\star)^2 - i \omega v_{0\star} \right) \right\} $$
   
   *Where $S_j$ is the resting SSP template.*

2. **Gas Emission Templates ($M_{gas, k}$):**
   Modeled as discrete Gaussian profiles normalized to unit area. For a line with rest wavelength $\lambda_{rest}$:
   
   $$ M_{gas}(\lambda) = \frac{1}{\sqrt{2\pi}\sigma_\lambda} \exp\left( -\frac{(\lambda - \lambda_{obs})^2}{2\sigma_\lambda^2} \right) $$
   *(where $\lambda_{obs} = \lambda_{rest}(1 + v_{0gas}/c)$ and $\sigma_\lambda = (\sigma_{gas}/c)\lambda_{obs}$)*
   
   For **tied doublets** (e.g., [O III] $\lambda\lambda 4959, 5007$), the components are locked into a single template column using their quantum mechanical ratios (e.g., 1:3).

3. **Dust Extinction:**
   Handled by the scalar $A_V$ applied to an empirical curve $k(\lambda)$ from the literature (CCM, Calzetti, Gordon, etc.), normalized at a user-defined $\lambda_{norm}$.

4. **Tikhonov Regularization ($|| \mathbf{D} \mathbf{w}_\star ||^2$):**
   To prevent catastrophic fragmentation (unrealistic rapid variations in age/metallicity), a penalty matrix $\mathbf{D}$ is applied to the stellar weights. $\mathbf{D}$ acts as a finite-difference operator (1st or 2nd order) penalizing differences between adjacent SSPs. 

---

## 2. Code Architecture

BRAIN-v1 is modularized to cleanly decouple physics, optimization, linear algebra, and configuration.

| Module | Purpose / Functionality |
|--------|-------------------------|
| `brainv1.py` | The main driver script. Orchestrates loading files, building the optimizer, and writing outputs. |
| `spectral_engine.py` | Performs the core mathematical operations: `log_rebin`, batched Fourier space broadening (`fourier_broaden_matrix`), and `dust_vector` formulations. Designed for matrix forms to allow easy GPU porting later. |
| `optimizer.py` | Handles the nonlinear evaluation. Defines `SpectralFitter` which runs a coarse Grid-Search to find the kinematic basin, and hands it off to `scipy.least_squares` (Trust Region Reflective algorithm) to find the minimum for the 5 nonlinear parameters. |
| `solver.py` | The linear sub-problem solver (`solve_nnls_regularized`). At every nonlinear step, this rapidly solves for the optimal $N$-dimensional linear weights $w_i > 0$ given the current trial kinematics and dust using Bounded-Variable Least Squares. |
| `reddening_laws.py` | Comprehensive library of parametric dust curves from the literature. |
| `emission_lines.py` | Contains dictionaries of Optical/NIR rest-wavelengths, handles doublet ratios, and dynamically generates the Gaussian $M_{gas}$ design matrix based on the observed data's wavelength coverage. |
| `errors.py` | Applies Monte Carlo bootstrap resampling via residual shuffling or flux perturbation to compute standard deviations/errors on the optimized weights. |
| `config.py` | The central `@dataclass` for all user-adjustable parameters (input paths, lambda ranges, regularization strength). |

---

## 3. Usage & Customization Guide

### Altering the Configuration
If someone needs to adapt BRAIN-v1 for their dataset, they should look at the end of `brainv1.py` under the `if __name__ == "__main__":` block. 

A standard run requires initializing the `NewBrainConfig` object.

```python
cfg = NewBrainConfig(
    obs_spectrum_file="my_galaxy.txt",
    ssp_folder="../SSPs/BC03/",
    reddening_law="CCM",
    norm_wavelength=5500.0,
    has_errorbars=False,    # true if file has 3 cols (wave, flux, err)
    reg_strength=1.0,       # The λ parameter for Tikhonov
    n_mc_resamples=100      # Reduce for quicker tests, increase for pub-quality errors
)
run(cfg)
```

### Adding New Emission Lines
To include a new emission line (or tie a new doublet), edit `emission_lines.py`. 
Add your line to `EMISSION_LINES_OPTICAL` or `EMISSION_LINES_NIR` in the format:
```python
'He II_4686': 4686.0
```
If it's a doublet that must logically scale together, add it to `TIED_DOUBLETS`:
```python
'[O III]_Doublet': [(4959.0, 0.33), (5007.0, 1.0)]
```
BRAIN-v1 automatically detects which lines fall inside your spectrum's wavelength range and generates the matrix columns for you.

### Adding New Dust Laws
To introduce a new empirical extinction curve, open `reddening_laws.py` and define a new function (e.g., `def k_mylaw(wave):`). Then register it inside the `get_k_lambda` dispatcher function string comparison logic.

### Modifying Bounds
If fitting data with wildly different kinematics (e.g., cluster centers vs isolated dwarfs), modify `sigma_star_bounds`, `v0_star_bounds`, etc. inside `NewBrainConfig` to widen or tighten the Levenberg-Marquardt boundaries. The `v0_grid_step` dictates how fine the initial parameter-space scan is.
