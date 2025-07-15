from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse, HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import os
import json
from datetime import datetime
import cv2
import subprocess
import threading

app = FastAPI(title="Security Camera App", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="../frontend"), name="static")

HTML_PAGE = """<!DOCTYPE html>
<html>
<head>
    <title>Dual Camera Stream</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="stylesheet" href="/static/style.css">
    <script src="/static/script.js" defer></script>
    <style>
        body { background-color: #000; margin: 0; text-align: center; color: #fff; }
        h1 { font-size: 2em; padding-top: 20px; }
        .stream-container { display: flex; flex-wrap: wrap; justify-content: center; }
        img { width: 45%; margin: 10px; border: 2px solid #00b894; }
    </style>
</head>
<body>
    <h1>📷 Dual Camera Live Streams</h1>
    <div class="stream-container">
        <div><img src="/video_feed_1" alt="Brio 100"/></div>
        <div><img src="/video_feed_2" alt="Webcam C170"/></div>
    </div>
</body>
</html>"""

def detect_camera_path(keywords):
    cmd = ["v4l2-ctl", "--list-devices"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    lines = result.stdout.strip().split('\n')

    current_device = None
    matches = {}

    for line in lines:
        if line.strip() == "":
            continue
        if not line.startswith("\t"):
            current_device = line
        else:
            path = line.strip()
            for name in keywords:
                if name.lower() in current_device.lower():
                    matches[name] = path
    return matches

camera_map = detect_camera_path(["Brio", "C170"])
cam1_path = camera_map.get("Brio", "/dev/video2")
cam2_path = camera_map.get("C170", "/dev/video3")

cap1 = cv2.VideoCapture(cam1_path)
cap2 = cv2.VideoCapture(cam2_path)

# Motion detection and recording logic
motion_detected = {"cam1": False, "cam2": False}
recording = {"cam1": False, "cam2": False}

output_dirs = {"cam1": "../recordings/cam1", "cam2": "../recordings/cam2"}
for dir_path in output_dirs.values():
    os.makedirs(dir_path, exist_ok=True)

def detect_motion_and_record(camera, cam_key):
    global motion_detected, recording
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = None

    while True:
        ret, frame = camera.read()
        if not ret:
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (21, 21), 0)

        if not hasattr(detect_motion_and_record, "prev_frame"):
            detect_motion_and_record.prev_frame = gray
            continue

        frame_delta = cv2.absdiff(detect_motion_and_record.prev_frame, gray)
        thresh = cv2.threshold(frame_delta, 25, 255, cv2.THRESH_BINARY)[1]
        thresh = cv2.dilate(thresh, None, iterations=2)
        contours, _ = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        detect_motion_and_record.prev_frame = gray

        motion_detected[cam_key] = any(cv2.contourArea(c) > 5000 for c in contours)

        if motion_detected[cam_key] and not recording[cam_key]:
            recording[cam_key] = True
            filename = os.path.join(output_dirs[cam_key], f"motion_{datetime.now().strftime('%Y%m%d_%H%M%S')}.avi")
            out = cv2.VideoWriter(filename, fourcc, 20.0, (frame.shape[1], frame.shape[0]))

        if recording[cam_key]:
            out.write(frame)

        if not motion_detected[cam_key] and recording[cam_key]:
            recording[cam_key] = False
            out.release()

# Start motion detection threads
threading.Thread(target=detect_motion_and_record, args=(cap1, "cam1"), daemon=True).start()
threading.Thread(target=detect_motion_and_record, args=(cap2, "cam2"), daemon=True).start()

def generate_frames(camera):
    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            _, buffer = cv2.imencode('.jpg', frame)
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')

@app.get("/")
async def index():
    return HTMLResponse(content=HTML_PAGE)

@app.get("/video_feed_1")
async def video_feed_1():
    return StreamingResponse(generate_frames(cap1), media_type='multipart/x-mixed-replace; boundary=frame')

@app.get("/video_feed_2")
async def video_feed_2():
    return StreamingResponse(generate_frames(cap2), media_type='multipart/x-mixed-replace; boundary=frame')

@app.post("/record")
async def manual_record(cam: str):
    if cam not in ["cam1", "cam2"]:
        raise HTTPException(status_code=400, detail="Invalid camera key")

    global recording
    recording[cam] = True
    return {"message": f"Manual recording started for {cam}"}

@app.post("/toggle_motion")
async def toggle_motion(cam: str):
    if cam not in ["cam1", "cam2"]:
        raise HTTPException(status_code=400, detail="Invalid camera key")

    global motion_detected
    motion_detected[cam] = not motion_detected[cam]
    return {"message": f"Motion detection toggled for {cam}", "status": motion_detected[cam]}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)