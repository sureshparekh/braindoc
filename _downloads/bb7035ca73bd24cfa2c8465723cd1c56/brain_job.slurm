#!/bin/bash
# Tutorial 8: a SLURM job fitting every cube in cubes/ on one GPU.
# Submit with:  sbatch brain_job.slurm
#SBATCH --job-name=brain
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=16
#SBATCH --time=04:00:00

source ~/miniconda3/bin/activate brain
brainsp cube cubes/*.fits --table targets.csv --wavelength-scale vacuum \
    --sn 3 10 --fit-sn 3 --set nebular_mode=espop --device gpu -o megacubes
