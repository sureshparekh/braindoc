"""
A BRAIN run: spectra.

Written by brainsp 2.0.0 on 2026-10-14 19:27. Every setting of the run is in this
file; edit it here and run it again:

    python run.py                  run it
    python run.py --check          check everything, fit nothing
    python run.py --device gpu     choose the processor: auto, cpu or gpu
    python run.py more/*.spec       fit these files instead

Each setting is documented where it is set. The same text, and more, is in
the BRAIN documentation (Settings reference), and in Python:
    import brainsp; print(brainsp.Settings.describe("dust_range"))
"""

import os
import sys

import brainsp

HERE = os.path.dirname(os.path.abspath(__file__))


def here(path):
    """A path written relative to this file's folder, made usable from any
    working directory. Absolute paths are left as they are."""
    return path if os.path.isabs(path) else os.path.join(HERE, path)

SETTINGS = brainsp.Settings(

    # ======================================================================
    # 1. WHAT TO FIT
    # ======================================================================

    # Optional list of wavelength regions to treat specially — sky lines, bad
    # columns, or features you want the fit to try harder on. One region per line:
    #
    #       start_wavelength   end_wavelength   [weight]
    #
    # The weight is optional and defaults to 0, meaning the region is thrown away.
    # A weight above 1 makes those pixels count for more; 2 counts them double.
    # A .sm / .gm mask file works as it is: its first line is the number of
    # regions N, and only the N lines after it are read; anything below them is
    # treated as notes.
    # For a datacube the same mask is applied to every spaxel.
    # Leave blank for no mask. The desktop interface can draw one for you.
    mask=None,

    # ======================================================================
    # 2. WAVELENGTH RANGE
    # ======================================================================

    # Fit only between these wavelengths, in Angstroms. Trim the noisy ends of
    # your spectrum here. Leave blank to use everything.
    #
    # Changing this changes the size of the problem, so BRAIN rebuilds its
    # compiled engine once (a few seconds). Keeping one range across a batch
    # keeps every run fast.
    wavelength_min=3700.0,
    wavelength_max=6900.0,

    # ======================================================================
    # 2b. INSTRUMENTAL RESOLUTION
    # ======================================================================

    # Your spectrograph smears every spectral line by a fixed amount, and so does
    # whatever machine produced the template library. Those two smearings are
    # almost never equal, and the difference goes straight onto the velocity
    # dispersion BRAIN reports. Tell BRAIN about them and it corrects for the
    # difference and reports a stellar dispersion. Leave them blank and BRAIN
    # still fits, but the dispersion it reports is an OBSERVED one that includes
    # the instrument.
    #
    # BRAIN will never smooth your spectrum to make the two match. Smoothing
    # correlates neighbouring noise values, and every chi-squared in this code
    # assumes they are independent, so a smoothed spectrum produces a better
    # looking fit that means nothing.
    #
    # Your data's resolution, in the OBSERVED frame, written any of these ways:
    #     instrumental_resolution: 2.9             a FWHM in Angstrom
    #     instrumental_resolution: "70 km/s"       constant in velocity (a sigma)
    #     instrumental_resolution: lsf_10517.txt   two columns: wavelength, FWHM
    # Leave blank if you do not know it.
    #
    # If your data came from the MaNGA DRP, you do not have to model this: the
    # cube ships the line-spread function per spaxel, as a 1-sigma width in
    # Angstrom. DR17 names the extensions LSFPRE and LSFPOST; in DR15 and DR16 the
    # same two were called PREDISP and DISP. Take the pre-pixelised one, LSFPRE:
    # it is the width before integration over the pixel, which is the convention
    # that matches this kind of fitting. Carrying that array through from wherever
    # you extracted the spectrum is always better than a single number here.
    instrumental_resolution=None,

    # The template library's resolution, at rest wavelengths. Leave blank and
    # BRAIN reads it from the template files' own headers; if they do not state
    # one, BRAIN says so and applies no correction rather than guessing.
    #     library_resolution: 3.4            a FWHM in Angstrom
    #     library_resolution: "45 km/s"      constant in velocity (a sigma)
    library_resolution=None,

    # The redshift that was removed from your spectrum before you handed it to
    # BRAIN. This matters: the instrument smeared the light at the wavelength it
    # was observed at, lambda_rest * (1 + z), while the library is smeared at the
    # rest wavelength. Leave it 0.0 if your spectrum is still in the observed
    # frame.
    spectrum_redshift=0.0,

    # Is the spectrum already in the rest frame?
    #   true  : you de-redshifted it; spectrum_redshift records what you removed.
    #   false : it is still in the OBSERVED frame; BRAIN removes spectrum_redshift
    #           itself before fitting, by dividing the wavelengths by 1 + z, the
    #           way it does for a datacube.
    spectrum_in_rest_frame=True,

    # Galactic (Milky Way) reddening, removed BEFORE fitting, single spectra only.
    # This is the foreground dust between us and the galaxy, so it is undone at
    # the OBSERVED wavelengths: flux and errors are multiplied by 10^(0.4 A_lambda)
    # with A_lambda = R_V E(B-V) q(lambda). The galaxy's OWN dust is not touched:
    # it is a fitted parameter (A_V). E(B-V) for a sky position: e.g. the
    # Schlafly & Finkbeiner (2011) maps. For a datacube, use the dereddening stage
    # (or the 'ebv' column of a targets table) instead.
    galactic_ebv=0.0,
    galactic_rv=3.1,
    galactic_law='CCM',

    # The redshift BRAIN should REMOVE from a datacube before fitting it.
    # This is the opposite of the setting above, and it applies to datacubes only.
    #
    #   A SPECTRUM you hand BRAIN is expected to be in the rest frame already:
    #   you de-redshifted it, and 'spectrum_redshift' records what you removed.
    #
    #   A DATACUBE arrives from the telescope in the OBSERVED frame, so BRAIN
    #   de-redshifts it for you. Put the galaxy's redshift here and BRAIN divides
    #   the wavelength axis by 1+z before it does anything else.
    #
    # Leave it 0.0 for a cube that is already in the rest frame. Setting this and
    # 'spectrum_redshift' both is refused, because it describes a cube that gets
    # de-redshifted twice.
    #
    # MaNGA cubes do not carry the galaxy redshift anywhere in the file; it lives
    # in the DRPall catalogue. You have to supply it.
    #
    # The value used is written into the output as BRAINZ, so a finished cube
    # says which frame it was fitted in.
    cube_redshift=0.0,

    # ======================================================================
    # 3. STELLAR TEMPLATES — which populations BRAIN may find
    # ======================================================================

    # BRAIN describes your galaxy as a mixture of simple stellar populations, each
    # with one age and one metallicity. You choose which are on the menu.
    #
    # The library ships a catalogue of everything available:
    #       brainsp/data/libraries/BasesGM/CATALOGUE.txt
    # or run:
    #       brainsp libraries info BasesGM
    #
    # Copy the exact values from there. Asking for one that does not exist is an
    # error, and BRAIN will tell you the nearest ones available.
    base_folder='BasesGM',

    # Ages in YEARS, or the word  all  for every age in the catalogue.
    #   all  is the safe choice. A shorter list fits faster and is less
    #   degenerate, but describes a coarser star-formation history. If you do
    #   shorten it, spread the ages out rather than clustering them.
    #
    # Example of a compact 6-age set spanning 1 Myr to 12.6 Gyr:
    #   ages: [1e6, 1e7, 1e8, 1e9, 5.01e9, 1.26e10]
    ages=[10000000.0, 100000000.0, 1000000000.0, 5010000000.0, 12600000000.0],   # default: 'all'

    # Metallicities (mass fraction of elements heavier than helium).
    # 0.0190 is solar. Use  all  for every one in the catalogue.
    #   metallicities: [0.0076, 0.0190]
    metallicities='all',

    # Add a featureless power-law component? This soaks up light from an active
    # galactic nucleus. Leave false for normal galaxies — switching it on when
    # there is no AGN lets it absorb light that belongs to real stars.
    include_power_law=False,

    # ======================================================================
    # 4. DUST
    # ======================================================================

    # How dust dims and reddens the light of the stars. Pick the curve that
    # matches the dust you think you are looking through, not the newest paper.
    #
    #   Milky Way
    #     CCM   Cardelli, Clayton & Mathis (1989), R_V = 3.1.  Good default.
    #     HZ1   Allen (1976).
    #     HZ2   Seaton (1979), fit by Fitzpatrick (1986).
    #
    #   Starburst
    #     CAL   Calzetti et al. (2000), R_V = 4.05.
    #     CCC   Calzetti (2000) with a Leitherer (2002) far-UV extension.
    #     HZ5   Calzetti (2000), starburst (SB) form. Same curve as CAL.
    #
    #   Large Magellanic Cloud
    #     HZ3   Fitzpatrick (1986).
    #     GD3   Gordon et al. (2003), LMC average.
    #     GD2   Gordon et al. (2003), LMC2 supershell near 30 Doradus.
    #
    #   Small Magellanic Cloud
    #     HZ4   Prevot (1984) & Bouchet (1985).
    #     GD1   Gordon et al. (2003), SMC bar. Steep UV, no 2175 A bump.
    #     GD24  Gordon et al. (2024).
    #
    # The Magellanic curves differ from the Milky Way ones mostly in the
    # ultraviolet, so for a purely optical fit the choice matters far less than
    # it looks. It matters a great deal if your range reaches below ~3000 A.
    reddening_law='CCM',

    # How much dust BRAIN may find, in magnitudes of V-band extinction.
    # [-1, 5] spans a dust-free galaxy to a heavily obscured one, and lets A_V go
    # a little negative. A negative A_V compensates for extinction that is not
    # otherwise corrected: light that reaches us through the galaxy itself (from
    # its far side, say) has crossed its dust, and correcting for that depends on
    # a model of the geometry that no two groups make the same way, so it is
    # common practice to allow A_V down to -1. Use [0, 5] to forbid it.
    dust_range=[0.0, 3.0],   # default: [-1.0, 5.0]

    # Extra dust allowed in front of the YOUNGEST populations only — young stars
    # sit in their birth clouds and are often dustier. Use [0.0, 0.0] to disable.
    young_extra_dust_range=[0.0, 5.0],

    # ======================================================================
    # 5. MOTION OF THE STARS
    # ======================================================================

    # Velocity in km/s; positive means receding. This range must contain your
    # galaxy's actual velocity. If you know the redshift z, velocity is roughly
    # z * 300000 km/s.
    velocity_range=[-2000.0, 5000.0],

    # Velocity dispersion in km/s — how much the stars' individual motions blur
    # the spectral lines. Typical galaxies sit between 50 and 300.
    dispersion_range=[10.0, 500.0],

    # ======================================================================
    # 6. GAS EMISSION LINES
    # ======================================================================

    # Fit the bright lines from glowing gas (H-alpha, [O III], ...)?
    # Only has an effect when nebular_mode is 'espop' or 'nespop'.
    # With nebular_mode 'spop' the fit is purely stellar and the lines stay
    # masked. Setting this false under 'espop' is rejected: espop with no
    # lines is spop.
    fit_emission_lines=True,

    # ======================================================================
    # 2b. INSTRUMENTAL RESOLUTION
    # ======================================================================

    # The wavelength scale YOUR SPECTRUM is on: 'air' or 'vacuum'.
    #
    # This is a property of your data, not of your galaxy, and it is not about
    # the template library — BRAIN puts the emission-line rest wavelengths on the
    # scale you declare here and leaves the library's own scale alone.
    #
    #   vacuum   SDSS, MaNGA, DESI, LAMOST.
    #   air      MUSE (its cube header says CTYPE3 = 'AWAV'), CALIFA.
    #
    # BRAIN REFUSES TO GUESS, and only asks when the answer can change a number:
    # it is required when 'fit_emission_lines' is true and 'nebular_mode' fits
    # lines, and it is ignored in 'spop', which builds no lines at all.
    #
    # The reason it is refused rather than defaulted is that a wrong answer here
    # is invisible. Air and vacuum wavelengths differ by about 83 km/s across the
    # optical — 85.2 km/s at [O II] 3726, 82.7 at [S II] 6731 — and the offset is
    # very nearly constant in velocity, so it is absorbed almost entirely by the
    # fitted gas velocity. chi2 moves by less than 0.05%, with a sign that
    # depends on the spectrum. The fit converges, the line fluxes look ordinary,
    # and the only symptom is a gas-to-stars velocity offset that is not real.
    #
    # The shipped example spectrum is MaNGA-derived, so it is VACUUM. That is not
    # an assumption: Law et al. 2016, AJ 152, 83, Section 3.1 and the Appendix B
    # datamodel both state that the DRP delivers wavelengths in the vacuum
    # heliocentric frame.
    wavelength_scale='vacuum',   # default: None

    # ======================================================================
    # 6. GAS EMISSION LINES
    # ======================================================================

    # The gas often moves slightly differently from the stars, so it gets its own
    # velocity and dispersion.
    gas_velocity_range=[-2000.0, 5000.0],

    # Nothing raises that lower end behind your back. It used to be pushed up to
    # your spectrum's pixel width, back when a line narrower than a pixel was
    # drawn by sampling a Gaussian at pixel centres and most of its flux went
    # missing; the line is now integrated over the pixel and is exact at any
    # width. 1.0 km/s is below the thermal width of every ion in the catalogue at
    # 10000 K, so a dispersion that lands there is a bound and BRAIN reports it as
    # one rather than printing a number you could mistake for a measurement.
    gas_dispersion_range=[1.0, 500.0],

    # ======================================================================
    # 7. NEBULAR PHYSICS   (advanced — "spop" is a perfectly good choice)
    # ======================================================================

    # Young stars emit ultraviolet light that ionises nearby gas, which glows back.
    #
    #   spop       Purely stellar populations. The emission lines are left masked
    #              and are not fitted at all.
    #              Fastest, and correct unless you specifically need the gas.
    #              THIS IS THE DEFAULT.
    #
    #   espop      Emission lines and stellar populations together. Every line is
    #              fitted from its rest position with a free amplitude; nothing
    #              is predicted, so no ionising photon budget is needed and this
    #              mode works with ANY template library. Lines can have several
    #              Gaussian components (line_components, below) in espop only.
    #              What it does NOT do: there is no nebular continuum. Real gas
    #              also emits a smooth free-free, free-bound and two-photon
    #              continuum, and in this mode that light has nowhere to go, so
    #              it is absorbed into the stellar populations and the
    #              extinction. If your spectrum has strong lines and your
    #              library reaches the Lyman limit, use nespop.
    #
    #   nespop     FADO's FC mode (formerly photopop). The emission lines are
    #              measured as in espop; then the stars are fitted with the
    #              nebular continuum of the gas each population's own ionising
    #              photons keep ionised (Case B, at each spectrum's measured T_e
    #              and n_e), on the pixels free of lines, with H-alpha and H-beta
    #              tied to the measured fluxes: the Case B lines of those photons
    #              must be the ones observed. A_V^neb comes from the Balmer
    #              decrement. Where FADO would not apply FC (above the Kewley
    #              line, H-alpha or H-beta under S/N 3, an unphysical [S II]
    #              ratio) the nebular continuum is still the populations' own
    #              but nothing ties the lines (FADO's NC); NEBMAPS MODE and the
    #              summary say which. Needs a template library whose spectra
    #              reach below the Lyman limit at 911.76 A; run
    #              brainsp libraries info <library> to see what yours supports.
    #              (nepop and photopop are no longer modes: use nespop.)
    nebular_mode='espop',   # default: 'spop'

    # Gas conditions. Used only when nebular_mode is nespop. With
    # measure_gas_conditions on, each spectrum's T_e and n_e are measured from
    # its own lines ([O III] 4363 / 5007 and [S II] 6716 / 6731, each at S/N 3
    # or more) as FADO does, and these values are used where the lines cannot
    # give them.
    # Kelvin
    gas_temperature=10000.0,

    # electrons per cubic cm
    gas_density=100.0,
    measure_gas_conditions=True,

    # 0.02 is solar
    gas_metallicity=0.02,

    # ======================================================================
    # 8. FIT QUALITY vs SPEED
    # ======================================================================

    # Smoothness of the recovered star-formation history. Higher is smoother and
    # more stable, lower is more detailed but noisier. 0 applies no prior at all,
    # which is the default; raise it if you want the
    # history smoothed and can say why.
    smoothness=0.0,

    # Error bars (the summary's Uncertainties section; an <EXT>_ERR extension
    # beside every map of a cube).
    # 0: formal errors from the fit's covariance, at no cost, for the quantities
    # where they are right: A_V, sigma_*, v_*, light-weighted age and Z, gas
    # kinematics, line fluxes, and in nespop A_V^neb, H-alpha/H-beta, T_e, n_e,
    # Q(H). Age bins, x_j, mass-weighted means, masses, f_neb and tau get none
    # (nan): a template entering or leaving the fit moves them, which a
    # covariance cannot see. Nor does any quantity of a spectrum whose chi2/dof
    # exceeds 2 (template mismatch, not noise): high-S/N data need N > 0.
    # N > 0: the bootstrap, the whole fit repeated N times on the model plus its
    # residuals with random signs (40-100), for every quantity; N times the cost.
    error_samples=0,

    # Reject individual pixels that disagree wildly with the model (cosmic rays,
    # unmasked artefacts). Their weight goes to zero and the spectrum is fitted
    # again without them, so the fitted parameters move as well as Nl_eff, adev
    # and the error bars. One clip-and-refit pass, on a spectrum and on every
    # spaxel of a datacube alike. A pixel is an outlier beyond outlier_threshold
    # times its error (outlier_scale, below). See the settings page. Leave on.
    reject_outliers=True,

    # ======================================================================
    # 9. OUTPUT
    # ======================================================================

    # Save a plot of the fit alongside the numbers?
    make_plot=True,

    # ======================================================================
    # 11. ADVANCED — everything else BRAIN can be told
    # ======================================================================

    # active_set : exact. Reaches the same answer as a reference solver to ~1e-12.
    # (fista, the previous iterative solver, is withdrawn: it did not converge
    # on this problem, and BRAIN now fits the data on their own pixels, which
    # only the active-set solver does.)
    linear_solver='active_set',

    # fast      : the only one (fast_cube.py). The NNLS starts from the
    #               previous solution's active templates, the LM derivative is
    #               exact (variable projection), the velocity grid is scanned,
    #               and the model is projected into the data's own pixels. (The
    #               reference fitter, which fitted a log-rebinned copy of the
    #               data, is withdrawn.)
    cube_fitter='fast',

    # Datacubes only: a pixel with a finite flux but no usable error.
    #   exclude     : leave it out (the default). In MaNGA an inverse variance of 0
    #                 marks a pixel not to be trusted.
    #   interpolate : keep it, with its error interpolated from the spaxel's
    #                 neighbouring errors, when the flux is finite and the quality
    #                 mask does not flag it; the flux itself is never changed.
    #                 Some cubes give no error for real data: the JWST NIRSpec
    #                 cubes of 3C 293, CGCG 012-070 and NGC 3884 carry NaN errors
    #                 on 15 % of their pixels and on ~45 % at 2.20-2.27 um.
    missing_error='exclude',

    # ======================================================================
    # 7. NEBULAR PHYSICS   (advanced — "spop" is a perfectly good choice)
    # ======================================================================

    # stellar_kinematics
    #   masked : sigma_* and v_* from the stars alone, with the strong lines and
    #            every other line the spectrum shows masked over
    #            +-kinematics_mask_width. Lines the galaxy does not have stay in
    #            the fit (the Ca II triplet, high-order Balmer absorption, Na D).
    #   joint  : fitted together with the lines.
    # population_fit
    #   masked : the populations (and in nespop the nebular continuum) on the
    #            pixels free of every detected line, then the lines measured on
    #            data - continuum at the fitted gas kinematics. One Gaussian per
    #            line leaves real wings in the residual; fitted jointly, the
    #            populations absorbed them (A_V 0.30 for 0.50 on a mock with
    #            EW(H-alpha) ~ 1200 A).
    #   joint  : stars and lines in one fit.
    stellar_kinematics='masked',
    population_fit='masked',

    # km/s, each side of a masked line
    kinematics_mask_width=1500.0,

    # ======================================================================
    # 11. ADVANCED — everything else BRAIN can be told
    # ======================================================================

    # Search the starting velocity in two passes, a coarse grid over the whole
    # velocity range and then a finer one around its best point, instead of one
    # fine grid. Same answer, far fewer evaluations. Single spectra only.
    coarse_to_fine_grid=True,

    # Estimate the Levenberg-Marquardt derivatives with central rather than
    # forward differences: twice the cost per step, more accurate near the
    # bounds. Single spectra only (a datacube's fast fitter computes them exactly).
    central_differences=False,

    # Force the stellar light fractions to sum to exactly 1. Off by default: the
    # constraint only holds alongside a fitted normalisation flux, so imposing it
    # alone costs accuracy. Reported fractions are normalised to 100% either way.
    enforce_simplex=False,

    # ======================================================================
    # 10. SPEED   (you should not need to change these)
    # ======================================================================

    # BRAIN stores its compiled engine and prepared templates on disk, so the
    # first run is slow and every run after it is fast. Leave both on.
    # To wipe them (always safe, just costs time):  brainsp clear-cache
    use_cached_engine=True,
    use_cached_templates=True,

    # auto picks GPU or CPU sensibly. Force with cpu or gpu if you need to.
    device='auto',

    # Datacubes on a CPU are fitted by several worker processes, each pinned to
    # one core, which scales with the cores (one process cannot: measured 0.9
    # spaxels/s on 4, 16 or 64 cores, and 0.55 on a single core). auto uses
    # every core but two, no more than the free memory allows (about 1.2 GB per
    # worker) and no more than there are spaxels; a number sets it, never above
    # every core but two; 1 turns the pool off. The workers fit the spaxels; the
    # other stages (stars-alone kinematics, weak lines, population and nebular
    # fits, errors) run in the main process, held to every core but two as well.
    # The result is the same as on a GPU, to rounding. A GPU ignores this setting
    # and fits batches of spaxels at once.
    cpu_workers='auto',

    # ======================================================================
    # 11. ADVANCED — everything else BRAIN can be told
    # ======================================================================

    # is column 3 a real error bar?
    has_errorbars=True,

    # must sit in clean continuum, inside range
    normalisation_wavelength=5500.0,

    # 1 penalises differences between neighbouring populations, 2 penalises
    # curvature. Changing this rebuilds the compiled engine.
    smoothness_order=1,
    av_start=0.3,
    dispersion_start=150.0,

    # normally overridden by the velocity search
    v0_start=0.0,
    gas_dispersion_start=100.0,
    gas_v0_start=0.0,

    # km/s step of the initial velocity search
    velocity_grid_step=150.0,

    # relative chi-squared and step tolerance
    fit_tolerance=1e-07,
    max_iterations=200,

    # legacy engine only
    max_function_evals=500,

    # sigma, for reject_outliers
    outlier_threshold=3.0,

    # What outlier_threshold multiplies. error: each pixel's own error, as
    # STARLIGHT's NSIGMA clipping (a pixel more than 3 sigma off the model is
    # dropped however the rest of the spectrum fits). typical: the larger of the
    # error and the spectrum's typical residual, so a model that cannot match a
    # very high-S/N spectrum anywhere does not lose most of its pixels.
    outlier_scale='typical',

    # Lines in one group share a velocity and dispersion. Leave blank to let
    # BRAIN group them automatically. To set them yourself, naming species
    # exactly as BRAIN spells them, spaces and all:
    #   line_groups:
    #     0: [Halpha, Hbeta, "[N II]", "[S II]"]
    #     1: ["[O III]", "[Ne III]"]
    # The labels are names, not positions: they need not be 0 and 1, and need
    # not be contiguous. Every species you do not list falls into group 0,
    # which BRAIN then fits as a group of its own even if you never named it.
    line_groups=None,

    # off: one Gaussian per line. A number (2-4): that many components for every
    # line of the chosen groups, each component sharing one velocity and
    # dispersion across its group, doublets tied as for one component. auto: up
    # to max_line_components, a component kept only when, around its group's
    # lines, it lowers BIC by more than component_bic_threshold and its flux is
    # at least component_min_snr sigma in some line. Component 1 keeps the line
    # names; component k of a line is "<name> #k".
    line_components='off',
    max_line_components=3,

    # blank = every group; else a list of labels
    component_line_groups=None,

    # Blank: every component searches gas_dispersion_range and they are
    # reported narrowest first. Or one [min, max] per component, narrowest
    # first, as ifscube separates narrow from broad: [[40, 300], [300, 2000]]
    component_dispersion_ranges=None,

    # Delta BIC a component must win by (auto)
    component_bic_threshold=10.0,

    # and the S/N its flux must reach somewhere
    component_min_snr=3.0,

    # starting points tried for each new component
    component_seeds=3,

    # sigma_*, v_* held at the espop fit
    component_fix_stellar_kinematics=True,
    helium_abundance=0.25,
    lyman_escape_fraction=0.0,

    # Q(H) is integrated from the raw template files shortward of the Lyman
    # limit. If only some of them reach it, the ones that do carry the whole
    # ionising budget and the rest contribute none, so the number is a property
    # of which templates happen to be long enough rather than of the galaxy.
    # BRAIN refuses that by default. Set true to accept it anyway.
    allow_partial_ionising_coverage=False,

    # A_V of the gas from the Balmer decrement is clipped to this
    nebular_dust_range=[0.0, 6.0],

    # unused since the FADO-style nebular fit
    nebular_dust_start=0.5,

    # unused since the FADO-style nebular fit
    nebular_iterations=12,

    # Lsun or cgs — units of your template files
    ssp_flux_unit='Lsun',

    # unused since the FADO-style nebular fit
    sc_tolerance=0.15,

    # unused since the FADO-style nebular fit
    sc_av_neb_tolerance=0.01,

    # unused since the FADO-style nebular fit
    sc_max_iterations=20,

    # unused since the FADO-style nebular fit
    sc_damping=1.0,

    # nespop: weight of the Case B H-alpha, H-beta rows
    sc_penalty_weight=1000.0,
)

