# E008 Comparability Audit

| Dimension | Classification | Evidence / limit |
| --- | --- | --- |
| Canonical cases, IDs, difficulty | IDENTICAL | All 30 parent cases and 10 cases per tier are present in the E007 manifest. |
| Source repository/base | IDENTICAL or EQUIVALENT | Parent manifests/freeze records preserve repository/commit or frozen tree hashes; E007 stages the same frozen source snapshots. |
| Task prompt | IDENTICAL | Prompt SHA-256 reconciles for each case. |
| Held-out and regression tests | IDENTICAL | E007 calls the parent evaluator assets; frozen hashes or unchanged referenced evaluator paths are recorded below. |
| Scoring logic | EQUIVALENT | Primary TASK_SUCCESS still requires public, held-out, and regression suites to pass; evaluator implementation is parent-specific and reused. |
| Model and effort | IDENTICAL | Exact original/E007 Medium and Max selectors and returned generation model IDs agree. |
| Isolation/permissions | EQUIVALENT | Fresh Docker workspaces; Linux/arm64; dangerous/Bypass; read-only root; dropped capabilities; no control repo/home/docker socket; evaluator unavailable until session close. |
| CLI/runtime | EQUIVALENT | CLI 3000.10.21 (611c1cba). E006 uses frozen e006 image; other parent tiers use e002 image with same case-specific setup. |
| Execution date | CHANGED | Original sessions were on Sep 15–16, 2026; E007 ran Sep 25, 2026. |
| Private backend deployment revision | UNKNOWN | Not exposed per session. |
| E007 very-hard evaluator result | CHANGED / evaluator-invalid for affected cells | E007 pytest collection used host-path-cached bytecode. Clean-copy rechecks of preserved workspaces changed six outcomes per effort; see E008-E007-EVALUATOR-RECHECK.md. E007 records remain unmodified. |
| E007 wrapper/setup incidents | CHANGED | One High-only wrapper record is incomplete; rejected pre-session catalog attempts and proxy recovery occurred before accepted runs. The wrapper gap is outside Medium/Max. |
| Billing | UNKNOWN | No direct billing data. Catalog labels SWE-2 variants Free; account-level cost was not observable. |

## Case-by-case frozen identity checks

