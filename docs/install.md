# Installation

BRAIN needs **Python 3.10 or newer**. It runs on Linux, macOS and Windows.

## The short version

```bash
git clone https://github.com/sureshparekh/brainv1.git
cd brainv1
pip install -r requirements.txt
python run_brain.py --check
```

If the last command prints `brain_setup.yaml is valid`, you are ready.

---

## In an isolated environment

Recommended, so BRAIN's dependencies cannot collide with anything else you have
installed.

=== "venv"

    ```bash
    python -m venv brain-env
    source brain-env/bin/activate        # Windows: brain-env\Scripts\activate
    pip install -r requirements.txt
    ```

=== "conda"

    ```bash
    conda create -n brain python=3.12
    conda activate brain
    pip install -r requirements.txt
    ```

---

## As an installed package

```bash
pip install -e ".[gui]"
```

`-e` installs it in editable mode, so the files stay where they are and your
edits take effect immediately. Drop `-e` for a fixed install.

Extras available:

| Extra | Brings in |
|---|---|
| `gui` | PySide6, for the desktop interface |
| `cuda` | The CUDA 12 build of JAX |
| `docs` | MkDocs, to build this site locally |

---

## Using a GPU

The default JAX wheel is **CPU-only**. That is deliberate: it installs
everywhere without a CUDA toolkit, and for single spectra it is often just as
fast, because the problem is small enough that the cost of moving data to the
card dominates.

For an NVIDIA card:

```bash
pip install --upgrade "jax[cuda12]"
```

Confirm which backend JAX picked:

```bash
python -c "import jax; print(jax.default_backend())"
```

`gpu` means the card is in use. Nothing in BRAIN changes — it follows whatever
JAX reports. To force the CPU for one run, set `device: cpu` in the settings
file, or:

```bash
JAX_PLATFORMS=cpu python run_brain.py
```

!!! tip "When the GPU is actually worth it"
    A GPU pays off for **datacubes and large batches**, where thousands of
    spectra are fitted in one process and the card stays saturated. For a
    single spectrum on a modern CPU the difference is small.

---

## What gets installed

| Dependency | Why |
|---|---|
| `jax` | The whole numerical engine — compiled, vectorised, differentiable |
| `numpy`, `scipy` | Array handling and interpolation |
| `matplotlib` | Plots, and the canvas inside the desktop interface |
| `PyYAML` | Reading `brain_setup.yaml` |
| `astropy` | FITS input for datacubes |
| `PySide6` | The desktop interface (optional) |

---

## Putting BRAIN in your applications menu

```bash
python install_desktop.py
```

Creates a launcher with the BRAIN icon — a `.desktop` entry on Linux, a small
`.app` bundle on macOS, a Start Menu shortcut on Windows. Undo it with
`python install_desktop.py --remove`.

---

## Verifying the installation

```bash
python run_brain.py --check      # settings are consistent
python run_brain.py --templates  # list the available SSPs
python brain_gui.py              # the desktop interface opens
```

A full run on the bundled example takes about thirty seconds the first time
and much less afterwards — see [Performance](performance.md) for why.
