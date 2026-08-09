# 3. Zero-Device Default Onboarding and Custom Virtual Device Engine

* Status: Accepted
* Date: 2026-08-09

## Context and Problem Statement

The system previously shipped with hardcoded default virtual devices (`Light`, `Fan`, `AC`) and default spatial zones (`Zone A`, `Zone B`) pre-configured out-of-the-box. Users needed the flexibility to define their own custom virtual devices with customized power ramp durations, rated wattages, shutdown delays, and spatial zone mappings, starting with a clean slate out-of-the-box.

## Decision Drivers

* Start clean out-of-the-box with zero pre-configured devices or zones.
* Support user-defined Custom Virtual Devices with custom names, categories, power ratings, shutdown delays, and per-device power ramp profiles.
* Provide a high-end, Perplexity-aesthetic 2-step onboarding experience in the UI side panel when zero devices exist.
* Maintain bidirectional synchronization between browser `localStorage` and backend `settings.yaml`.

## Considered Options

1. Static pre-configured devices with editing capability.
2. Zero-device default with full dynamic custom-device lifecycle and guided onboarding wizard.

## Decision Outcome

Chosen Option: Option 2 (Zero-device default with custom virtual device engine and guided onboarding).

### Positive Consequences

* Clean, un-cluttered initial state requiring no deletion of sample devices.
* Full flexibility for custom electrical device modeling (e.g. server racks, heaters, monitors).
* Seamless persistence across page reloads and server restarts via dual `localStorage` + REST API synchronization.

### Negative Consequences

* Energy calculation baseline remains 0 W until user completes onboarding step 1 and step 2.
