# Research Log

---

## 2026-07-21

### Objective

Investigate the dependence of quantum information observables on collision energy in

\[
e^+e^- \rightarrow t\bar t
\]

using MadGraph5_aMC Density Mode.

---

### Energy points

- 350 GeV
- 365 GeV
- 500 GeV
- 700 GeV
- 1000 GeV
- 3000 GeV

---

### Analysis pipeline

1. Generate events using MG5 Density Mode.
2. Produce LHE files.
3. Compute event dataset.
4. Perform energy comparison.

---

### Important correction

Originally,

\[
\cos\theta
=
\frac{p_z}{|\vec p|}
\]

was used.

After checking Appendix C of

Durupt et al. (2026),

the convention was corrected to

\[
\cos\theta
=
-\frac{p_z}{|\vec p|}.
\]

All datasets were regenerated.

---

### Result

The concurrence maximum moved from

\[
\cos\theta \approx +0.51
\]

to

\[
\cos\theta \approx -0.51
\]

matching the literature prediction

\[
\theta \simeq 0.67\pi.
\]

This confirms that the simulation now follows the same angular convention as the paper.