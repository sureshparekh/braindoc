# BRAIN-v1 Methodology

The **BRAIN** pipeline uses a sophisticated hybrid approach to perform direct pixel-fitting on integral field unit (IFU) or long-slit optical/NIR galaxy spectra. It mathematically disentangles the stellar absorption features (which encode the star formation history) from the nebular emission lines (which encode the current gas properties).

---

## 1. Mathematical Foundation: Penalized Pixel-Fitting (P3F)

The underlying model matches the observed spectrum $O_\lambda$ with a synthetic spectrum $M_\lambda$, which is a sum of line-of-sight velocity dispersed (LOSVD) stellar populations ($T_{\star, \lambda}$), nebular emission templates ($E_{\lambda}$), scaled by a multiplicative polynomial and damped by uniform dust extinction.

$$ M_\lambda = P_{\text{legendre}}(\lambda) \times 10^{-0.4 \cdot A_v \cdot [k(\lambda)-k(\lambda_V)]} \times \left( \sum_{j} w_{\star, j} \Big( T_{\star, j}(\lambda) \ast \mathcal{L}(v_\star, \sigma_\star) \Big) + \sum_{k} w_{g, k} E_{k}(\lambda, v_{gas}, \sigma_{gas}) \right) $$

To evaluate this accurately, the solver requires resolving both high-frequency localized physical conditions (stellar vs gas velocities) and low-frequency distortions (like flux calibration errors).

---

## 2. Core Architectural Components

### Levenberg-Marquardt Optimizer
Early versions of `brainv1` employed a monolithic Markov Chain Monte Carlo (MCMC) sampler. However, solving for kinematics inside an MCMC traversing thousands of parameter combinations was computationally prohibitive and struggled with local minima. 

In the finalized architecture, the non-linear subspace — $A_v, \sigma_\star, v_{0,\star}, \sigma_{gas}, v_{0,gas}$, and the Legendre polynomial coefficients — are driven by a **Levenberg-Marquardt (LM) algorithm** (`scipy.optimize.least_squares`). The LM algorithm iteratively computes the Jacobian and navigates down the $\chi^2$ valley exponentially faster than random-walk implementations, allowing a simultaneous fit of continuum, stars, and gas within seconds.

A coarse grid sweep over $v_0$ is executed before LM initialization to guarantee placing the optimizer inside the global kinematic minimum basin, avoiding "offset trapping."

### Tied Emission Line Doublets (FADO paradigm)
Emission lines cannot be fitted as independent blind Gaussians without physics violation. Because quantum mechanics rigidly defines the relative populations of atomic energy levels, certain line ratios are naturally fixed.

`brainv1` generates emission line templates as strict multi-component templates instead of solitary lines:

- **Collisionally Excited Doublets:** Features like `[O III]` 4959/5007 and `[N II]` 6548/6584 are generated as single arrays locked to their theoretical `1:3` ratio. This restricts the Non-Negative Least Squares (NNLS) solver from inventing unphysical emission ratios to simply fit raw noise in the spectrum.
- **Balmer Decrement Calibration:** `H_alpha`, `H_beta`, `H_gamma`, and `H_delta` are grouped into a single `Balmer_Series` base template. To preserve proper Case B recombination physics under a variety of dust environments, intrinsic ratios (~2.86 for $H\alpha/H\beta$) are enforced, with only the free $A_v$ non-linear parameter permitted to skew their relative heights.

### Multiplicative Legendre Polynomials
To account for varying dust configurations, flux calibration mismatches between observation setups, and spectral shape discrepancies in models, the optimizer applies a **Multiplicative Legendre Polynomial** (currently set up to degree 12).  

The polynomial spans $P \in [-1, 1]$ mapped across the rest-frame wavelength axis. The non-linear subset array continuously evaluates these bounds to warp the synthetic spectrum up/down without sacrificing the high-frequency absorption physics. 

---

## 3. The `NNLS` Linear Phase

Once the LM optimizer passes down a specific non-linear state, the template library is convolved, scaled, and compiled into a single unified 2D matrix $\mathbf{A}$.

1. Matrix columns $0 \rightarrow N_\star$ contain the heavily broadened and shifted Simple Stellar Populations (SSPs).
2. Matrix columns $N_\star \rightarrow N_{gas}$ contain the emission templates.

We solve $\mathbf{A} \vec{x} = \vec{b}$ using **Non-Negative Least Squares (NNLS)**, enforcing the physical constraint that you cannot have a negative fraction of stars or gas.

**Regularization / Smoothing**
A second-order derivative difference operator $\mathbf{D}$ matrix is stacked below the primary NNLS matrix, controlled by a scalar $\lambda$ (`REGULARIZATION_STRENGTH`). This physically enforces the expectation that Star Formation Histories (SFHs) are generally smooth; avoiding wild 100% burst oscillations between adjacent 5 Myr and 10 Myr bins caused by tiny noise fluctuations.
