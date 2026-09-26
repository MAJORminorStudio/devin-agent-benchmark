# E008 Discordant Cases

There are **9 discordant cases** and 11 case-effort outcome changes. The trace counts below are heuristic classifications of preserved tool calls; they do not expose or infer hidden reasoning.

## E002-C02 (moderate)

### Medium

**OBSERVATION:** The original run E002-C02-M was a solve; E007 run E007-E002-C02-MEDIUM was a fail. Original evaluator note: successful repair. E007 evaluator suites: public. E007 failing test identifiers, when printed: tests/test_serialize_response_model.py::test_valid, tests/test_serialize_response_model.py::test_coerce, tests/test_serialize_response_model.py::test_validlist, tests/test_serialize_response_model.py::test_validdict. Steps: 35 vs 34; wall seconds: 299.3 vs 288.41546212503454; input+output tokens: 609329 vs 473186. Source files changed: original fastapi/routing.py, E007 fastapi/routing.py (3 total changed paths before generated-file filtering). Heuristic trace counts (exploration/edit/test calls): original 22/3/6, E007 23/4/5. First edit steps: 14 vs 9.

**INTERPRETATION:** The evaluator localizes the observable difference to public. The recorded patch/file list and final pass/fail establish the outcome, but the counts alone do not establish whether localization, diagnosis, implementation, or verification caused it.

**UNRESOLVED:** These are only two observations for this condition. Ordinary stochastic run variance, temporal backend/model drift, and smaller execution-service differences remain unresolved. No causal explanation is assigned from the traces.

## E002-C05 (moderate)

### Medium

**OBSERVATION:** The original run E002-C05-M was a solve; E007 run E007-E002-C05-MEDIUM was a fail. Original evaluator note: successful repair. E007 evaluator suites: heldout. E007 failing test identifiers, when printed: (errors=1). Steps: 33 vs 30; wall seconds: 175.5 vs 184.25452741695335; input+output tokens: 439766 vs 500008. Source files changed: original tornado/http1connection.py, E007 tornado/http1connection.py, tornado/httputil.py (36 total changed paths before generated-file filtering). Heuristic trace counts (exploration/edit/test calls): original 24/7/8, E007 19/5/7. First edit steps: 9 vs 9.

**INTERPRETATION:** The evaluator localizes the observable difference to heldout. The recorded patch/file list and final pass/fail establish the outcome, but the counts alone do not establish whether localization, diagnosis, implementation, or verification caused it.

**UNRESOLVED:** These are only two observations for this condition. Ordinary stochastic run variance, temporal backend/model drift, and smaller execution-service differences remain unresolved. No causal explanation is assigned from the traces.

### Max

**OBSERVATION:** The original run E002-C05-X was a solve; E007 run E007-E002-C05-MAX was a fail. Original evaluator note: successful repair. E007 evaluator suites: heldout. E007 failing test identifiers, when printed: (errors=1). Steps: 36 vs 44; wall seconds: 326.5 vs 358.496036291006; input+output tokens: 793236 vs 1167356. Source files changed: original tornado/http1connection.py, E007 tornado/http1connection.py (40 total changed paths before generated-file filtering). Heuristic trace counts (exploration/edit/test calls): original 27/5/10, E007 37/4/7. First edit steps: 16 vs 24.

**INTERPRETATION:** The evaluator localizes the observable difference to heldout. The recorded patch/file list and final pass/fail establish the outcome, but the counts alone do not establish whether localization, diagnosis, implementation, or verification caused it.

**UNRESOLVED:** These are only two observations for this condition. Ordinary stochastic run variance, temporal backend/model drift, and smaller execution-service differences remain unresolved. No causal explanation is assigned from the traces.

## E004-N03 (moderate)

### Medium

**OBSERVATION:** The original run E004-N03-M was a solve; E007 run E007-E004-N03-MEDIUM was a fail. Original evaluator note: none recorded. E007 evaluator suites: heldout. E007 failing test identifiers, when printed: test_replacing_values_does_not_retain_caller_mutation, (failures=1). Steps: 16 vs 16; wall seconds: 81.4 vs 90.90612900000997; input+output tokens: 124965 vs 121988. Source files changed: original not recorded, E007 not recorded (0 total changed paths before generated-file filtering). Heuristic trace counts (exploration/edit/test calls): original 10/2/4, E007 9/2/3. First edit steps: 14 vs 14.