# Each spectrum, with the settings that are its own: the redshift
# BRAIN removes (spectrum_in_rest_frame False) or that was already
# removed (True), and the Milky Way's reddening, E(B-V), R_V and law.
# Paths relative to this file's folder.
SPECTRA = {
    'examples/spectra/mock_star_forming_lines.spec': {},
    'examples/spectra/mock_observed_frame.spec': {'spectrum_redshift': 0.03, 'spectrum_in_rest_frame': False, 'galactic_ebv': 0.05},
}

# Where the results go: <name>_summary.txt, <name>_fitted.txt and,
# with make_plot, <name>_fit.pdf. Relative to this file's folder.
OUTPUT_DIR = 'brain_out'

# The processor: auto (a GPU when JAX sees one), cpu or gpu.
DEVICE = 'auto'

# The wavelength mask, as (start, end, weight); none.
MASK = []


def main(argv):
    flags = [a for a in argv[1:] if a.startswith("--")]
    files = [a for a in argv[1:] if not a.startswith("--")]
    device = DEVICE
    if "--device" in argv:
        device = argv[argv.index("--device") + 1]
        files = [f for f in files if f != device]
    out = here(OUTPUT_DIR)
    settings = SETTINGS.copy()
    for key in ("instrumental_resolution", "library_resolution",
                "base_folder"):
        value = settings.get(key)
        if isinstance(value, str) and value and os.path.exists(here(value)):
            settings[key] = here(value)
    if MASK:
        os.makedirs(out, exist_ok=True)
        mask_file = os.path.join(out, "mask.sm")
        brainsp.write_mask(mask_file, MASK)
        settings["mask"] = mask_file
    listed = {here(f): extra for f, extra in SPECTRA.items()}
    spectra = [os.path.abspath(f) for f in files] or list(listed)
    corrections = {f: listed.get(f, next(iter(listed.values()), {}))
                   for f in spectra}
    missing = [f for f in spectra if not os.path.isfile(f)]
    if missing:
        print("These spectra are not here:\n  " + "\n  ".join(missing))
        return 1
    if "--check" in flags:
        for f in spectra:
            settings.copy(spectrum=f, **corrections[f]).validate()
        print(f"{len(spectra)} spectra, all valid. Output: {out}")
        return 0
    results = brainsp.fit_spectra(spectra, settings, corrections=corrections,
                                  output_dir=out, device=device)
    failed = [r for r in results if r.error_message]
    print(f"\nDone: {len(results) - len(failed)} fitted, {len(failed)} "
          f"failed. Results in {out}")
    for r in results:
        print(f"  {r!r}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
