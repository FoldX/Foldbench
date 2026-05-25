"""
Lesuite Inference Client

Calls the /predict endpoint: sends state and images, receives an action vector.
Simulates the ARK Aloha robot-side control loop for local testing.
"""

import numpy as np
import requests
import json
import cv2

SERVER_URL = "http://localhost:8000/predict"


def send_http_request(obs):
    """
    obs = {
        'joints': np.array(14,),  # joint state
        'task': str,               # task name
        'cam_high': np.array(...), # optional image (RGB, uint8)
        'cam_left_wrist': ...,
        'cam_right_wrist': ...
    }
    """
    try:
        data = {
            'state': json.dumps(obs["joints"].tolist()),
            'task': obs["task"]
        }
        files = {}
        for key in ['cam_high', 'cam_left_wrist', 'cam_right_wrist']:
            if key in obs and obs[key] is not None:
                img = cv2.cvtColor(obs[key].astype(np.uint8), cv2.COLOR_RGB2BGR)
                _, buffer = cv2.imencode('.jpg', img, [cv2.IMWRITE_JPEG_QUALITY, 100])
                files[key] = (f'{key}.jpg', buffer.tobytes(), 'image/jpeg')
        response = requests.post(SERVER_URL, data=data, files=files, timeout=30)
        response.raise_for_status()
        return np.array(response.json()["action"], dtype=np.float32)
    except Exception as e:
        print(f"Error: {e}")
        return np.zeros(14, dtype=np.float32)


def main():
    obs = {
        'joints': np.random.rand(14).astype(np.float32),
        'task': 'balcony_pick_place',
        'cam_high': np.random.randint(0, 255, (224, 224, 3)).astype(np.uint8),
        'cam_left_wrist': np.random.randint(0, 255, (224, 224, 3)).astype(np.uint8),
        'cam_right_wrist': np.random.randint(0, 255, (224, 224, 3)).astype(np.uint8)
    }
    action = send_http_request(obs)
    print(f"Action: {action}")


if __name__ == "__main__":
    main()