**INTERPRETATION:** The evaluator localizes the observable difference to heldout. The recorded patch/file list and final pass/fail establish the outcome, but the counts alone do not establish whether localization, diagnosis, implementation, or verification caused it.

**UNRESOLVED:** These are only two observations for this condition. Ordinary stochastic run variance, temporal backend/model drift, and smaller execution-service differences remain unresolved. No causal explanation is assigned from the traces.

### Max

**OBSERVATION:** The original run E004-N03-X was a fail; E007 run E007-E004-N03-MAX was a solve. Original evaluator note: none recorded. E007 evaluator suites: all suites pass. E007 failing test identifiers, when printed: not exposed in runner output. Steps: 17 vs 18; wall seconds: 119.4 vs 180.28072887501912; input+output tokens: 160160 vs 190891. Source files changed: original not recorded, E007 not recorded (0 total changed paths before generated-file filtering). Heuristic trace counts (exploration/edit/test calls): original 16/2/3, E007 20/1/3. First edit steps: 15 vs 15.

**INTERPRETATION:** The evaluator localizes the observable difference to all suites pass. The recorded patch/file list and final pass/fail establish the outcome, but the counts alone do not establish whether localization, diagnosis, implementation, or verification caused it.

**UNRESOLVED:** These are only two observations for this condition. Ordinary stochastic run variance, temporal backend/model drift, and smaller execution-service differences remain unresolved. No causal explanation is assigned from the traces.

## E005-K04 (hard)

### Medium

**OBSERVATION:** The original run E005-K04-M was a fail; E007 run E007-E005-K04-MEDIUM was a solve. Original evaluator note: Public and held-out behavior failed because cycle cleanup was moved into RequestHandler.finish, clearing template state before an ordinary WebSocket render; regression passed.. E007 evaluator suites: all suites pass. E007 failing test identifiers, when printed: not exposed in runner output. Steps: 32 vs 38; wall seconds: 145.1 vs 251.35783912497573; input+output tokens: 26872 vs 689606. Source files changed: original tornado/web.py, tornado/websocket.py, E007 not recorded (0 total changed paths before generated-file filtering). Heuristic trace counts (exploration/edit/test calls): original 21/3/2, E007 28/4/1. First edit steps: 19 vs 18.

**INTERPRETATION:** The evaluator localizes the observable difference to all suites pass. The recorded patch/file list and final pass/fail establish the outcome, but the counts alone do not establish whether localization, diagnosis, implementation, or verification caused it.

**UNRESOLVED:** These are only two observations for this condition. Ordinary stochastic run variance, temporal backend/model drift, and smaller execution-service differences remain unresolved. No causal explanation is assigned from the traces.

## E005-K02 (hard)

### Max

**OBSERVATION:** The original run E005-K02-X was a fail; E007 run E007-E005-K02-MAX was a solve. Original evaluator note: Held-out behavior failed because the patch added the scheduler parameter and pruning call but did not enable pruning in the local scheduler factory; public and regression suites passed.. E007 evaluator suites: all suites pass. E007 failing test identifiers, when printed: not exposed in runner output. Steps: 56 vs 97; wall seconds: 571.8 vs 744.8037050830317; input+output tokens: 69632 vs 5717960. Source files changed: original luigi/scheduler.py, E007 not recorded (0 total changed paths before generated-file filtering). Heuristic trace counts (exploration/edit/test calls): original 47/5/1, E007 61/9/7. First edit steps: 36 vs 23.

**INTERPRETATION:** The evaluator localizes the observable difference to all suites pass. The recorded patch/file list and final pass/fail establish the outcome, but the counts alone do not establish whether localization, diagnosis, implementation, or verification caused it.

**UNRESOLVED:** These are only two observations for this condition. Ordinary stochastic run variance, temporal backend/model drift, and smaller execution-service differences remain unresolved. No causal explanation is assigned from the traces.

## E005-K01 (hard)

### Medium

