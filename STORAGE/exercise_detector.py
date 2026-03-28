"""
AI Exercise Detector & Trainer
================================
Continuously detects which exercise you're performing and runs
the appropriate tracker with rep counting, scoring, and feedback.

Supported exercises:
  - Bicep Curls
  - Squats
  - Push-ups
  - Pull-ups
  - Plank (time-based)
  - Abdominal Crunches

Controls:
  q - Quit
  r - Reset counters for current exercise
  m - Mute / Unmute audio coaching

Usage:
  .venv\\Scripts\\python.exe STORAGE\\exercise_detector.py
"""

import cv2
import mediapipe as mp
import numpy as np
import sys
import os
import time
import traceback
import tkinter as tk
from tkinter import filedialog
from collections import deque

# Add STORAGE to path so we can import angle_utils
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import session_tracker
from angle_utils import calculate_angle, get_coords, body_orientation
from audio_manager import AudioManager
from exercises import (
    CurlExercise,
    SquatExercise,
    PushupExercise,
    PullupExercise,
    PlankExercise,
    CrunchExercise,
)
# --- AI Coach removed ---

# -----------------------------------------
# MediaPipe Setup
# -----------------------------------------
mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils
PL = mp_pose.PoseLandmark

pose = mp_pose.Pose(
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5,
)


import argparse

# -----------------------------------------
# Input Source Selection (via GUI or CLI)
# -----------------------------------------
parser = argparse.ArgumentParser()
parser.add_argument("--user", type=str, help="Username")
parser.add_argument("--source", type=str, default="webcam", help="webcam or path to video")
parser.add_argument("--voice", type=str, default="male", help="male or female")
parser.add_argument("--no-gui", action="store_true", help="Launch without GUI")
args, unknown = parser.parse_known_args()

if args.no_gui and args.user:
    username = args.user
    voice_gender = args.voice
    if args.source == "webcam":
        cap = cv2.VideoCapture(0)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        source_desc = "Webcam"
        use_mirror = True
    else:
        import os
        cap = cv2.VideoCapture(args.source)
        if not cap.isOpened():
            sys.exit(1)
        source_desc = os.path.basename(args.source)
        use_mirror = False
else:
    from gui_launcher import launch_setup_gui
    try:
        cap, source_desc, use_mirror, username, voice_gender = launch_setup_gui()
    except Exception as e:
        print(f"Error launching setup: {e}")
        sys.exit(1)

ai_coach = None

# -----------------------------------------
# Audio Coach Setup
# -----------------------------------------
audio_mgr = AudioManager(voice_gender=voice_gender)

# Display size
DISPLAY_W, DISPLAY_H = 1280, 720

# -----------------------------------------
# Exercise Instances
# -----------------------------------------
exercises = {
    'curls': CurlExercise(),
    'squats': SquatExercise(),
    'pushups': PushupExercise(),
    'pullups': PullupExercise(),
    'plank': PlankExercise(),
    'crunches': CrunchExercise(),
}

# Attach audio manager and real-time logger to all exercises
def real_time_logger(ex_name, val, score):
    session_tracker.log_session(username, ex_name, val, score)

for ex in exercises.values():
    ex.set_audio_manager(audio_mgr)
    ex.log_callback = real_time_logger

current_exercise = None
current_exercise_key = None

# Detection buffer — need N consistent detections before switching
DETECTION_BUFFER_SIZE = 15
detection_history = deque(maxlen=DETECTION_BUFFER_SIZE)

# Cooldown after switch (don't switch too fast)
last_switch_time = 0
SWITCH_COOLDOWN = 2.0  # seconds

# Video playback state
paused = False

# AI Coaching tracking
last_ai_tip_time = time.time()
AI_TIP_INTERVAL = 10.0  # seconds
current_ai_tip = "AI Coach is analyzing your form..."


