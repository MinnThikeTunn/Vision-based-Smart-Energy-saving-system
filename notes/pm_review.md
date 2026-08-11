# Product Discovery & Outcomes Evaluation: Vision-Based Smart Energy Saving System

**Evaluator:** Marty Cagan (Product Discovery & Outcomes)  
**Target Repository:** `D:\cvProject`  
**Date:** August 2026  
**Status:** Action Required — High Technical Output, High Product Risk  

---

## 🎯 Executive Summary & Overall Score

The **Vision-Based Smart Energy Saving System** is a classic case of **engineering excellence building in a product vacuum**. The repository demonstrates impressive technical depth—YOLOv8 inference, decoupled frame queues, centroid tracking state machines, Prometheus metrics, and automated ROI analytics. 

However, evaluated strictly through the lens of **Product Discovery, Business Viability, and Customer Value over Output**, this project behaves as a **Phase-based Feature Factory**. It optimizes solutions (ONNX acceleration, pose estimation keypoints, synthetic power ramp curves) before validating core product risks (privacy adoption, total cost of ownership, hardware processing power overhead, and ROI vs. cheap PIR/mmWave alternatives).

### Scorecard Summary

| Evaluation Axis | Score | Verdict |
| :--- | :---: | :--- |
| **1. Customer Value & Business Outcomes** | **4 / 10** | Flawed baseline economics; processing power overhead ignored. |
| **2. Team Empowerment & Discovery** | **3 / 10** | Roadmap is a rigid, output-driven 8-phase feature factory. |
| **3. Problem vs. Solution Fit** | **4 / 10** | Over-engineered vision solution for a problem solved by $10 PIR/mmWave sensors. |
| **4. Product-Design-Engineering Alignment** | **5 / 10** | Strong tech architecture; missing customer UX and facilities buyer alignment. |
| **OVERALL PRODUCT DISCOVERY SCORE** | **4.0 / 10** | **High Output / Low Outcome Risk** |

---

## 1. Does this create measurable customer value and business outcomes?

**Score: 4 / 10**

