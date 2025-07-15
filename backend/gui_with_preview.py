"""
Tkinter-based GUI for dual-camera security monitor app.

Features:
- Live video previews from selected cameras (video0, video2)
- Motion detection using frame differencing
- Red MOTION alert overlay on preview
- Save motion-detected clips to folders per camera
- Thread-safe GUI updates
- Clean exit with camera release
- Car counting and logging
"""

import tkinter as tk
from tkinter import ttk, messagebox
import cv2
import numpy as np
import threading
import time
import os
from datetime import datetime
from PIL import Image, ImageTk
import queue
import csv

class SecurityCameraGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("DualCam Security Monitor")
        self.root.geometry("1200x800")
        self.root.configure(bg='#2b2b2b')
        
        # Camera settings
        self.cameras = {
            'video2': {'index': 2, 'name': 'Brio 100', 'enabled': True},
            'video3': {'index': 3, 'name': 'Webcam C170', 'enabled': True}
        }
        
        # Video capture objects
        self.caps = {}
        self.frames = {}
        self.last_frames = {}
        self.motion_detected = {}
        self.recording = {}
        
        # Threading
        self.running = False
        self.update_queue = queue.Queue()
        self.recording_threads = {}
        
        # Recording settings
        self.recordings_dir = "../recordings"
        self.motion_threshold = 30
        self.recording_duration = 10  # seconds
        
        # Car settings
        self.car_count = 0
        self.car_log_file = "car_log.csv"
        
        # Create directories
        for cam_id in self.cameras:
            cam_dir = os.path.join(self.recordings_dir, cam_id, "motion")
            os.makedirs(cam_dir, exist_ok=True)
        
        self.setup_gui()
        self.setup_cameras()
        self.setup_car_logging()
        
    def setup_gui(self):
        """Setup the GUI layout"""
        # Main frame
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Control panel (top)
        control_frame = ttk.LabelFrame(main_frame, text="Controls", padding=10)
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Camera selection
        camera_frame = ttk.Frame(control_frame)
        camera_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(camera_frame, text="Cameras:").pack(side=tk.LEFT)
        
        self.camera_vars = {}
        for cam_id, cam_info in self.cameras.items():
            var = tk.BooleanVar(value=cam_info['enabled'])
            self.camera_vars[cam_id] = var
            cb = ttk.Checkbutton(
                camera_frame, 
                text=f"{cam_info['name']} ({cam_id})",
                variable=var,
                command=self.on_camera_toggle
            )
            cb.pack(side=tk.LEFT, padx=(10, 0))
        
        # Mode and controls
        mode_frame = ttk.Frame(control_frame)
        mode_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(mode_frame, text="Mode:").pack(side=tk.LEFT)
        self.mode_var = tk.StringVar(value="Motion")
        mode_combo = ttk.Combobox(
            mode_frame, 
            textvariable=self.mode_var,
            values=["Motion"],
            state="readonly",
            width=15
        )
        mode_combo.pack(side=tk.LEFT, padx=(10, 0))
        
        # Start/Stop buttons
        button_frame = ttk.Frame(control_frame)
        button_frame.pack(fill=tk.X)
        
        self.start_button = ttk.Button(
            button_frame, 
            text="Start Monitoring", 
            command=self.start_monitoring,
            style="Accent.TButton"
        )
        self.start_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.stop_button = ttk.Button(
            button_frame, 
            text="Stop Monitoring", 
            command=self.stop_monitoring,
            state=tk.DISABLED
        )
        self.stop_button.pack(side=tk.LEFT)
        
        # Status
        self.status_var = tk.StringVar(value="Ready")
        status_label = ttk.Label(control_frame, textvariable=self.status_var)
        status_label.pack(side=tk.RIGHT)
        
        # Video preview frame
        preview_frame = ttk.LabelFrame(main_frame, text="Live Preview", padding=10, style="Modern.TLabelframe")
        preview_frame.pack(fill=tk.BOTH, expand=True)

        # Create video labels
        self.video_labels = {}
        for i, (cam_id, cam_info) in enumerate(self.cameras.items()):
            frame = ttk.Frame(preview_frame, style="Modern.TFrame")
            frame.grid(row=0, column=i, padx=10, pady=10, sticky="nsew")

            # Camera label
            ttk.Label(frame, text=cam_info['name'], font=('Helvetica', 14, 'bold'), anchor="center").pack(pady=5)

            # Video display
            video_label = ttk.Label(frame, text="No Camera", relief=tk.RIDGE, borderwidth=3, background="#f0f0f0")
            video_label.pack(pady=10, ipadx=20, ipady=10)
            self.video_labels[cam_id] = video_label

            # Status indicators
            status_frame = ttk.Frame(frame, style="Modern.TFrame")
            status_frame.pack(fill=tk.X, pady=5)

            # Motion indicator
            motion_label = ttk.Label(status_frame, text="MOTION", foreground="red", font=('Helvetica', 12, 'bold'))
            motion_label.pack(side=tk.LEFT, padx=5)
            self.motion_labels = getattr(self, 'motion_labels', {})
            self.motion_labels[cam_id] = motion_label
            motion_label.pack_forget()  # Hide initially

            # Recording indicator
            recording_label = ttk.Label(status_frame, text="REC", foreground="green", font=('Helvetica', 12, 'bold'))
            recording_label.pack(side=tk.RIGHT, padx=5)
            self.recording_labels = getattr(self, 'recording_labels', {})
            self.recording_labels[cam_id] = recording_label
            recording_label.pack_forget()  # Hide initially

        # Configure grid weights
        for i in range(len(self.cameras)):
            preview_frame.grid_columnconfigure(i, weight=1)
        
    def setup_cameras(self):
        """Initialize camera captures"""
        for cam_id, cam_info in self.cameras.items():
            if cam_info['enabled']:
                self.init_camera(cam_id)
    
    def init_camera(self, cam_id):
        """Initialize a specific camera"""
        cam_info = self.cameras[cam_id]
        cap = cv2.VideoCapture(cam_info['index'])

        if not cap.isOpened():
            # Try alternative indices
            for i in range(4):
                if i != cam_info['index']:
                    cap = cv2.VideoCapture(i)
                    if cap.isOpened():
                        cam_info['index'] = i
                        break

            if not cap.isOpened():
                print(f"Warning: Could not open camera {cam_id}")
                self.cameras[cam_id]['enabled'] = False  # Disable camera
                return

        # Set camera properties
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        cap.set(cv2.CAP_PROP_FPS, 30)
        
        self.caps[cam_id] = cap
        self.frames[cam_id] = None
        self.last_frames[cam_id] = None
        self.motion_detected[cam_id] = False
        self.recording[cam_id] = False
        
        print(f"Camera {cam_id} initialized successfully")
    
    def on_camera_toggle(self):
        """Handle camera checkbox toggles"""
        for cam_id, var in self.camera_vars.items():
            enabled = var.get()
            if enabled and cam_id not in self.caps:
                self.init_camera(cam_id)
            elif not enabled and cam_id in self.caps:
                self.release_camera(cam_id)
    
    def release_camera(self, cam_id):
        """Release camera resources"""
        if cam_id in self.caps:
            self.caps[cam_id].release()
            del self.caps[cam_id]
            del self.frames[cam_id]
            del self.last_frames[cam_id]
            del self.motion_detected[cam_id]
            del self.recording[cam_id]
    
    def detect_motion(self, cam_id, frame):
        """Detect motion in camera frame"""
        if cam_id not in self.last_frames or self.last_frames[cam_id] is None:
            self.last_frames[cam_id] = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            return False
        
        # Convert to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (21, 21), 0)
        
        # Calculate difference
        frame_delta = cv2.absdiff(self.last_frames[cam_id], gray)
        thresh = cv2.threshold(frame_delta, 25, 255, cv2.THRESH_BINARY)[1]
        
        # Dilate to fill holes
        kernel = np.ones((5, 5), np.uint8)
        thresh = cv2.dilate(thresh, kernel, iterations=2)
        
        # Find contours
        contours, _ = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Check for significant motion
        motion_detected = False
        for contour in contours:
            if cv2.contourArea(contour) > self.motion_threshold:
                motion_detected = True
                break
        
        self.last_frames[cam_id] = gray
        return motion_detected
    
    def setup_car_logging(self):
        """Initialize car logging file"""
        if not os.path.exists(self.car_log_file):
            with open(self.car_log_file, mode='w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(["Timestamp", "Direction"])

    def log_car(self, direction):
        """Log car entry with direction"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(self.car_log_file, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([timestamp, direction])
        self.car_count += 1
        self.update_car_count_display()

    def update_car_count_display(self):
        """Update car count display in the GUI"""
        self.car_count_var.set(f"Cars: {self.car_count}")

    def start_monitoring(self):
        """Start the monitoring process"""
        self.running = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.status_var.set("Monitoring...")
        
        # Start video update thread
        self.video_thread = threading.Thread(target=self.video_update_loop, daemon=True)
        self.video_thread.start()
        
        # Start GUI update thread
        self.gui_thread = threading.Thread(target=self.gui_update_loop, daemon=True)
        self.gui_thread.start()
    
    def stop_monitoring(self):
        """Stop the monitoring process"""
        self.running = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.status_var.set("Stopped")
        
        # Hide all indicators
        for cam_id in self.cameras:
            if cam_id in self.motion_labels:
                self.motion_labels[cam_id].pack_forget()
            if cam_id in self.recording_labels:
                self.recording_labels[cam_id].pack_forget()
    
    def video_update_loop(self):
        """Main video processing loop"""
        while self.running:
            for cam_id, cam_info in self.cameras.items():
                if not self.camera_vars[cam_id].get():
                    continue

                if cam_id not in self.caps:
                    continue

                cap = self.caps[cam_id]
                if not cap.isOpened():
                    continue

                ret, frame = cap.read()
                if not ret:
                    continue

                # Detect motion
                motion = self.detect_motion(cam_id, frame)

                # Handle motion detection
                if motion and not self.motion_detected[cam_id]:
                    self.motion_detected[cam_id] = True
                    self.start_motion_recording(cam_id)

                elif not motion:
                    self.motion_detected[cam_id] = False

                # Detect cars
                self.detect_cars(frame)

                # Convert frame for display
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                # Add motion overlay if detected
                if motion:
                    cv2.rectangle(frame_rgb, (10, 10), (200, 50), (255, 0, 0), -1)
                    cv2.putText(frame_rgb, "MOTION", (20, 35), 
                              cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

                # Resize for display
                frame_resized = cv2.resize(frame_rgb, (320, 240))

                # Convert to PIL Image
                pil_image = Image.fromarray(frame_resized)
                photo = ImageTk.PhotoImage(pil_image)

                # Queue for GUI update
                self.update_queue.put((cam_id, photo, motion, self.recording[cam_id]))

            time.sleep(0.033)  # ~30 FPS
    
    def gui_update_loop(self):
        """Update GUI elements from queue"""
        while self.running:
            try:
                cam_id, photo, motion, recording = self.update_queue.get(timeout=0.1)
                
                # Update video display
                if cam_id in self.video_labels:
                    self.video_labels[cam_id].configure(image=photo)
                    self.video_labels[cam_id].image = photo  # Keep reference
                
                # Update motion indicator
                if cam_id in self.motion_labels:
                    if motion:
                        self.motion_labels[cam_id].pack(side=tk.LEFT)
                    else:
                        self.motion_labels[cam_id].pack_forget()
                
                # Update recording indicator
                if cam_id in self.recording_labels:
                    if recording:
                        self.recording_labels[cam_id].pack(side=tk.RIGHT)
                    else:
                        self.recording_labels[cam_id].pack_forget()
                
            except queue.Empty:
                continue
    
    def start_motion_recording(self, cam_id):
        """Start recording when motion is detected"""
        if self.recording[cam_id]:
            return
        
        # Start recording in separate thread
        thread = threading.Thread(target=self.record_motion_clip, args=(cam_id,), daemon=True)
        thread.start()
        self.recording_threads[cam_id] = thread
    
    def record_motion_clip(self, cam_id):
        """Record a motion-triggered video clip"""
        if cam_id not in self.caps or not self.caps[cam_id].isOpened():
            return
        
        self.recording[cam_id] = True
        
        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"motion_{timestamp}.avi"
        cam_dir = os.path.join(self.recordings_dir, cam_id, "motion")
        filepath = os.path.join(cam_dir, filename)
        
        # Set up video writer
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        out = cv2.VideoWriter(filepath, fourcc, 30.0, (640, 480))
        
        start_time = time.time()
        
        try:
            while time.time() - start_time < self.recording_duration:
                if not self.running:
                    break
                
                ret, frame = self.caps[cam_id].read()
                if ret:
                    out.write(frame)
                time.sleep(0.033)
        finally:
            out.release()
            self.recording[cam_id] = False
    
    def detect_cars(self, frame):
        """Detect cars in the frame and log their direction"""
        # Placeholder for car detection logic
        # Simulate car detection with random direction
        import random
        directions = ["North", "South", "East", "West"]
        detected = random.choice([True, False])
        if detected:
            direction = random.choice(directions)
            self.log_car(direction)

    def on_closing(self):
        """Handle application closing"""
        self.running = False
        
        # Release all cameras
        for cam_id in list(self.caps.keys()):
            self.release_camera(cam_id)
        
        self.root.destroy()

def main():
    """Main application entry point"""
    root = tk.Tk()
    
    # Configure style
    style = ttk.Style()
    style.theme_use('clam')
    
    # Create application
    app = SecurityCameraGUI(root)
    
    # Set up closing handler
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    
    # Start GUI
    root.mainloop()

if __name__ == "__main__":
    main()