def classify_exercise(landmarks):
    """
    Classify the exercise being performed based on body pose angles.
    
    Returns: exercise key string or None
    """
    try:
        # --- Extract all key landmarks ---
        nose = get_coords(landmarks, PL.NOSE)

        l_shoulder = get_coords(landmarks, PL.LEFT_SHOULDER)
        r_shoulder = get_coords(landmarks, PL.RIGHT_SHOULDER)
        l_elbow = get_coords(landmarks, PL.LEFT_ELBOW)
        r_elbow = get_coords(landmarks, PL.RIGHT_ELBOW)
        l_wrist = get_coords(landmarks, PL.LEFT_WRIST)
        r_wrist = get_coords(landmarks, PL.RIGHT_WRIST)

        l_hip = get_coords(landmarks, PL.LEFT_HIP)
        r_hip = get_coords(landmarks, PL.RIGHT_HIP)
        l_knee = get_coords(landmarks, PL.LEFT_KNEE)
        r_knee = get_coords(landmarks, PL.RIGHT_KNEE)
        l_ankle = get_coords(landmarks, PL.LEFT_ANKLE)
        r_ankle = get_coords(landmarks, PL.RIGHT_ANKLE)

        # --- Compute key angles ---
        l_elbow_angle = calculate_angle(l_shoulder, l_elbow, l_wrist)
        r_elbow_angle = calculate_angle(r_shoulder, r_elbow, r_wrist)
        elbow_angle = min(l_elbow_angle, r_elbow_angle)

        l_knee_angle = calculate_angle(l_hip, l_knee, l_ankle)
        r_knee_angle = calculate_angle(r_hip, r_knee, r_ankle)
        knee_angle = (l_knee_angle + r_knee_angle) / 2

        # Body orientation
        orientation = body_orientation(landmarks)

        # Shoulder-hip vertical difference
        avg_shoulder_y = (l_shoulder[1] + r_shoulder[1]) / 2
        avg_hip_y = (l_hip[1] + r_hip[1]) / 2

        # Wrist position relative to shoulder
        avg_wrist_y = (l_wrist[1] + r_wrist[1]) / 2
        avg_elbow_y = (l_elbow[1] + r_elbow[1]) / 2
        wrists_above_shoulders = avg_wrist_y < avg_shoulder_y - 0.05
        elbows_above_shoulders = avg_elbow_y < avg_shoulder_y - 0.03

        # Body angle (shoulder → hip → ankle)
        body_angle = calculate_angle(l_shoulder, l_hip, l_ankle)

        # Crunch angle (shoulder → hip → knee)
        shoulder_mid = [(l_shoulder[0] + r_shoulder[0]) / 2,
                        (l_shoulder[1] + r_shoulder[1]) / 2]
        hip_mid = [(l_hip[0] + r_hip[0]) / 2,
                   (l_hip[1] + r_hip[1]) / 2]
        knee_mid = [(l_knee[0] + r_knee[0]) / 2,
                    (l_knee[1] + r_knee[1]) / 2]
        crunch_angle = calculate_angle(shoulder_mid, hip_mid, knee_mid)

        # --- Classification logic ---

        # PULL-UPS: standing/hanging, wrists AND elbows above shoulders (arms fully overhead)
        if wrists_above_shoulders and elbows_above_shoulders and orientation == 'standing':
            return 'pullups'

        # PUSH-UPS: body horizontal, arms involved (not totally straight)
        if orientation == 'horizontal' and body_angle > 140:
            if avg_shoulder_y < avg_hip_y + 0.08:
                if elbow_angle < 140:
                    return 'pushups'
                else:
                    return 'plank'

        # PLANK: body horizontal, arms straight
        if orientation == 'horizontal':
            if body_angle > 150 and abs(l_shoulder[1] - l_hip[1]) < 0.12:
                return 'plank'

        # CRUNCHES: lying position, knees bent
        if orientation == 'horizontal':
            if l_knee_angle < 130 and crunch_angle < 150:
                return 'crunches'

        # SQUATS: standing, knees bending
        if orientation == 'standing' and knee_angle < 150:
            return 'squats'

        # CURLS: standing, elbow bending (no squat)
        if orientation == 'standing' and knee_angle > 150 and elbow_angle < 140:
            return 'curls'

        return None

    except Exception:
        return None


# -----------------------------------------
# Main Loop
# -----------------------------------------
print()
print("  Starting exercise detection...")
print(f"  Source: {source_desc}")
print(f"  Voice: {voice_gender.capitalize()} | Audio: ON")
print("  Supported: Curls, Squats, Push-ups, Pull-ups, Plank, Crunches")
print("  Press 'q' to quit  |  'r' reset  |  'm' mute/unmute  |  'p' pause (video)")
print("=" * 50)

fps_time = time.time()
fps = 0

