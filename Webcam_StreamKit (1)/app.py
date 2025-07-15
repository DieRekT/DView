from flask import Flask, Response, render_template_string
import cv2
import subprocess

app = Flask(__name__)

HTML_PAGE = """<!DOCTYPE html>
<html>
<head>
    <title>Dual Camera Stream</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { background-color: #000; margin: 0; text-align: center; color: #fff; }
        h1 { font-size: 2em; padding-top: 20px; }
        .stream-container { display: flex; flex-wrap: wrap; justify-content: center; }
        img { width: 45%%; margin: 10px; border: 2px solid #00b894; }
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

def generate_frames(camera):
    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            _, buffer = cv2.imencode('.jpg', frame)
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')

@app.route('/')
def index():
    return render_template_string(HTML_PAGE)

@app.route('/video_feed_1')
def video_feed_1():
    return Response(generate_frames(cap1), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/video_feed_2')
def video_feed_2():
    return Response(generate_frames(cap2), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
