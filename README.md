# 🖐️ Hand Gesture Mouse using OpenCV & MediaPipe

A virtual mouse application built using **Python**, **OpenCV**, and **MediaPipe Hand Landmarker**. This project allows you to control your system's mouse cursor, perform left/right clicks, drag elements, scroll pages, and zoom using hand gestures via your webcam—without touching any physical hardware!

---

## ✨ Key Features

- 🎯 **Smooth Cursor Movement**: Uses exponential moving average smoothing for precise cursor tracking.
- 🖱️ **Gesture Controls**:
  - **Move Cursor**: Index finger up.
  - **Left Click**: Pinch thumb and index finger together.
  - **Right Click**: Bring index and middle finger close together.
  - **Drag & Drop**: Hold thumb and index finger close while moving hand.
  - **Scroll**: Move middle finger up/down while keeping fingers extended.
  - **Both Hands Zoom**: Pinch/expand distance using index fingers of both hands (`Ctrl +` / `Ctrl -`).
- 🪞 **Camera Mirror Fix**: Automatic horizontal flip for natural left/right movement.
- 🛡️ **PyAutoGUI Safety**: Fail-safe mechanisms and boundary checks to prevent accidental script crashes.

---

## 🛠️ Requirements & Prerequisites

Make sure you have **Python 3.8+** installed on your system along with a working webcam.

### Required Libraries
- `opencv-python`
- `mediapipe`
- `pyautogui`

---

## 🚀 Quick Setup & Installation

### 1. Clone the Repository
```bash
git clone [https://github.com/your-username/hand-gesture-mouse.git](https://github.com/your-username/hand-gesture-mouse.git)
cd hand-gesture-mouse
