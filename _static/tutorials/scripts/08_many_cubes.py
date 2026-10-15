"""Tutorial 8: many cubes, no display (a server, a batch job).

Run:  python 08_many_cubes.py
Same as:  brainsp cube examples/cube/mock_cube.fits --redshift 0.02 \
              --wavelength-scale vacuum --sn 3 --fit-sn 3 -o megacubes
"""
import brainsp

brainsp.mock.write_examples("examples")
brainsp.set_device("auto")                 # "gpu" or "cpu" to choose

# A glob fits every cube it matches. Per-cube redshifts can come from a
# table instead: per_cube="targets.csv".
p = brainsp.CubePipeline("examples/cube/mock_cube.fits",
                         redshift=0.02,
                         settings=brainsp.Settings(nebular_mode="espop"),
                         wavelength_scale="vacuum",
                         sn_mask=[3], fit_sn_threshold=3,
                         output_dir="megacubes",
                         overwrite=False)  # skip cubes already done
p.validate()
p.run(log=print)
