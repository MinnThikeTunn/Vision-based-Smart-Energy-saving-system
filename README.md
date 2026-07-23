# Vision-Based Smart Energy Saving System

A real-time, vision-based room occupancy detection and energy-saving automation system. The system leverages **YOLOv8** for object detection, **FastAPI** for api routing, and **WebSockets** for a real-time, interactive dashboard showing occupant count, room status, timers, and simulated device states (Light, Fan, AC).

---

## Key Features
* **Vision Inference Pipeline**: Real-time frame capture decoupled from YOLOv8 object detection.
* **Occupancy State Machine**: Uses a configurable *Persistence Window* (to absorb transient camera flickers) and *Empty Timeout* before declaring a room empty.
* **Device Control Matrix**: Evaluates room state and triggers independent automated shutdown timeouts per device.
* **Premium Dashboard UI**: A sleek, dark-mode dashboard styled with a Perplexity-inspired aesthetic, featuring real-time video stream, virtual toggle controls, event logs, and dynamic config settings.

---

## Project Structure
```text
D:\cvProject\
├── app/
│   ├── api/
│   │   ├── config_router.py   # Settings configuration API
│   │   ├── video_router.py    # MJPEG camera stream API
│   │   └── ws_router.py       # WebSocket status stream
│   ├── config/
│   │   ├── loader.py          # Settings parser
│   │   ├── schema.py          # Pydantic models
│   │   └── settings.yaml      # Configuration values
│   ├── decision_engine/
│   │   ├── device_matrix.py   # Automated shutdown evaluation rules
│   │   └── state_machine.py   # Occupancy transitions state machine
│   ├── detector/
│   │   ├── person_detector.py # YOLO and dummy fallback detectors
│   │   └── pipeline.py        # Frame capture & inference worker
│   ├── device_controller/
│   │   ├── base.py            # Device adapter interface
│   │   └── simulation.py      # Simulated device state controller
│   ├── static/
│   │   └── index.html         # Premium dashboard UI
│   └── main.py                # FastAPI app initialization
├── requirements.txt           # Main dependencies list
├── yolov8n.pt                 # YOLO model weight file
└── README.md                  # Setup and usage guide
```

---

## Setup & Installation

Follow these steps to set up the project on your machine.

### 1. Create a Virtual Environment
Create a clean Python virtual environment inside the project directory:
```powershell
python -m venv .venv
```

### 2. Activate the Virtual Environment
Activate the environment:
```powershell
# In PowerShell:
.venv\Scripts\Activate.ps1

# In CMD:
.venv\Scripts\activate.bat
```

### 3. Install Dependencies
Install all required libraries, including websockets support (required by FastAPI for status updates):
```powershell
pip install -r requirements.txt
pip install websockets
```

*Note: The local YOLOv8 weight file (`yolov8n.pt`) is already included in your workspace root, so no internet download is required during startup.*

---

## How to Run

1. **Start the FastAPI Development Server**:
   Ensure your virtual environment is active, then run:
   ```powershell
   python -m uvicorn app.main:app --reload
   ```

2. **Access the Dashboard**:
   Open your browser and navigate to:
   ```text
   http://127.0.0.1:8000
   ```

---

## Testing the Automation Step-by-Step

To verify that the system automatically shuts down devices when you leave the room:

1. **Configure Short Testing Timeouts**:
   On the dashboard, locate the **Settings & Rules** card (right panel) and set the following parameters to short durations:
   * **Persistence Window**: `2` (seconds)
   * **Empty Timeout**: `5` (seconds)
   * **Light Shutdown Timeout**: `5` (seconds)
   * **Fan Shutdown Timeout**: `10` (seconds)
   * **AC Shutdown Timeout**: `10` (seconds)
   * Click **Save Settings**.

2. **Trigger Detection (ON)**:
   * Sit in front of the camera. The system will detect you (`Occupants: 1`), transition the room status to `Occupied`, and turn all virtual devices `ON`.

3. **Trigger Shutdown (OFF)**:
   * Step completely out of the camera's view.
   * Watch the dashboard telemetry:
     - The live occupant count drops to `0`.
     - After **2 seconds** (the persistence window), the countdown begins ticking down from `5` to `0`.
     - Once it reaches `0`, the status transitions to `Empty`.
     - The **Light** countdown hits `0` and immediately shuts down (`OFF`).
     - The **Fan** and **AC** countdowns hit `0` exactly 5 seconds later and shut down (`OFF`).

### Troubleshooting Detections
* If the occupant count stays at `1` when you are away, YOLO may be detecting a background object (such as a chair or cushion) as a person.
* To fix this, increase the **YOLO Confidence Threshold** to `0.70` or `0.75` in the dashboard settings and click **Save Settings** to filter out low-confidence background objects.
