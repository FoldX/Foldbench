"""
Lesuite Inference Server

Implements the /predict endpoint: accepts state and images, returns an action vector.
"""

import numpy as np
import json
import cv2
from fastapi import FastAPI, HTTPException, File, UploadFile, Form
from typing import Optional

app = FastAPI()
model = None


def load_model():
    """Load the inference model."""
    class MockModel:
        def predict(self, state, images):
            return np.random.rand(14).astype(np.float32)
    return MockModel()


def preprocess_image(img_bytes):
    img = cv2.imdecode(np.frombuffer(img_bytes, np.uint8), cv2.IMREAD_COLOR)
    return cv2.cvtColor(img, cv2.COLOR_BGR2RGB).astype(np.float32) / 255.0


@app.post("/predict")
async def predict(
    state: str = Form(...),
    task: str = Form(...),
    cam_high: Optional[UploadFile] = File(None),
    cam_left_wrist: Optional[UploadFile] = File(None),
    cam_right_wrist: Optional[UploadFile] = File(None)
):
    try:
        state_array = np.array(json.loads(state), dtype=np.float32)
        images = {}
        for name, file in zip(
            ['cam_high', 'cam_left_wrist', 'cam_right_wrist'],
            [cam_high, cam_left_wrist, cam_right_wrist]
        ):
            if file:
                images[name] = preprocess_image(await file.read())
        action = model.predict(state_array, images)
        return {"action": action.tolist()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def main():
    import uvicorn
    global model
    model = load_model()
    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
