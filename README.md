# 🔒 Security Camera App

A modern, professional security camera web application built with FastAPI and OpenCV. Features live streaming, motion detection, automatic recording, and a beautiful dark-themed UI.

## ✨ Features

- **📹 Live Camera Feed**: Real-time video streaming from USB webcam
- **🎯 Motion Detection**: Automatic recording when motion is detected
- **📱 Manual Recording**: One-click manual recording button
- **📁 Recordings Management**: View, play, and download recorded clips
- **🎨 Modern UI**: Beautiful dark theme with responsive design
- **📊 Status Monitoring**: Real-time camera and recording status
- **🔔 Notifications**: User-friendly notifications for all actions

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- USB webcam
- Linux/macOS/Windows

### Installation

1. **Clone or download the project**
   ```bash
   # If you have the project files, just navigate to the directory
   cd /path/to/security-camera-app
   ```

2. **Create virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   python run_server.py
   ```

5. **Open your browser**
   ```
   http://localhost:8000
   ```

## 📁 Project Structure

```
security-camera-app/
├── backend/
│   ├── app.py              # FastAPI server
│   ├── camera.py           # Camera and motion detection logic
│   └── __init__.py
├── frontend/
│   ├── index.html          # Main UI
│   ├── style.css           # Modern dark theme
│   └── script.js           # Frontend functionality
├── recordings/             # Saved video clips
├── events/                 # Event logs
├── requirements.txt        # Python dependencies
├── run_server.py           # Launch script
└── README.md              # This file
```

## 🎮 Usage

### Main Interface

1. **Live Feed**: The camera feed displays automatically when the app loads
2. **Record Now**: Click to start a 10-second manual recording
3. **View Recordings**: Click to see all recorded clips
4. **Status Indicator**: Shows connection and recording status

### Recordings Panel

- **Play**: Click to view recordings in a modal player
- **Download**: Click to download recordings to your device
- **Auto-refresh**: Recordings list updates automatically

### Motion Detection

- Automatically records 10-second clips when motion is detected
- Motion indicator appears in the top-right corner
- Events are logged with timestamps

## ⚙️ Configuration

### Camera Settings

Edit `backend/camera.py` to modify:
- Camera index (default: 0)
- Motion detection sensitivity
- Recording duration
- Video quality settings

### Server Settings

Edit `backend/app.py` to modify:
- Server host and port
- CORS settings
- API endpoints

## 🔧 Troubleshooting

### Camera Not Working

1. **Check camera permissions**
   ```bash
   # On Linux, ensure user is in video group
   sudo usermod -a -G video $USER
   ```

2. **Test camera with OpenCV**
   ```python
   import cv2
   cap = cv2.VideoCapture(0)
   print("Camera opened:", cap.isOpened())
   cap.release()
   ```

3. **Try different camera index**
   - Edit `backend/camera.py` line 8: `camera_index: int = 1`

### Dependencies Issues

1. **Reinstall dependencies**
   ```bash
   pip uninstall -r requirements.txt
   pip install -r requirements.txt
   ```

2. **Update pip**
   ```bash
   pip install --upgrade pip
   ```

### Port Already in Use

Change the port in `run_server.py`:
```python
uvicorn.run(app, host="0.0.0.0", port=8001)  # Change 8000 to 8001
```

## 📊 API Endpoints

- `GET /` - Main application page
- `GET /video_feed` - Live video stream
- `POST /record` - Trigger manual recording
- `GET /recordings` - List all recordings
- `GET /recordings/{filename}` - Download specific recording
- `GET /status` - Camera and server status
- `GET /events` - Recent events log

## 🎨 Customization

### Theme Colors

Edit `frontend/style.css` to change colors:
```css
:root {
  --primary-color: #00d4ff;
  --secondary-color: #ff6b6b;
  --background: #1a1a2e;
}
```

### Recording Settings

Edit `backend/camera.py`:
```python
self.motion_threshold = 30  # Motion sensitivity
duration = 10  # Recording duration in seconds
```

## 🔒 Security Notes

- The app runs on `0.0.0.0` by default (accessible from any IP)
- For production use, consider:
  - Adding authentication
  - Using HTTPS
  - Restricting network access
  - Implementing rate limiting

## 🚀 Advanced Features (Future)

- [ ] Object detection (person, vehicle, etc.)
- [ ] Timeline view with filters
- [ ] Email/SMS notifications
- [ ] Cloud storage integration
- [ ] Mobile app companion
- [ ] Multiple camera support
- [ ] Recording scheduling
- [ ] Analytics dashboard

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is open source and available under the MIT License.

## 🆘 Support

If you encounter issues:

1. Check the troubleshooting section above
2. Review the console output for error messages
3. Ensure all dependencies are installed
4. Verify camera permissions and access

---

**Built with ❤️ using FastAPI, OpenCV, and modern web technologies** 