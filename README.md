# BRAIN — documentation website

The documentation of **BRAIN** (the `brainsp` Python package): stellar
population synthesis by full spectral fitting, for spectra and IFU
datacubes, on a CPU or a GPU.

### Read it at **<https://sureshparekh.github.io/braindoc/>**

---

This repository only serves the website. The site lives on the `gh-pages`
branch, which GitHub Pages publishes; it is built from the documentation
source in the code repository,
[sureshparekh/brainv1](https://github.com/sureshparekh/brainv1)
(`documentation/`), and pushed here by `documentation/publish.sh`:

```bash
# in a clone of brainv1, with the docs extras installed (pip install -e ".[docs]")
documentation/publish.sh
```

Nothing on this branch is built: edit the documentation in brainv1.