### What’s Working:
* **Quantified Financial and Carbon Telemetry**: [`app/analytics/energy_calculator.py`](file:///D:/cvProject/app/analytics/energy_calculator.py) explicitly tracks cumulative kWh, cost savings ($), and CO2e prevented (kg), giving facilities managers visible metrics to report.
* **Granular Device Mapping**: [`app/config/settings.yaml`](file:///D:/cvProject/app/config/settings.yaml) supports rated wattages for specific appliances (AC at 1200W, fans, lights) enabling differential energy modeling.

### Core Product Flaws:
1. **Flawed Baseline Metrics (The "Always-ON" Fallacy)**:
   * The ROI calculation in `EnergyCalculator` evaluates savings against an `Always-ON` baseline. In real commercial or residential settings, occupants already turn off lights/AC manually or existing building management systems (BMS) operate on timers. Claiming 34.2% kWh savings against an Always-ON baseline overstates value proposition by 2-3x.
2. **Ignoring the System's Own Energy Consumption (Negative Parasitic Load)**:
   * Running real-time YOLOv8 person detection on a local host/edge device requires a GPU or high-power CPU running 24/7 (drawing ~15W to 60W continuous power). 
   * A 30W edge server consumes **0.72 kWh/day ($0.108/day)**. If the system turns off a 40W light bulb and a 65W fan for 4 hours a day, it saves 0.42 kWh/day—meaning **the vision system consumes more energy processing video frames than it saves turning off low-wattage appliances!**
3. **No Total Cost of Ownership (TCO) or Payback Period Model**:
   * Hardware costs (cameras, edge compute boxes, smart relays, installation labor) are completely unmodeled. Without factoring hardware capex and maintenance against real net energy savings, customer ROI is unverified.

---

## 2. Is the team empowered for continuous discovery rather than feature factories?

**Score: 3 / 10**

### Core Product Flaws:
1. **Output-Driven Phase-Based Roadmap**:
   * [`docs/version2.md`](file:///D:/cvProject/docs/version2.md) lays out a rigid 8-Phase execution schedule (Phase 0 to Phase 8) over 7 weeks.
   * Tasks are measured by engineering effort (`S`, `M`, `L`) and tech outputs (ONNX export, ByteTrack integration, Canvas anonymization) rather than validated customer outcomes or risk reduction milestones.
2. **Building for GitHub Standouts over Customer Validation**:
   * Phase 8 explicitly names its objective: *"Add stand-out features to set this project apart from standard occupancy-detection projects on GitHub."*
   * This is a **Portfolio/Engineering output goal**, not a **Product Outcome goal**. True discovery tests value, usability, feasibility, and viability hypotheses with real target users (facilities managers, office managers, enterprise IT), not star counts.
3. **Lack of Discovery Experiments**:
   * The roadmap lacks any product discovery loops: zero user interviews, zero pilot deployment metrics, zero A/B testing on occupancy shutdown grace periods (`empty_timeout_sec: 300` vs user comfort/frustration).

---

## 3. Are we solving the right problem before optimizing the solution?

**Score: 4 / 10**

### Core Product Flaws:
1. **Severe Privacy Risk & Adoption Barrier**:
   * Deploying optical cameras into offices, private desks, or rooms creates massive corporate surveillance anxiety, employee pushback, and legal compliance hurdles (GDPR, works council approvals).
   * While `settings.yaml` and `docs/privacy.md` introduce `anonymize_faces: true` and `headless_mode: false`, the presence of a visual lens remains a non-starter for 70%+ of commercial office customers.
2. **Wrong Tech Stack for 80% of Occupancy Scenarios**:
   * For binary room occupancy (Occupied vs. Empty), **PIR (Passive Infrared)**, **Ultrasonic**, or **mmWave Radar** sensors cost $10–$25, consume < 0.5W of power, require zero video pipelines, and carry zero privacy risks.
   * The camera vision approach is only justified if **Spatial ROI** (Zone A: Desk vs Zone B: Transit) or **Count-based HVAC modulation** provides significant net energy savings that exceed the heavy compute cost and privacy friction. This core hypothesis remains unvalidated.

---

## 4. Is there alignment across product, design, and engineering on outcomes?

**Score: 5 / 10**

### What’s Working:
* **Engineering-Architecture Cleanliness**: High domain clarity in [`CONTEXT.md`](file:///D:/cvProject/CONTEXT.md) and crisp separation between `detector`, `decision_engine`, `device_controller`, and `analytics`.

### Core Product Flaws:
1. **Dashboard Target Audience Mismatch**:
   * The WebSocket dashboard (`index.html`) serves developer/engineering telemetry (Prometheus endpoints, raw frame rates, state machine logs) rather than actionable decision tools for facilities managers (e.g., monthly budget impact, zone efficiency heatmaps, override alerts).
2. **Disconnect Between Config & Reality**:
   * In `settings.yaml`, `spatial_zones` includes typos (`deak_`, duplicate `Zone 3` names) indicating configuration drift and a lack of validated UX editing tools for non-technical users.

---

## 🛑 The Four Product Risks Assessment

```
┌────────────────────────────────────────────────────────────────────────┐
│                        CAGAN RISK MATRIX ANALYSIS                      │
├───────────────────┬──────────────┬─────────────────────────────────────┤
│ Risk Type         │ Risk Level   │ Evaluation & Evidence               │
├───────────────────┼──────────────┼─────────────────────────────────────┤
│ 1. Value Risk     │ 🔴 HIGH      │ Net ROI negative when factoring     │
│    (Will buy/use?)│              │ compute power & capex costs.        │
├───────────────────┼──────────────┼─────────────────────────────────────┤
│ 2. Usability Risk │ 🟡 MEDIUM    │ Manual YAML setup & dev-centric     │
│    (Can figure out?)│            │ dashboard UI.                       │
├───────────────────┼──────────────┼─────────────────────────────────────┤
│ 3. Feasibility    │ 🟢 LOW       │ Engineering stack (YOLO/FastAPI)    │
│    (Can we build?)│              │ is proven and working.              │
├───────────────────┼──────────────┼─────────────────────────────────────┤
│ 4. Viability Risk │ 🔴 HIGH      │ Privacy compliance & corporate      │
│    (Works for biz?)│             │ surveillance pushback.              │
└───────────────────┴──────────────┴─────────────────────────────────────┤
```

---

## 💡 Actionable PM Recommendations (Pivoting from Output to Outcome)

### Recommendation 1: Correct the Net Energy Formula Immediately
Modify `EnergyCalculator` in [`app/analytics/energy_calculator.py`](file:///D:/cvProject/app/analytics/energy_calculator.py) to account for **Edge Computer Processing Overhead Power**:
$$\text{Net Saved kWh} = \text{Baseline Appliance kWh} - \text{Actual Appliance kWh} - \text{System Processing Overhead kWh}$$
* If Net Saved kWh is negative, surface a warning flag in the API telemetry.

### Recommendation 2: Shift Focus from Whole-Room Sensing to High-Wattage Spatial ROI
* Stop attempting to turn off 40W LED lights with a 30W GPU server.
* Focus **exclusively** on high-wattage appliances (1,200W–3,500W AC/HVAC units and commercial zone heaters) where spatial ROI (turning off HVAC in unused zones while keeping active desk zones comfortable) yields massive net positive financial returns ($50–$300/month per zone).

### Recommendation 3: Convert the Roadmap into Outcome-Based Discovery Milestones
Replace the 8-phase feature factory in [`docs/version2.md`](file:///D:/cvProject/docs/version2.md) with outcome-driven discovery questions:
1. *Milestone 1 (Viability Test)*: Can we achieve 100% privacy compliance using mmWave radar fallback or hardware-enforced edge anonymization?
2. *Milestone 2 (Value Test)*: Can the system demonstrate a < 12-month hardware payback period in a real 3-zone office pilot?
3. *Milestone 3 (Usability Test)*: Can a facilities manager setup spatial ROI zones in < 3 minutes on the web UI without touch screen/YAML editing?

---

**Summary Statement**: Stop adding roadmap features (pose detection, predictive ML) to impress GitHub. Validate the net economic ROI and solve privacy viability with real facilities buyers first. Engineering is complete; Product Discovery must begin.
