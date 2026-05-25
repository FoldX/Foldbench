# Inference Protocol

## Overview

This protocol defines the communication specification for robot control inference services. It is used to connect a local robot client with a remote inference server.

---

## Test Pipeline

The end-to-end test flow works as follows:

1. **You implement the inference service** — Based on this sample code, wrap your model in a service that exposes the `POST /predict` API (see `server.py`). Replace `load_model()` and the inference logic inside `predict()` with your own policy.
2. **You run the service locally or on a reachable host** — Start the server (e.g. `python server.py`) so it listens on a known host and port.
3. **The local ARK Aloha arm acts as the client** — The on-robot (or local) control stack collects joint state and camera images, calls your `/predict` endpoint at the configured rate (up to 50 FPS), and applies the returned 14-D action vector to the dual-arm system.

Participants provide an inference API; the robot side pulls observations and posts actions over HTTP. Here, `client.py` is a minimal stand-in for the Aloha client; in production, the ARK stack replaces it while keeping the same request/response format.

```
┌─────────────────────┐     HTTP POST /predict      ┌──────────────────────┐
│  ARK Aloha (client) │  ─────────────────────────► │  Your inference API │
│  state + images     │  ◄─────────────────────────  │  (this sample)      │
│  applies action     │         action [14]         │  load_model + predict│
└─────────────────────┘                             └──────────────────────┘
```

### Quick start (local test)

```bash
# Terminal 1: start the inference server
python server.py

# Terminal 2: simulate the robot client (optional smoke test)
python client.py
```

Point the real Aloha client at your server URL (same multipart fields as `client.py`).

---

## User Guide

### 1. Installation

```bash
cd /path/to/sample_code

# (Recommended) Create and activate a virtual environment
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

pip install fastapi uvicorn numpy opencv-python requests
```

### 2. Customize the server

Edit `server.py`:

1. Implement `load_model()` — load checkpoints and return your policy object.
2. Implement inference in `predict(state, images)` — map observations to a 14-D `numpy` action vector.

Keep the HTTP contract (`POST /predict`, multipart fields, JSON response) unchanged so the Aloha client can connect without modification.

### 3. Test

```bash
# Start the service
python server.py

# Run the sample client against http://localhost:8000/predict
python client.py
```

For integration with the real arm, configure the client stack to use your server host/port and verify latency stays within the 30s timeout at your target control rate.

---

## Protocol Specification

### Endpoint

**POST /predict**

### Request format

`multipart/form-data`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| state | string (JSON) | Yes | Joint state array (14 floats) |
| task | string | Yes | Task name |
| cam_high | file (JPEG) | No | High camera image |
| cam_left_wrist | file (JPEG) | No | Left wrist camera image |
| cam_right_wrist | file (JPEG) | No | Right wrist camera image |

### Response format

```json
{
    "action": [j0, j1, j2, j3, j4, j5, g0, j6, j7, j8, j9, j10, j11, g1]
}
```

---

## Data Formats

### State vector (state) — 14 dimensions

| Index | Meaning |
|-------|---------|
| 0–5 | Left arm joints 1–6 |
| 6 | Left gripper |
| 7–12 | Right arm joints 1–6 |
| 13 | Right gripper |

### Action vector (action) — 14 dimensions

Same layout as `state`.

### Images

| Property | Value |
|----------|-------|
| Format | JPEG |
| Size | 224 × 224 |
| Channels | RGB |

---

## Communication Parameters

| Parameter | Value |
|-----------|-------|
| Protocol | HTTP/1.1 |
| Encoding | multipart/form-data |
| JPEG quality | 100 |
| Timeout | 30 s |
| Call rate | up to 50 FPS |

---

## Files

```
client.py   # Example client (robot side)
server.py   # Server template (your inference API)
```

**Server responsibilities:**

1. `load_model()` — load your model
2. `predict(state, images)` — run inference and return a 14-D action

**Client responsibilities (Aloha / `client.py`):**

1. Read joint state and cameras
2. POST to `/predict`
3. Apply returned `action` to the robot

---