| Case | Tier | Parent experiment | Prompt SHA-256 | Base/tree evidence | Held-out evidence | Regression evidence |
| --- | --- | --- | --- | --- | --- | --- |
| E002-C02 | moderate | E002 | identical | 869c7389e22dc9ad659940fa271da76c4f3ba3b1 | same referenced evaluator path | same referenced evaluator path |
| E002-C04 | moderate | E002 | identical | 19b08ab34fdbfa0275bc5cb2430436c724c7e759 | same referenced evaluator path | same referenced evaluator path |
| E002-C01 | moderate | E002 | identical | fb34c9e19589d05f92084a28940837151251ebd6 | same referenced evaluator path | same referenced evaluator path |
| E002-C05 | moderate | E002 | identical | d7d9c467cda38f4c9352172ba7411edc29a85196 | same referenced evaluator path | same referenced evaluator path |
| E002-C03 | moderate | E002 | identical | be2e910dd06ba4904e7b10eb5a7e3251e8dab099 | same referenced evaluator path | same referenced evaluator path |
| E004-N05 | moderate | E004 | identical | 3e88cee06a6e7232bb948e0769a536f891f403cfa780ea53e52eb8f09a1beb77 | 0a765cfd6a9e5db8c4896b9cf0184416f294cec11911f9833a6d56f1b08b0d88 | 3600d8f677dd35b536cc51cfc1199dd749a7bee2b97086221b17e870a7bf9eb6 |
| E004-N04 | moderate | E004 | identical | 33dcb4040821d0c9498ebe538a1b2f53ad1b5f75c143350aa2f93fe81a7bd1c1 | 950f57196cb84246cdc4fc5e65eb0a1797112d505681e6274d6cf4119b0e751f | a7119f48567c13cb6942ba921267997d18adad17e0a815483a445fac76b9ea84 |
| E004-N01 | moderate | E004 | identical | 195667d0c4721066ab7ecd59e676f1f78d841ddf269860cd2ab46733eccde513 | da184f36d41c37de5be409d67a34ebcf599e6fb97ebfd6eae8a20682e3397dc7 | 86823f0df442c56cd4011f597d3f6704bb0d36c33448f8ed57339af726ce8ebb |
| E004-N02 | moderate | E004 | identical | 750c3e095e165da446064c07348da6cad3d9b9457325a4f96585e17cb27eff5b | 64c483c3c3340801bc1ce512b3913c25c81995453cc365064f57eeb91d5000b5 | 3efe111fd55281f53811ef85e119c52d68af1d6d3209f437bc7562161c8e135a |
| E004-N03 | moderate | E004 | identical | 96a71c976f74812f8a73eec0871988fdebb68cb9b1e35c459f038e0d4ab53a48 | 7f0b5f76fb6819be56d801749370813172053b796853b2e0428dc118ddb5385e | 40ed71d48cc060759cb487f82a63f66c406687bf60179bdb47fa5d8e5fa89c01 |
| E005-K04 | hard | E005 | identical | 2d7f7dd46a1123d079ab2102e0004c63078ee7a371ca0cb2762f6293b42c8579 | ff2c769d221921e7701bd2ccfd34921a58142e8f512ca8a4dc7f0464b387eb0e | f31ceaaf318118119e960fc3a79340e675672122cc34a3e605586488c0430a68 |
| E005-K05 | hard | E005 | identical | e63126cb649e2cf5525bdf3e081c64ddc4a29e07d51ac5c14a993622f9628bb9 | 5f98d558a6882d22ae27c8307317c6fe0d86c390f5cc514ea8af8bb8ddbc2de5 | 3e94a633c234da6b443e9327ad770257f2d199331f3214cdfe433e736f21fa93 |
| E005-K02 | hard | E005 | identical | 4810451132769f38e6fe9b43682cbe604d461485d99a6bd7bae3ec31635c978e | 1f92b1a033762ce3695603a87a5be617050c327f4586f7f9e91e1c36e6d0a771 | 2b252cb40e51e645f3d03be59c69f4319ad5d58d494787e1a5bd818000886c88 |
| E005-K01 | hard | E005 | identical | f17a4de1420375d320b05ae49630dba33de742e88e7219f1ad4495b88222af25 | f3acd804354cbc752f56363c322c2bdf7d9dc813ef85aca1266f8ac222456d3f | 9ea1781f89f6fbb8f74f2a1a2234ac37d87aaaa03b9bbc60cf016b9c90f7b920 |
| E005-H05 | hard | E005 | identical | 609554ae61eca457dcac7198c3b78e885fde3cb92660cd769b6064297088ab30 | 048d56e6f622a756343e6689d966236469651cdc0e741f3a9404a8b2625aebf3 | 8f8ccb0e164cbc68b2b43c1574c340ebfe1d191039bee16a6f5c234503d8c47a |
| E005-H04 | hard | E005 | identical | 85d682080352fb9d10bbe1414106310ee1e52b41f33d163fcb4a06ecf742b411 | 9087196a6a27179ff0e8003bdee29aed5198676392d7e6517731f4aed18024d2 | 7e9154a51fe3d3fe5cf902f4df9ca6b78ce5a4f45dc32b8bccac20eac347281e |
| E005-H03 | hard | E005 | identical | 467195ccffe2f481aea2b304d0f44b0e117d6c46fa9a38dc2a466a920650871b | e8b456c60fa4c4c65b49d7af27c1ff0bfc94209ddc3ece38e3028d33d8e62db9 | 1e6ce1f2aba10c0da03ff616243b89d096dd3898511516d9c86c3b7298bdaa8b |
| E005-K03 | hard | E005 | identical | ee927dcffcab9c2dda294749cc24c51dfd74f0d814c27c87aee5f244ce9c650b | bb29e8d9cda6df640a80b1acee8f6cabf3a13f38d09bf93eff3a1f6fafa0fe2c | 540616a4c59cbc1a9f2f08de31db711d76aa26507d890955d8ce3c641b924b6f |
| E005-H01 | hard | E005 | identical | 51de31a932c9c8b0d0c00edafbb1a85ad4580e4ba236341011fab07bbc457ac9 | 29166de5393b057778e93930b923ac32ad3e10ba62fc77f216492a1ad3965433 | 46e9dfa73ea806d42f091ab6cc89765eda1ba20a279f4f4c3b14883db874d9ba |
| E005-H02 | hard | E005 | identical | 540dbd98d22fd6cd02fe9880cb0d0ff680bab5ea7490fca1b3247829a0671368 | 8c38c744e37d9d7675b6017a26e8a3a775ad5e1e751f3eeac0429060a4428cca | c6c68e13107ea51566b0a4015387ed8ecfce3755efa3e76a99314c75a6208612 |
| E006-K03 | very-hard | E006 | identical | 42d55576373a26045d51643c0309e560ab074c8d6b4ac835686df000fd6b11d7 | 9c4c4e36353b4cb15896afb6d48ead827ecbd4bf5295a56e75211b3a48a0f838 | 3eff128cf1f711685d351d0059eb98e05907c4c972908103a0be166770bec8c1 |
| E006-H02 | very-hard | E006 | identical | b1caca29d0b12d59ff87a97f89e6ed19a14ebb6d04d5b94889091d700c9a849e | f7c3f407e2c8d181da20ded2d5687d6cc520f5bdd9b7099bdf22215630385c72 | 708fb33f5b9b428ddb553306b64cc2d07c5e6b1a0b585e7a5a7a455e284170f3 |
| E006-H03 | very-hard | E006 | identical | 73d4e96c43ae6dd705e72ff1870d54754941e42f44db539bd698ae414656abd8 | 37a962885eef0ab5138c998128adbe674ab702b3c6453dd4eeee055782155547 | d41a39d225201f39371caae9a4c4a305b4168ed8591ae0201d157a56be445001 |
| E006-K05 | very-hard | E006 | identical | 3073c86a50b77bd09ab08899e32b213be57e56493b6acfc9cf0c3564f8415394 | 8f7aff44aba0186326da618152775eea413a0d41f269554e1f6725d214f62c05 | 92f4ea2750b5e7551413eff98ccae604449d23a18bb4296ab4be8a6d2101eef5 |
| E006-K04 | very-hard | E006 | identical | bf401e4f6cf650d7163ed206e15eef2b6a0a562a8a0bbef7c7410c786ac81072 | 3c80e425cab8a78d17c82f0772c9242ab8c8131f96f1d86ed7c877a28542a0db | ed67b411fabb3e7457324fdafde746cf5d136f6b20b30c9ab0f901aa46c7ef91 |
| E006-H01 | very-hard | E006 | identical | 0400d16988f6835a92307d11b2562a5d9a9fd9ed96402c19916283b3d23dba25 | f05f3fcf344767c4996cc2ec3a56561b5fe717f6f3e77b48b8688f3d33607ae3 | 71771522ad8585cd90c54a58f947bd66df2c6cb719b46459a0b4d008265e49ab |
| E006-H05 | very-hard | E006 | identical | 75ba42fd562146efec3ff36a9c99f905f72f3bdcb28b42567f492d4b56a3e2ea | 456dd484f2c8a31d0780ec854ddb956872266f629e3a8d7f4206804a85ee2e79 | 81431cb7d6f69202992042bf08704f3b6a25a580fcd6b9e75433183e65842fb1 |
| E006-K02 | very-hard | E006 | identical | 6bf3021d8c6a8b153940c2af4c19c9019b9b6a68533b48e463f8db4bfde9028c | 9d1b40a1fda3d76f07a4ca5a01914ccd19af927b4be96636ac78df6bb1c6132e | 94dbc80b01bfb43159cddb66e33dbd354e9a2153cb94a892ee874a71cfed20e8 |
| E006-H04 | very-hard | E006 | identical | 7cba5d7e23e2da957663e8fc64703451aa0369c0621ffef16e1fc2d34253e9d6 | df1a29bb2ac7ba52da3e147bdab8ef1006b3dc7979673f9a33d7fa1f485b1ce0 | 43320ea0899e9c53f93d9fd922802d91b2d65b0ff718463dfed0998a676f99a1 |
| E006-K01 | very-hard | E006 | identical | b98930bf1ccaeaccbadddd34cc2420e977552a37a302dec6e13a06b897db413a | 44b781fe9f7fa1e27b8d26f791d06e98c38334b4dcedea8e3c4b085cf9b66236 | a8b0a3012468c80334f3fab50ca8c5a9b2020cdad35cfa506b68c27a5a987304 |

**Verdict:** Frozen task definitions and the scoring contract are comparable, but E007’s original E006 evaluator results are invalid for affected cells because of a test-collection artifact. E008 uses clean-copy re-evaluation of the preserved E007 workspaces as a separate corrected-outcome sensitivity analysis. The date changed and private backend revision is unknown, so attribution between stochastic variation and temporal service drift remains unresolved.