while True:
    if not paused:
        ret, frame = cap.read()
        if not ret:
            # For video files: we've reached the end
            if source_desc != "Webcam":
                print("\n  >> Video ended.")
                # Wait for user to press q
                while True:
                    key = cv2.waitKey(100) & 0xFF
                    if key == ord('q'):
                        break
            break

        # Flip for mirror effect (webcam only)
        if use_mirror:
            frame = cv2.flip(frame, 1)

        # Process pose
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = pose.process(rgb_frame)

        # Calculate FPS
        current_time = time.time()
        fps = 1.0 / max(current_time - fps_time, 0.001)
        fps_time = current_time

        if result.pose_landmarks:
            # Draw pose skeleton
            mp_drawing.draw_landmarks(
                frame, result.pose_landmarks, mp_pose.POSE_CONNECTIONS,
                mp_drawing.DrawingSpec(color=(100, 100, 100), thickness=2, circle_radius=2),
                mp_drawing.DrawingSpec(color=(200, 200, 200), thickness=2),
            )

            landmarks = result.pose_landmarks.landmark

            # --- Detect exercise ---
            detected = classify_exercise(landmarks)
            detection_history.append(detected)

            # Check if detection is consistent
            if len(detection_history) == DETECTION_BUFFER_SIZE:
                from collections import Counter
                counts = Counter(detection_history)
                most_common, count = counts.most_common(1)[0]

                if (most_common is not None
                        and count >= DETECTION_BUFFER_SIZE * 0.8
                        and (current_time - last_switch_time) > SWITCH_COOLDOWN):
                    
                    # Only switch if it's a NEW exercise
                    if most_common != current_exercise_key:
                        current_exercise_key = most_common
                        current_exercise = exercises[current_exercise_key]
                        # Don't reset score/counter on auto-switch!
                        current_exercise.reset(hard_reset=False)
                        last_switch_time = current_time
                        detection_history.clear()
                        print(f"  >> Detected: {current_exercise.NAME}")

                        # Audio: announce the new exercise
                        audio_mgr.play_exercise_switch_sound()
                        audio_mgr.announce_exercise(current_exercise.NAME)

            # --- Run active exercise tracker ---
            if current_exercise is not None:
                try:
                    frame = current_exercise.process(landmarks, frame)
                    current_exercise._trigger_audio()  # Audio coaching
                    frame = current_exercise.draw_ui(frame)
                except Exception as e:
                    print(f"\n  [ERROR] in {current_exercise_key} process: {e}")
                    traceback.print_exc()

            # --- Periodic AI Coaching removed ---

        # --- Status bars ---
        h, w = frame.shape[:2]

        # Bottom bar
        cv2.rectangle(frame, (0, h - 50), (w, h), (30, 30, 30), -1)

        if current_exercise_key:
            status = f"Active: {exercises[current_exercise_key].NAME}"
            cv2.putText(frame, status, (10, h - 18),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        else:
            cv2.putText(frame, "Detecting exercise... Start moving!", (10, h - 18),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 200, 255), 2)

        # Source label
        cv2.putText(frame, f"SRC: {source_desc}", (10, h - 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.45, (150, 150, 150), 1)

        # Video progress bar (for video files)
        if source_desc != "Webcam":
            total_frames = cap.get(cv2.CAP_PROP_FRAME_COUNT)
            current_frame = cap.get(cv2.CAP_PROP_POS_FRAMES)
            if total_frames > 0:
                progress = current_frame / total_frames
                bar_y = h - 55
                bar_w = w - 20
                cv2.rectangle(frame, (10, bar_y), (10 + bar_w, bar_y + 5), (80, 80, 80), -1)
                cv2.rectangle(frame, (10, bar_y), (10 + int(bar_w * progress), bar_y + 5), (0, 200, 255), -1)

        # FPS counter
        cv2.putText(frame, f"FPS: {int(fps)}", (w - 150, h - 18),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (150, 150, 150), 1)

        # --- AI Coaching tooltip removed ---

        # Controls hint
        controls = "Q: Quit | R: Reset | M: Mute | P: Pause" if source_desc != "Webcam" else "Q: Quit | R: Reset | M: Mute"
        cv2.putText(frame, controls, (w - 480, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (150, 150, 150), 1)

        # Save last frame for paused display
        last_frame = frame.copy()

    else:
        # Paused — show last frame with PAUSED overlay
        frame = last_frame.copy()
        h, w = frame.shape[:2]
        overlay = frame.copy()
        cv2.rectangle(overlay, (w // 2 - 120, h // 2 - 30), (w // 2 + 120, h // 2 + 30), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.6, frame, 0.4, 0, frame)
        cv2.putText(frame, "PAUSED", (w // 2 - 80, h // 2 + 12),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 200, 255), 3)

    # --- Resize and display ---
    display_frame = cv2.resize(frame, (DISPLAY_W, DISPLAY_H))
    cv2.imshow("AI Exercise Detector & Trainer", display_frame)

    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break
    elif key == ord('r'):
        if current_exercise:
            if getattr(current_exercise, 'counter', 0) > 0:
                session_tracker.log_session(username, current_exercise.NAME, current_exercise.counter, current_exercise.score)
            current_exercise.reset(hard_reset=True)
            print("  >> Counters and Score reset!")
    elif key == ord('m'):
        muted = audio_mgr.toggle_mute()
        state = 'MUTED' if muted else 'UNMUTED'
        print(f"  >> Audio: {state}")
    elif key == ord('p') and source_desc != "Webcam":
        paused = not paused
        print(f"  >> {'Paused' if paused else 'Resumed'}")

# Cleanup
if current_exercise and getattr(current_exercise, 'counter', 0) > 0:
    session_tracker.log_session(username, current_exercise.NAME, current_exercise.counter, current_exercise.score)

audio_mgr.shutdown()
cap.release()
cv2.destroyAllWindows()

print("\nSession ended. Great workout! 💪")
session_tracker.print_leaderboard()
