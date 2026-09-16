# Third-party notices and licensing boundary

The root [`LICENSE`](LICENSE) applies only to material original to this
repository. It does not relicense third-party projects, benchmark data,
historical patches, generated agent output, or provider materials.

## BugsInPy

This project uses BugsInPy as an external, pinned source checkout. The dataset
source lock is recorded in [`sources/bugsinpy.json`](sources/bugsinpy.json),
including commit `316b95e2353ecda832bad9b42f86fa7c2fcec8ac`. The BugsInPy
repository is not vendored here. No root license file was located in the
pinned source checkout used for this benchmark; this notice therefore makes
no license assumption for the dataset and does not grant permission to
redistribute it. Review the upstream repository and its contributor/project
notices before redistributing a BugsInPy checkout or its source contents.

- [BugsInPy repository](https://github.com/reproducing-research-projects/BugsInPy)
- [Pinned BugsInPy source revision](https://github.com/reproducing-research-projects/BugsInPy/tree/316b95e2353ecda832bad9b42f86fa7c2fcec8ac)

## Historical OSS projects

The five benchmark cases refer to historical revisions of these projects. The
case manifests record the exact buggy and fixed commits. The repository may
contain small sanitized patches and evidence derived from those projects;
those materials remain subject to the applicable upstream terms and notices.

| Project | Upstream license file inspected | License observed at upstream source |
|---|---|---|
| Black | [`LICENSE`](https://github.com/psf/black/blob/fb34c9e19589d05f92084a28940837151251ebd6/LICENSE) | MIT |
| FastAPI | [`LICENSE`](https://github.com/tiangolo/fastapi/blob/869c7389e22dc9ad659940fa271da76c4f3ba3b1/LICENSE) | MIT |
| Scrapy | [`LICENSE`](https://github.com/scrapy/scrapy/blob/be2e910dd06ba4904e7b10eb5a7e3251e8dab099/LICENSE) | BSD-style terms |
| tqdm | [`LICENCE`](https://github.com/tqdm/tqdm/blob/19b08ab34fdbfa0275bc5cb2430436c724c7e759/LICENCE) | Mixed notices: MIT and MPL-2.0 exceptions are described there |
| Tornado | [`LICENSE`](https://github.com/tornadoweb/tornado/blob/d7d9c467cda38f4c9352172ba7411edc29a85196/LICENSE) | Apache-2.0 |

The upstream files are the authoritative licensing sources. This table is a
navigation aid, not a legal determination of every dependency or every file
in an upstream distribution. Downstream users should retain upstream notices
when redistributing source-derived material and inspect dependency licenses
separately.

## Agent and provider materials

Devin, Cognition, SWE-2, and related product names are used descriptively.
They are not licensed by this repository. Public run artifacts contain
sanitized observable session metadata and output; provider terms continue to
govern any underlying service materials.
