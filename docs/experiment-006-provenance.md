# Experiment 006 Provenance and Novelty Boundary

## Historical half

The K half is drawn from the external BugsInPy checkout pinned in
`sources/bugsinpy.json` at commit
`316b95e2353ecda832bad9b42f86fa7c2fcec8ac`. The selected records and their
immutable upstream commits are recorded in
`manifests/experiment-006-config.json`; the private historical manifest also
records Python versions, original test files, buggy/fixed commits, and
commands. The five selected IDs are black-6, PySnooper-1, black-23,
thefuck-17, and tqdm-2. None is reused from E001-E005.

The historical source checkout is never copied into this control repository.
The private preparation produced separate buggy, fixed, and agent-workspace
trees. Fixed trees, solution-bearing `bug_patch.txt` material, private
behavior/regression tests, and validation outputs stay under the ignored
`local-run-store` root.

K02 needed an explicitly recorded public compatibility adapter: the pinned
upstream Chinese-source test did not fail on the pinned local validation
interpreter. The adapter asserts the same intended source-decoding contract
for a no-cookie Python-3.8 file, and the held-out suite separately checks a
declared Latin-1 file. This is an adaptation, not an undisclosed oracle
change.

## Novel half

H01-H05 were written specifically for E006 as small, dependency-free Python
projects. Their visible tasks describe symptoms and required public tests but
do not expose the evaluator scenarios, exact mutated line, reference patch,
or construction notes. The private ground-truth matrix was created before any
agent execution and was checked by running each buggy/fixed pair in the same
local Python-3.8 validation environment. No agent, SWE-2 model, or autonomous
repair loop was used in design, calibration, or validation.

“Withheld” means withheld from Devin before a future launch; it does not claim
that a public language model has never seen a similar pattern. The public
repository contains only task prompts, high-level case descriptions, hashes,
and methodology. The private validator fails on fixed-tree, private-test,
reference-patch, prior-result, credential, and control-repository leakage.

## Freeze identity

The public freeze manifest is hash-only for private material. It binds the
configuration, run order, protocol, calibration, survey, provenance,
validator, container planner, prompts, and each private case's buggy/fixed
trees, reference patch, public test, held-out tests, regression tests, and
sanitized agent-workspace template. Hashes are generated only after the final
ground-truth and leak audits pass.

## Infrastructure re-freeze

The first E006 freeze was not executed. Its mandatory dependency gate found
that the original Devin image exposed only Python 3.11.2 and lacked the
`python` command, pytest, and the historical project dependencies needed by
the frozen cases. No case, prompt, evaluator, reference repair, result, or
run-order material was changed in response. The replacement image is an
immutable `devin-e006:3000.10.21-r7` layer based on the exact original Devin
image; its pinned runtimes, package locks, build definition, and case mapping
are recorded under `isolation/experiment-006/` and in the configuration.
Dependencies were selected from the frozen BugsInPy metadata and project
metadata/requirements, with the pre-freeze E006 validator used as the
compatibility check. Installation occurs only at image build time. A
control-side runtime validator ran all ten buggy/fixed matrices twice in 40
fresh containers and matched the original ground-truth signatures. This
infrastructure change is the sole reason for the new authoritative freeze.
