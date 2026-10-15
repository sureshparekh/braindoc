BRAIN tutorial scripts
======================

One script per tutorial of the documentation:
https://sureshparekh.github.io/braindoc/tutorials/

  01_first_spectrum.py   fit one spectrum, read the numbers, plot the fit and SFH
  02_emission_lines.py   stars and gas together (espop), line fluxes, BPT class
  03_agn.py              an active nucleus, without and with AGN templates
  04_many_spectra.py     redshift and Galactic reddening, a batch from a table
  05_masks_settings.py   masks, settings files, a run saved as a script
  06_datacube.py         fit a datacube into a megacube, compare with the truth
  07_megacube.py         maps, spaxels, BPT and WHAN from the megacube (after 06)
  08_many_cubes.py       many cubes without a display, as on a server
  brain_job.slurm        the same as a SLURM batch job

Needs brainsp installed. Run in this folder, in order:

  python 01_first_spectrum.py

Each script writes the mock data (examples/) if it is missing; the mocks
come with the true values they were built from. A GPU is used when there
is one; on a CPU each script takes a few seconds to two minutes.
