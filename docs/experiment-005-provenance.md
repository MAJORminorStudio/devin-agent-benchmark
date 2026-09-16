# Experiment 005 Provenance and Embargo

## Historical/public half

K01-K05 are intentionally known/public defects from the [BugsInPy dataset](https://github.com/reproducing-research-projects/BugsInPy), pinned at commit [`316b95e2353ecda832bad9b42f86fa7c2fcec8ac`](https://github.com/reproducing-research-projects/BugsInPy/tree/316b95e2353ecda832bad9b42f86fa7c2fcec8ac). The dataset records the project URL, bug directory, buggy revision, fixed revision, and relevant upstream test. The selected records are:

| Case | BugsInPy record | Upstream project | Buggy revision | Fixed revision |
|---|---|---|---|---|
| E005-K01 | [fastapi bug 1](https://github.com/reproducing-research-projects/BugsInPy/tree/316b95e2353ecda832bad9b42f86fa7c2fcec8ac/projects/fastapi/bugs/1) | [tiangolo/fastapi](https://github.com/tiangolo/fastapi) | `766157bfb4e7dfccba09ab398e8ec444d14e947c` | `3397d4d69a9c2d64c1219fcbf291ea5697a4abb8` |
| E005-K02 | [luigi bug 23](https://github.com/reproducing-research-projects/BugsInPy/tree/316b95e2353ecda832bad9b42f86fa7c2fcec8ac/projects/luigi/bugs/23) | [spotify/luigi](https://github.com/spotify/luigi) | `c707253572deb795a900c3e07d21eee591a55fca` | `dc41727f4de88f86f4e77aa45be51eff4ee6b3be` |
| E005-K03 | [tornado bug 6](https://github.com/reproducing-research-projects/BugsInPy/tree/316b95e2353ecda832bad9b42f86fa7c2fcec8ac/projects/tornado/bugs/6) | [tornadoweb/tornado](https://github.com/tornadoweb/tornado) | `fb74e4816ccfa7fc6a7abd8c8aab1f415cfc1b13` | `2905ee4fb3c283d40b10f609359e189c83a0dc06` |
| E005-K04 | [tornado bug 10](https://github.com/reproducing-research-projects/BugsInPy/tree/316b95e2353ecda832bad9b42f86fa7c2fcec8ac/projects/tornado/bugs/10) | [tornadoweb/tornado](https://github.com/tornadoweb/tornado) | `ecd8968c5135b810cd607b5902dda2cd32122b39` | `5931d913b4ea250891a0b582f1f8b2901b868c79` |
| E005-K05 | [thefuck bug 16](https://github.com/reproducing-research-projects/BugsInPy/tree/316b95e2353ecda832bad9b42f86fa7c2fcec8ac/projects/thefuck/bugs/16) | [nvbn/thefuck](https://github.com/nvbn/thefuck) | `d92765d5df6607cb2f2fb67cee7b63f64ac7aa6b` | `bb5f6bb705a3b217eb682f3357ec6bbb709555c1` |

Historical cases are not novel and may have appeared in training data or
public coding corpora. That is an intended provenance condition, not a
contamination claim. Their source checkout is used only to materialize a
buggy agent workspace and private fixed/evaluation trees; the public freeze
records provenance and hashes, not source snapshots.

## Newly constructed/withheld half

H01-H05 are the five original E005 cases: feature-plan, work-queue, wire-relay,
order-flow, and event-ledger. They were constructed for this benchmark and
withheld from Devin before execution. The claim is limited to construction and
withholding; absence from unknowable model training corpora is not claimed.
Their private source, fixed trees, prompts, reference patches, held-out tests,
and construction notes remain embargoed.

The first E005 freeze contained only H01-H05 and had no execution. The current
freeze expanded it to K01-K05 plus H01-H05 before execution, replacing the
original ten-run order with a new twenty-run randomized order.

## Private validation and leak boundary

The ignored local staging root is
`local-run-store`. It contains the historical checkout
cache and verification trees, K/H buggy and fixed trees, visible and private
tests, prompt files, reference patches, evaluator output, H02 shortcut review,
and twenty run-workspace templates. Nothing under this root is a public case
artifact.

The validator fails closed. For each K run it checks that the workspace has no
`.git`, fixed revision hash, fixed/evaluation tree, metadata, or patch artifact;
for each H run it additionally scans forbidden benchmark and solution markers.
It materializes separate M and X templates for each case and records a
pass/fail audit for all twenty planned run IDs. Fixed trees and held-out suites
are opened only in the private validation process after workspace materialization;
the future container evaluator remains outside the agent container until the
session is closed.

## Integrity records

The public freeze manifest contains SHA-256 hashes for each buggy/fixed tree,
reference patch, public/held-out/regression test group, prompt, and agent
workspace template, plus hashes for the configuration, run order, validator,
workspace auditor, and container planner. The private repeat validator recorded
buggy target failures, fixed target passes, regression preservation, stable
repeat outcomes, and zero Devin/SWE-2 invocations.
