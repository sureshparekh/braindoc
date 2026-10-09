"""
A BRAIN run: datacubes.

Written by brainsp 2.0.0 on 2026-10-08 21:22. Every setting of the run is in this
file; edit it here and run it again:

    python run.py                  run it
    python run.py --check          check everything, fit nothing
    python run.py --device gpu     choose the processor: auto, cpu or gpu

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
    ages='all',

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
    dust_range=[-1.0, 5.0],

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
    # Only has an effect when nebular_mode is 'espop', 'nepop' or 'photopop'.
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
    wavelength_scale=None,

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
    #              mode works with ANY template library.
    #              What it does NOT do: there is no nebular continuum. Real gas
    #              also emits a smooth free-free, free-bound and two-photon
    #              continuum, and in this mode that light has nowhere to go, so
    #              it is absorbed into the stellar populations and the
    #              extinction. A_V and the young populations will be biased by
    #              however much of it is there. If your spectrum has strong
    #              lines and your library reaches the Lyman limit, use nepop.
    #
    #   nepop      As espop, plus the smooth glow from the ionised gas modelled
    #              as its own fitted component, its brightness set by the young
    #              stars BRAIN finds. Needs a template library whose spectra
    #              reach below the Lyman limit at 911.76 A; run
    #              brainsp libraries info <library> to see what yours supports.
    #
    #   photopop   As nepop, plus forcing hydrogen line strengths to agree
    #              with the ionising photon budget.
    #              *** NOT READY FOR SCIENCE USE. The machinery works, but the
    #              predicted line strengths are currently mis-scaled by a large
    #              factor. Use nepop. ***
    nebular_mode='espop',   # default: 'spop'

    # Gas conditions. Used only when nebular_mode is not spop.
    # Kelvin
    gas_temperature=10000.0,

    # electrons per cubic cm
    gas_density=100.0,

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

    # Error bars from resampling the data. 0 skips them (fast). 100-300 gives
    # reliable uncertainties. This is the slowest part of a run.
    error_samples=0,

    # Reject individual pixels that disagree wildly with the model (cosmic rays,
    # unmasked artefacts). Their weight goes to zero and the spectrum is fitted
    # again without them, so the fitted parameters move as well as Nl_eff, adev
    # and the error bars. One clip-and-refit pass, on a spectrum and on every
    # spaxel of a datacube alike. A pixel is an outlier beyond outlier_threshold
    # times the larger of its error and the spectrum's typical residual, so a
    # model that cannot match a very high-S/N spectrum everywhere does not lose
    # most of its pixels. See the settings page. Leave on.
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
    #   fista      : the previous iterative solver. Does not converge on this
    #                problem and returns near-zero fluxes for strong emission
    #                lines. Kept only to reproduce older results.
    linear_solver='active_set',

    # fast      : the same fit, computed faster (fast_cube.py). The NNLS starts
    #               from the previous solution's active templates, the LM
    #               derivative is exact (variable projection) instead of estimated
    #               by finite differences, and the velocity grid is scanned.
    #               Measured on 64 MaNGA spaxels: 2.4x (spop) to 3.9x (espop)
    #               faster; largest change in any fitted value 5e-4 km/s, 2e-5 mag,
    #               2e-5 dex, chi2 identical to 1e-9. YAV is exactly 0 when no
    #               template carries extra dust; the reference lets it drift.
    #   reference : the original batch fitter, kept to reproduce older results.
    # Only the active_set solver can be run fast; fista always uses reference.
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

    # Datacubes on a CPU are fitted by several worker processes, one thread
    # each, which scales with the cores (one process cannot: measured 0.9
    # spaxels/s on 4, 16 or 64 cores, and 0.55 on a single core). auto uses
    # every core but one, no more than the free memory allows (about 1.2 GB per
    # worker) and no more than there are spaxels; a number sets it; 1 turns the
    # pool off. A GPU ignores it and fits batches of spaxels at once.
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
    helium_abundance=0.25,
    lyman_escape_fraction=0.0,

    # Q(H) is integrated from the raw template files shortward of the Lyman
    # limit. If only some of them reach it, the ones that do carry the whole
    # ionising budget and the rest contribute none, so the number is a property
    # of which templates happen to be long enough rather than of the galaxy.
    # BRAIN refuses that by default. Set true to accept it anyway.
    allow_partial_ionising_coverage=False,
    nebular_dust_range=[0.0, 6.0],
    nebular_dust_start=0.5,

    # undamped, |dQ|/Q < 1e-10 by iteration 9 worst case
    nebular_iterations=12,

    # Lsun or cgs — units of your template files
    ssp_flux_unit='Lsun',

    # |tau-1| above this is warned about, not tested
    sc_tolerance=0.15,

    # bracket width that ends the Av_neb search
    sc_av_neb_tolerance=0.01,

    # refits the Av_neb search may spend
    sc_max_iterations=20,

    # damping averages in the Q=0 first iterate; do not lower
    sc_damping=1.0,
    sc_penalty_weight=1000.0,
)

PIPELINE = dict(

    # The datacubes; relative paths are taken from this file's folder.
    cubes=['examples/cube/mock_cube.fits'],

    # The galaxy's redshift: wavelengths are divided by 1 + z.
    # 0 for a cube already in the rest frame. Required, unless
    # PER_CUBE gives every cube its own.
    redshift=0.02,

    # Where the megacubes go; relative to this file's folder.
    output_dir='cube_out',

    # The extension holding the flux.
    flux_hdu='FLUX',

    # The extension holding the uncertainty.
    error_hdu='IVAR',

    # What error_hdu holds: inv_variance, variance, error or inv_error.
    error_type='inv_variance',

    # The extension of bad-pixel flags (None if there is none).
    mask_hdu='MASK',

    # air or vacuum: the cube's wavelength scale. Needed to place
    # emission lines (espop, nepop, photopop). MaNGA/SDSS: vacuum;
    # MUSE, CALIFA: air.
    wavelength_scale='vacuum',

    # Milky Way E(B-V) removed before anything else; 0 = off.
    galactic_ebv=0.0,

    # R_V of the Galactic reddening law.
    galactic_rv=3.1,

    # The Galactic reddening law (CCM, ...).
    galactic_law='CCM',

    # Bin spaxels n x n; None = off.
    spatial_binning=None,

    # Smooth the data to a coarser resolution (to reproduce an older
    # run; it correlates the noise). None = off.
    degrade_resolution=None,

    # Resample the wavelength axis; None = off.
    spectral_binning=None,

    # Spatial low-pass Butterworth filter {order, range}; None = off.
    # It mixes neighbouring spaxels.
    butterworth=None,

    # Signal-to-noise masks to compute: thresholds, the window (Angstrom,
    # rest frame) and the method; None = off.
    sn_mask=[3, 10, 20],

    # Fit only spaxels above this S/N (one of the thresholds);
    # None = every spaxel with data.
    fit_sn_threshold=3,

    # (start, end, weight) regions applied to every spaxel, or a mask file.
    wavelength_mask=None,

    # Spaxels fitted at once; None = automatic.
    batch_size=None,

    # Age bins of the PoPBins maps: (name, youngest yr, oldest yr).
    population_bins=None,

    # Step, in Angstrom, of the linear grid FLXOBS and FLXSYN are written on.
    flxobs_step=None,

    # Star-formation-rate maps: (name, min yr, max yr), Msun/yr;
    # need galaxy_distance. None = none.
    sfr_bins=None,

    # Featureless power laws grouped by exponent: (name, min, max).
    fc_bins=None,

    # Blackbodies grouped by temperature: (name, min K, max K).
    bb_bins=None,

    # Distance in Mpc, for Mstar, Mpcross and the SFRs (per cube:
    # a 'galaxy distance' column of per_cube). None = no masses.
    galaxy_distance=None,

    # The factor the cube's flux unit carries (1e-17 for MaNGA);
    # None = read from BUNIT.
    flux_scale=None,

    # Settings that differ from cube to cube, one dict per cube
    # (target, redshift, ebv, ...); None = none. Files in it are
    # relative to this file's folder.
    per_cube=None,

    # Re-run a cube whose megacube already exists.
    overwrite=True,

    # Record the pipeline inside each megacube.
    save_config=True,

    # Run the fit (False runs the preparation stages only).
    fit=True,
)

# The processor: auto (a GPU when JAX sees one), cpu or gpu.
DEVICE = 'auto'


def main(argv):
    device = DEVICE
    if "--device" in argv:
        device = argv[argv.index("--device") + 1]
    options = dict(PIPELINE)
    options["output_dir"] = here(options["output_dir"])
    options["cubes"] = [here(c) for c in options["cubes"]]
    per_cube = options.get("per_cube")
    if isinstance(per_cube, str):
        options["per_cube"] = here(per_cube)
    elif per_cube:
        options["per_cube"] = [
            {k: (here(v) if k in ("target", "mask file") and isinstance(v, str)
                 and v else v) for k, v in entry.items()}
            for entry in per_cube]
    settings = SETTINGS.copy()
    for key in ("instrumental_resolution", "library_resolution",
                "base_folder"):
        value = settings.get(key)
        if isinstance(value, str) and value and os.path.exists(here(value)):
            settings[key] = here(value)
    pipeline = brainsp.CubePipeline(settings=settings, **options)
    if "--check" in argv:
        pipeline.validate()
        print(f"{len(pipeline.cubes)} cube(s), valid. Output: "
              f"{options['output_dir']}")
        return 0
    written = pipeline.run(device=device)
    print("\nMegacubes written:\n  " + "\n  ".join(written))
    return 0 if len(written) == len(pipeline.cubes) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
