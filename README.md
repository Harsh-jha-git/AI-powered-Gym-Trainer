# 💪 AI Exercise Detector & Trainer

An intelligent fitness tracker powered by Computer Vision. This application uses OpenCV and MediaPipe to automatically detect the exercise you are performing, count your reps, score your form, and provide real-time feedback—all through your webcam or uploaded video files!

---

## ✨ Features Supported

- **Real-Time Classification:** Autodetects which exercise you are doing by analyzing body angles.
- **6 Supported Exercises:**
  - 🏋️ Bicep Curls
  - 🦵 Squats
  - 🧍 Push-ups
  - 🧗 Pull-ups
  - ⏱️ Plank (time-based)
  - 🧎 Abdominal Crunches
- **Dual Input Modes:** Works securely with both live Webcam streaming and pre-recorded Video Files.
- **Form Feedback:** Displays real-time rep counts, current rep stage (e.g., "up" or "down"), form accuracy score, and live form-correction feedback on-screen.

---

## 🚀 Soon to come (In Development)

- **Daily Workout Schedule:** Automatically suggests different exercises (e.g., Leg Day, Push Day) based on the day of the week.
- **Targeted Muscle HUD:** On-screen indicators showing exactly which muscle groups are active.
- **Multiplayer & Leaderboards:** Allow multiple users to log their profiles and compete for high scores.
- **Excel Spreadsheet Export:** Track your entire workout history in a `.csv` or `.xlsx` file for long-term progress reviews.

---

## 💻 How to Run

Make sure your virtual environment is activated, then run the main detector script:

```bash
# Example if using your virtual environment on Windows
.venv\Scripts\python.exe STORAGE\exercise_detector.py
```

### Controls:
- `q` : Quit the session
- `r` : Reset current exercise counters
- `p` : Pause (only when using a video file)

---

## 🛠️ Built With

- **Python 3**
- **OpenCV** - For high-speed image and video manipulation.
- **MediaPipe Pose** - Google's blazing-fast ML framework for high-fidelity body tracking.
