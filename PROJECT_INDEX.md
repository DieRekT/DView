# Project Index: Security Camera App

## Overview
A modern, professional security camera web application built with FastAPI and OpenCV. Features live streaming, motion detection, automatic recording, and a beautiful dark-themed UI.

---

## Project Structure

```
DView/
├── backend/
│   ├── app.py              # FastAPI server for handling routes and camera streams
│   ├── camera.py           # Logic for camera and motion detection
│   ├── __init__.py         # Package initialization file
├── frontend/
│   ├── index.html          # Main UI for the application
│   ├── style.css           # Modern dark theme for the UI
│   ├── script.js           # Frontend functionality for interactivity
├── recordings/             # Directory for saved video clips
├── events/                 # Directory for event logs
├── requirements.txt        # Python dependencies
├── run_server.py           # Script to launch the server
├── README.md               # Project overview and instructions
└── PROJECT_INDEX.md        # This file
```

---

## Backend

### `app.py`
- **Purpose**: FastAPI server for handling routes and camera streams.
- **Enhancements**:
  - Added CORS middleware for cross-origin requests.
  - Improved camera detection logic.
  - Added endpoints for dual-camera streaming.

### `camera.py`
- **Purpose**: Logic for camera and motion detection.
- **Enhancements**:
  - Configurable motion sensitivity and recording duration.

---

## Frontend

### `index.html`
- **Purpose**: Main UI for the application.
- **Enhancements**:
  - Added a footer with app information.
  - Included a modal for displaying recordings.

### `style.css`
- **Purpose**: Modern dark theme for the UI.
- **Enhancements**:
  - Added styles for the modal.
  - Improved compatibility with Safari using `-webkit-backdrop-filter`.

### `script.js`
- **Purpose**: Frontend functionality for interactivity.
- **Enhancements**:
  - Added a function to handle the modal for displaying recordings.
  - Improved error handling for video feed and API calls.

---

## Static Files
- **Directory**: `/static`
- **Purpose**: Serve CSS and JavaScript files.

---

## Recordings
- **Directory**: `/recordings`
- **Purpose**: Store saved video clips.

---

## Events
- **Directory**: `/events`
- **Purpose**: Store event logs.

---

## Configuration

### `requirements.txt`
- **Purpose**: List of Python dependencies.
- **Key Dependencies**:
  - `FastAPI`
  - `Uvicorn`
  - `OpenCV`
  - `Python-Multipart`

### `run_server.py`
- **Purpose**: Script to launch the server.

---

## Documentation

### `README.md`
- **Purpose**: Project overview and instructions.
- **Enhancements**:
  - Updated with new features and usage instructions.

---

## Enhancements Summary
- **Backend**:
  - Added CORS middleware.
  - Improved camera detection logic.
  - Enhanced endpoints for dual-camera streaming.
- **Frontend**:
  - Modernized UI with a dark theme.
  - Added modal functionality for displaying recordings.
  - Improved compatibility and error handling.

---

## Future Improvements
- Add user authentication.
- Implement advanced motion detection algorithms.
- Enable cloud storage for recordings.

---

**Built with ❤️ using FastAPI, OpenCV, and modern web technologies.**
