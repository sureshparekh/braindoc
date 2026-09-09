# Extinction laws

Dust dims and reddens starlight. How much it does so at each wavelength is
described by an **extinction curve** $k(\lambda)$, and BRAIN applies it as

$$ F_{\rm obs}(\lambda) = F_{\rm intrinsic}(\lambda) \times
   10^{-0.4\,A_V\,[k(\lambda) - k(\lambda_{\rm norm})]} $$

$A_V$ is fitted. The curve is your choice, and BRAIN implements twelve.

---

## The twelve curves

Pick the curve that matches the dust you think you are looking through, not the
most recent paper.

=== "Milky Way"

    | Key | Reference | Notes |
    |---|---|---|
    | `CCM` | Cardelli, Clayton & Mathis (1989) | $R_V = 3.1$. **The safe default** |
    | `HZ1` | Allen (1976) | Tabulated and interpolated |
    | `HZ2` | Seaton (1979), fit by Fitzpatrick (1986) | |

=== "Starburst"

    | Key | Reference | Notes |
    |---|---|---|
    | `CAL` | Calzetti et al. (2000) | $R_V = 4.05$ |
    | `CCC` | Calzetti (2000) + Leitherer (2002) | Far-UV extension below 1846 Å |
    | `HZ5` | Calzetti (2000), STARLIGHT form | Identical curve to `CAL` |

=== "Large Magellanic Cloud"

    | Key | Reference | Notes |
    |---|---|---|
    | `HZ3` | Fitzpatrick (1986) | |
    | `GD3` | Gordon et al. (2003) | LMC average |
    | `GD2` | Gordon et al. (2003) | LMC2 supershell, near 30 Doradus |

=== "Small Magellanic Cloud"

    | Key | Reference | Notes |
    |---|---|---|
    | `HZ4` | Prévot (1984) & Bouchet (1985) | |
    | `GD1` | Gordon et al. (2003) | SMC bar. Steep UV, no 2175 Å bump |
    | `GD24` | Gordon et al. (2024) | |

---

## Choosing one

```yaml
reddening_law: CCM
```

!!! tip "For a purely optical fit, this matters less than it looks"
    These curves differ mainly in the **ultraviolet** — the presence or absence
    of the 2175 Å bump, and the steepness of the far-UV rise. Fitted over
    3700–6900 Å they give very similar answers:

    | Law | $A_V$ | $\sigma_\star$ | $\chi^2/N$ |
    |---|---|---|---|
    | `CCM` | 0.212 | 47.2 | 0.5673 |
    | `CAL` | 0.248 | 46.4 | 0.5666 |
    | `GD1` | 0.183 | 46.6 | 0.5670 |
    | `GD24` | 0.201 | 50.4 | 0.5688 |

    The choice becomes important once your range reaches below about 3000 Å.

`CAL`, `CCC` and `HZ5` agreeing exactly in the optical is correct — they are the
same Calzetti curve, differing only in their far-UV extensions.

---

## Extra extinction on young stars

```yaml
young_extra_dust_range: [0.0, 5.0]
```

Young stars are still inside the molecular clouds they formed from, so they are
often dustier than the older population around them. This adds a second
extinction parameter, `YAV`, applied only to templates flagged as young in the
catalogue.

It is reported as `YAV_min` in the summary. Set the range to `[0.0, 0.0]` to
disable it.

!!! note
    This only does something if your template catalogue actually flags young
    populations. The bundled `BasesGM/` library does not, so `YAV` will be
    exactly zero — which is why BRAIN skips it in the Jacobian and pays nothing
    for it.

---

## Adding a curve

All twelve live in one registry in `reddening_laws.py`:

```python
LAWS = {
    "CCM": ("Cardelli, Clayton & Mathis (1989)",
            "Milky Way average, R_V = 3.1. The safe default."),
    ...
}
```

Add an entry there and a branch in `get_k_lambda`, and it appears in the
settings validator, the desktop dropdown and this documentation automatically.
The function must return $k(\lambda)$ normalised so that $k(5500\,\text{Å})
\approx 1$.
