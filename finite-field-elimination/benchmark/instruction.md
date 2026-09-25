# Finite-Field Elimination Certificate

> Archived verbatim from the original benchmark prompt, preserved here only
> so the verifier setup in this folder remains reproducible. The completed
> certificate and its writeup live in
> [`../certificate/reference_certificate.json`](../certificate/reference_certificate.json)
> and [`../README.md`](../README.md).

Recover an exact shape-position representation of the zero-dimensional polynomial system in `/app/data/system.json` over the prime field `F_1009`.

The public variables are

```text
x0, x1, x2, x3, x4, x5, x6, t
```

and the auxiliary elimination parameter is `s`, related to the public variables by

```text
s = t + x0*x1
```

The instance is guaranteed to admit a representation

```text
h(s) = 0
x0 = r_x0(s)
...
x6 = r_x6(s)
t  = r_t(s)
```

where `h` is monic, splits into distinct linear factors over `F_1009`, and every root of `h` determines exactly one solution of the public polynomial system.

Write `/app/certificate.json` as a JSON object with this schema:

```json
{
  "prime": 1009,
  "parameter": "s",
  "solution_count": 0,
  "eliminant": [0, 0, 1],
  "coordinates": {
    "x0": [0],
    "x1": [0],
    "x2": [0],
    "x3": [0],
    "x4": [0],
    "x5": [0],
    "x6": [0],
    "t": [0]
  }
}
```

The numerical values above are only schema examples, not a solution.

Polynomial coefficient arrays use ascending-degree order: `[c0, c1, c2]` represents `c0 + c1*s + c2*s^2`. Submit coefficients as integer representatives in `[0, 1008]`. The eliminant must be monic, its degree must equal `solution_count`, and every recovery polynomial must have degree strictly less than the eliminant degree.

The verifier is semantic rather than textual. It enumerates the roots of the submitted eliminant in `F_1009`, reconstructs all public-variable tuples, checks `s = t + x0*x1`, evaluates every public polynomial exactly modulo 1009, checks distinctness and completeness, and compares the represented solution set with sealed ground truth. Equivalent valid certificates are accepted regardless of how they were computed.

You may use any method available in the environment. Singular is installed, but its use is not required.

You have 28800 seconds to complete this task. Do not cheat by using online solutions or hints specific to this task.
