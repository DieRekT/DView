# DualCam Security Monitor GUI

A Tkinter-based GUI application for dual-camera security monitoring with live previews and motion detection.

## Features

- **Live Camera Previews**: Real-time video feeds from multiple cameras
- **Motion Detection**: Automatic motion detection using frame differencing
- **Visual Alerts**: Red "MOTION" overlay when motion is detected
- **Automatic Recording**: Saves 10-second clips when motion is detected
- **Multi-Camera Support**: Configure and monitor multiple cameras simultaneously
- **Thread-Safe**: Non-blocking GUI with background video processing

## Quick Start

### Option 1: Using the Start Script
```bash
./start-gui.sh
```

### Option 2: Manual Launch
```bash
source venv/bin/activate
cd backend
python gui_with_preview.py
```

## Camera Configuration

The application is pre-configured for:
- **video0**: Brio 100 camera (disabled by default)
- **video2**: Webcam C170 camera (enabled by default)

You can toggle cameras on/off using the checkboxes in the GUI.

## Usage

1. **Launch the Application**: Run the start script or manual command
2. **Select Cameras**: Check/uncheck cameras you want to monitor
3. **Start Monitoring**: Click "Start Monitoring" to begin
4. **Watch for Motion**: Red "MOTION" alerts appear when motion is detected
5. **View Recordings**: Motion clips are saved to `recordings/{camera_id}/motion/`

## File Structure

```
recordings/
├── video0/
│   └── motion/
│       └── motion_YYYYMMDD_HHMMSS.avi
└── video2/
    └── motion/
        └── motion_YYYYMMDD_HHMMSS.avi
```

## Controls

- **Camera Selection**: Checkboxes to enable/disable cameras
- **Mode**: Currently supports "Motion" detection mode
- **Start/Stop**: Control monitoring state
- **Status**: Shows current application status

## Technical Details

- **Motion Detection**: Uses grayscale frame differencing with threshold-based contour detection
- **Recording Format**: AVI files with XVID codec
- **Recording Duration**: 10 seconds per motion event
- **Threading**: Separate threads for video capture, motion detection, and GUI updates
- **Camera Fallback**: Automatically tries alternative camera indices if primary fails

## Troubleshooting

- **No Camera Available**: The GUI will show "No Camera" if cameras can't be opened
- **Performance Issues**: Reduce frame rate or resolution in the code if needed
- **Permission Issues**: Ensure your user has access to video devices (`/dev/video*`)

## Dependencies

All required dependencies are included in `requirements.txt`:
- OpenCV (cv2)
- NumPy
- Pillow (PIL)
- Tkinter (built-in)

✅ Done—ready for review. 