**OBSERVATION:** The original run E005-K01-M was a solve; E007 run E007-E005-K01-MEDIUM was a fail. Original evaluator note: none recorded. E007 evaluator suites: heldout. E007 failing test identifiers, when printed: test_encoder_options_reach_models_and_containers, (failures=1). Steps: 81 vs 48; wall seconds: 771.7 vs 375.06597058300395; input+output tokens: 130442 vs 1324263. Source files changed: original fastapi/applications.py, fastapi/encoders.py, fastapi/openapi/utils.py, fastapi/routing.py, E007 not recorded (0 total changed paths before generated-file filtering). Heuristic trace counts (exploration/edit/test calls): original 58/26/7, E007 34/18/7. First edit steps: 31 vs 33.

**INTERPRETATION:** The evaluator localizes the observable difference to heldout. The recorded patch/file list and final pass/fail establish the outcome, but the counts alone do not establish whether localization, diagnosis, implementation, or verification caused it.

**UNRESOLVED:** These are only two observations for this condition. Ordinary stochastic run variance, temporal backend/model drift, and smaller execution-service differences remain unresolved. No causal explanation is assigned from the traces.

## E005-H03 (hard)

### Max

**OBSERVATION:** The original run E005-H03-X was a fail; E007 run E007-E005-H03-MAX was a solve. Original evaluator note: Regression failed because the attempted oversized-frame recovery skipped the following valid frame when the declared oversized payload bytes were not present; public and held-out suites passed.. E007 evaluator suites: all suites pass. E007 failing test identifiers, when printed: not exposed in runner output. Steps: 18 vs 17; wall seconds: 226.1 vs 207.63201287499396; input+output tokens: 25378 vs 200563. Source files changed: original src/wire_relay/framing.py, src/wire_relay/session.py, E007 not recorded (0 total changed paths before generated-file filtering). Heuristic trace counts (exploration/edit/test calls): original 8/3/4, E007 14/2/4. First edit steps: 13 vs 12.

**INTERPRETATION:** The evaluator localizes the observable difference to all suites pass. The recorded patch/file list and final pass/fail establish the outcome, but the counts alone do not establish whether localization, diagnosis, implementation, or verification caused it.

**UNRESOLVED:** These are only two observations for this condition. Ordinary stochastic run variance, temporal backend/model drift, and smaller execution-service differences remain unresolved. No causal explanation is assigned from the traces.

## E006-H03 (very-hard)

### Medium

**OBSERVATION:** The original run E006-H03-M was a fail; E007 run E007-E006-H03-MEDIUM was a solve. Original evaluator note: public-suite failure. E007 evaluator suites: all suites pass. E007 failing test identifiers, when printed: not exposed in runner output. Steps: 12 vs 15; wall seconds: 119.9 vs 124.79168204200687; input+output tokens: 70509 vs 123502. Source files changed: original src/wire_relay/framing.py, E007 not recorded (0 total changed paths before generated-file filtering). Heuristic trace counts (exploration/edit/test calls): original 7/2/1, E007 8/2/2. First edit steps: 10 vs 12.

**INTERPRETATION:** The evaluator localizes the observable difference to all suites pass. The recorded patch/file list and final pass/fail establish the outcome, but the counts alone do not establish whether localization, diagnosis, implementation, or verification caused it.

**UNRESOLVED:** These are only two observations for this condition. Ordinary stochastic run variance, temporal backend/model drift, and smaller execution-service differences remain unresolved. No causal explanation is assigned from the traces.

## E006-H01 (very-hard)

### Max

**OBSERVATION:** The original run E006-H01-X was a solve; E007 run E007-E006-H01-MAX was a fail. Original evaluator note: successful repair. E007 evaluator suites: regression. E007 failing test identifiers, when printed: not exposed in runner output. Steps: 18 vs 18; wall seconds: 409.6 vs 130.95040879200678; input+output tokens: 239665 vs 224663. Source files changed: original src/feature_store/cache.py, src/feature_store/resolver.py, E007 not recorded (0 total changed paths before generated-file filtering). Heuristic trace counts (exploration/edit/test calls): original 13/3/3, E007 14/2/3. First edit steps: 12 vs 12.

**INTERPRETATION:** The evaluator localizes the observable difference to regression. The recorded patch/file list and final pass/fail establish the outcome, but the counts alone do not establish whether localization, diagnosis, implementation, or verification caused it.

**UNRESOLVED:** These are only two observations for this condition. Ordinary stochastic run variance, temporal backend/model drift, and smaller execution-service differences remain unresolved. No causal explanation is assigned from the traces.

