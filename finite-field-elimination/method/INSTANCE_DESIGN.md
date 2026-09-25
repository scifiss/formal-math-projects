# Finite-Field Elimination Instance Design

## Final instance

This task uses exact polynomial arithmetic over the prime field

$
\mathbb F_{1009}.
$

The frozen public variables are

```text
x0, x1, x2, x3, x4, x5, x6, t
```

The final generated instance uses:

```text
seed              = 20260923
solutions         = 40
recovery degree   = 9
mixing rounds     = 2
shear pairs       = 1
prime             = 1009
```

The ideal is zero-dimensional with quotient-space dimension 40.

## Hidden shape representation

The instance is constructed from an auxiliary parameter `s`, not from public `t` directly. Before obfuscation, the hidden system has shape form

$
h(s)=0,
\qquad
x_i=r_i(s),\quad i=0,\ldots,6,
$

where `h` is monic of degree 40 and splits into 40 distinct linear factors over \(\mathbb F_{1009}\).

The public coordinate `t` is related to the hidden parameter by the nonlinear polynomial shear

$
s=t+x_0x_1,
$

so that

$
t=s-x_0x_1.
$

This change of coordinates is invertible. The generator substitutes `s = t + x0*x1` into the hidden shape generators and then applies invertible elementary generator mixing. The resulting public system therefore defines exactly the same 40 points while no longer exposing the primitive parameter as a standalone public coordinate.

## Certificate representation

A valid certificate uses `s` as its auxiliary parameter and contains:

- the prime `1009`;
- `parameter = "s"`;
- the exact solution count;
- a monic eliminant `h(s)`;
- one recovery polynomial in `s` for every public variable `x0,...,x6,t`.

Coefficient arrays use ascending-degree order:

```text
[c0, c1, c2]
```

means

$
c_0+c_1s+c_2s^2.
$

All submitted coefficients are interpreted modulo 1009. Recovery polynomials are represented canonically with degree strictly less than `deg(h)`.

## Semantic verification

The verifier does not compare a submitted Gröbner basis or certificate textually. It checks the represented solution set exactly.

For a submitted certificate it:

1. validates the certificate schema and field;
2. enumerates all roots of `h(s)` in \(\mathbb F_{1009}\);
3. requires exactly `solution_count` distinct roots and `deg(h) = solution_count`;
4. evaluates every recovery polynomial at every root;
5. checks the auxiliary relation \(s=t+x_0x_1\);
6. checks every reconstructed point against every public polynomial modulo 1009;
7. checks that all reconstructed public points are distinct;
8. compares the reconstructed set with sealed ground truth.

The verifier therefore accepts semantically equivalent valid certificates rather than requiring one particular textual Gröbner-basis form.

## Difficulty calibration

The final instance was selected by an automated parameter search over solution count, recovery degree, nonlinear shear strength, generator-mixing rounds, and deterministic seeds. Candidate generation was rejected when the public system became unnecessarily large or when the reference certificate failed exact semantic verification.

Measured locally on the authoring machine for the frozen instance:

```text
degree-order std + FGLM     4.28 s, 4.37 s, 3.99 s
Singular groebner + FGLM    4.19 s
direct lex Gröbner basis    > 60 s (timed out)
slimgb route                > 30 s (timed out)
```

The successful FGLM runs consistently recovered quotient-space dimension 40. These measurements are calibration data rather than grading thresholds; solver performance may vary by machine.

The final public system has:

```text
8 public polynomials
4,767 sparse terms total
maximum total degree 82
system.json size 965,650 bytes (~0.92 MiB)
```

The exact Python verifier accepted the frozen reference certificate locally in about 2.6 seconds.

## Frozen artifact hashes

The final artifacts are frozen at the following SHA-256 values:

```text
3b7fc256601e94cae33c67a8a0962ae1844aeac67ea587653138d2d65e133334  data/system.json
d45c11c7708dbd46ade7501fc3448fea440260aec167f7ada249444b901b1fb2  data/spec.json
1045ea488292948ac93368fbdefa7c4721bbab6dee4fbdfccf9d0fb69e9bfdb0  benchmark/tests/data/ground_truth.json
991519803d2283794b070946baa0e0fc9b67d4eff72839731bf9014407b71ff2  certificate/reference_certificate.json
```

`data/system.json` and `benchmark/tests/data/system.json` are intended to be byte-identical copies, as are the two `spec.json` files. Private answer material exists only under `benchmark/tests/` and `certificate/` and was not part of the original agent-visible environment.
