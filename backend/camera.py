import cv2
import numpy as np
import time
import os
import json
from datetime import datetime
from typing import Generator, Tuple
import threading
import queue

class SecurityCamera:
    def __init__(self, camera_index: int = 3):
        self.camera_index = camera_index
        self.cap = None
        self.is_recording = False
        self.motion_detected = False
        self.last_frame = None
        self.motion_threshold = 30
        self.recordings_dir = "../recordings"
        self.events_file = "../events/events.json"
        
        # Ensure directories exist
        os.makedirs(self.recordings_dir, exist_ok=True)
        os.makedirs(os.path.dirname(self.events_file), exist_ok=True)
        
        # Initialize camera
        self._init_camera()
    
    def _init_camera(self):
        """Initialize the camera capture"""
        self.cap = cv2.VideoCapture(self.camera_index)
        if not self.cap.isOpened():
            # Try alternative camera indices
            for i in range(1, 4):
                self.cap = cv2.VideoCapture(i)
                if self.cap.isOpened():
                    self.camera_index = i
                    break
            
            if not self.cap.isOpened():
                # Create a dummy frame if no camera is available
                self.cap = None
                return
        
        # Set camera properties for better performance
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.cap.set(cv2.CAP_PROP_FPS, 30)
    
    def detect_motion(self, frame: np.ndarray) -> bool:
        """Detect motion in the current frame"""
        if self.last_frame is None:
            self.last_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            return False
        
        # Convert to grayscale for motion detection
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (21, 21), 0)
        
        # Calculate difference
        frame_delta = cv2.absdiff(self.last_frame, gray)
        thresh = cv2.threshold(frame_delta, 25, 255, cv2.THRESH_BINARY)[1]
        
        # Dilate to fill in holes
        kernel = np.ones((5,5), np.uint8)
        thresh = cv2.dilate(thresh, kernel, iterations=2)
        
        # Find contours
        contours, _ = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Check for significant motion
        motion_detected = False
        for contour in contours:
            if cv2.contourArea(contour) > self.motion_threshold:
                motion_detected = True
                break
        
        self.last_frame = gray
        return motion_detected
    
    def _create_dummy_frame(self) -> np.ndarray:
        """Create a dummy frame when no camera is available"""
        # Create a 640x480 frame with a message
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        
        # Add text to the frame
        font = cv2.FONT_HERSHEY_SIMPLEX
        text = "No Camera Available"
        text_size = cv2.getTextSize(text, font, 1, 2)[0]
        text_x = (640 - text_size[0]) // 2
        text_y = (480 + text_size[1]) // 2
        
        cv2.putText(frame, text, (text_x, text_y), font, 1, (255, 255, 255), 2)
        
        # Add a camera icon or placeholder
        cv2.rectangle(frame, (280, 200), (360, 280), (100, 100, 100), 2)
        cv2.circle(frame, (320, 240), 30, (100, 100, 100), 2)
        
        return frame
    
    def generate_frames(self) -> Generator[bytes, None, None]:
        """Generate MJPEG frames for streaming"""
        while True:
            if self.cap is None:
                # Generate a dummy frame when no camera is available
                frame = self._create_dummy_frame()
                motion = False
            elif not self.cap.isOpened():
                break
            else:
                ret, frame = self.cap.read()
                if not ret:
                    break
                
                # Detect motion
                motion = self.detect_motion(frame)
                if motion and not self.motion_detected:
                    self.motion_detected = True
                    self._log_event("motion_detected")
                    # Start recording if motion detected
                    threading.Thread(target=self._record_motion_clip, args=(frame,)).start()
                elif not motion:
                    self.motion_detected = False
            
            # Encode frame as JPEG
            ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
            if not ret:
                continue
            
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
    
    def manual_record(self) -> str:
        """Trigger manual recording"""
        if self.is_recording:
            return "Already recording"
        
        self._log_event("manual_record")
        threading.Thread(target=self._record_clip, args=("manual",)).start()
        return "Recording started"
    
    def _record_motion_clip(self, frame: np.ndarray):
        """Record a clip when motion is detected"""
        self._record_clip("motion")
    
    def _record_clip(self, trigger_type: str):
        """Record a 10-second video clip"""
        if self.is_recording:
            return
        
        # Don't record if no camera is available
        if self.cap is None:
            self._log_event(f"{trigger_type}_no_camera")
            return
        
        self.is_recording = True
        
        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{trigger_type}_{timestamp}.mp4"
        filepath = os.path.join(self.recordings_dir, filename)
        
        # Set up video writer
        fourcc = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')
        out = cv2.VideoWriter(filepath, fourcc, 30.0, (640, 480))
        
        start_time = time.time()
        duration = 10  # 10 seconds
        
        try:
            while time.time() - start_time < duration:
                if self.cap and self.cap.isOpened():
                    ret, frame = self.cap.read()
                    if ret:
                        out.write(frame)
                time.sleep(0.033)  # ~30 FPS
        finally:
            out.release()
            self.is_recording = False
    
    def _log_event(self, event_type: str):
        """Log events to JSON file"""
        event = {
            "timestamp": datetime.now().isoformat(),
            "type": event_type
        }
        
        events = []
        if os.path.exists(self.events_file):
            try:
                with open(self.events_file, 'r') as f:
                    events = json.load(f)
            except:
                events = []
        
        events.append(event)
        
        with open(self.events_file, 'w') as f:
            json.dump(events, f, indent=2)
    
    def get_recordings(self) -> list:
        """Get list of all recordings"""
        recordings = []
        if os.path.exists(self.recordings_dir):
            for filename in os.listdir(self.recordings_dir):
                if filename.endswith('.mp4'):
                    filepath = os.path.join(self.recordings_dir, filename)
                    stat = os.stat(filepath)
                    recordings.append({
                        "filename": filename,
                        "size": stat.st_size,
                        "created": datetime.fromtimestamp(stat.st_ctime).isoformat()
                    })
        
        # Sort by creation time (newest first)
        recordings.sort(key=lambda x: x["created"], reverse=True)
        return recordings
    
    def __del__(self):
        """Cleanup camera resources"""
        if self.cap:
            self.cap.release()

# Global camera instance
camera = None

def get_camera() -> SecurityCamera:
    """Get or create camera instance"""
    global camera
    if camera is None:
        camera = SecurityCamera()
    return camera 
