import cv2
import numpy as np
import mediapipe as mp
from .base import BaseExercise
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from angle_utils import calculate_angle, get_coords

mp_pose = mp.solutions.pose
PL = mp_pose.PoseLandmark


class CurlExercise(BaseExercise):
    """Bicep Curl tracker — counts reps based on elbow angle with form checks."""

    NAME = "BICEP CURLS"
    COLOR = (0, 200, 255)  # Orange

    def __init__(self):
        super().__init__()
        # Track each arm independently
        self.l_stage = None
        self.r_stage = None
        # Shoulder stability tracking
        self._prev_l_shoulder_y = None
        self._prev_r_shoulder_y = None

    def reset(self):
        super().reset()
        self.l_stage = None
        self.r_stage = None
        self._prev_l_shoulder_y = None
        self._prev_r_shoulder_y = None

    def process(self, landmarks, frame):
        # --- Get coordinates for both arms ---
        l_shoulder = get_coords(landmarks, PL.LEFT_SHOULDER)
        l_elbow = get_coords(landmarks, PL.LEFT_ELBOW)
        l_wrist = get_coords(landmarks, PL.LEFT_WRIST)

        r_shoulder = get_coords(landmarks, PL.RIGHT_SHOULDER)
        r_elbow = get_coords(landmarks, PL.RIGHT_ELBOW)
        r_wrist = get_coords(landmarks, PL.RIGHT_WRIST)

        # Hip for posture check
        l_hip = get_coords(landmarks, PL.LEFT_HIP)
        r_hip = get_coords(landmarks, PL.RIGHT_HIP)

        # --- Calculate angles ---
        l_angle = calculate_angle(l_shoulder, l_elbow, l_wrist)
        r_angle = calculate_angle(r_shoulder, r_elbow, r_wrist)

        # Shoulder-to-hip angle (torso lean check)
        l_torso_angle = calculate_angle(l_elbow, l_shoulder, l_hip)
        r_torso_angle = calculate_angle(r_elbow, r_shoulder, r_hip)

        # --- Determine active arm (the one curling more) ---
        if r_angle < l_angle:
            angle = r_angle
            elbow_draw = r_elbow
            active_arm = "right"
        else:
            angle = l_angle
            elbow_draw = l_elbow
            active_arm = "left"

        # --- Draw angle near elbow ---
        h, w = frame.shape[:2]
        elbow_pixel = tuple(np.multiply(elbow_draw, [w, h]).astype(int))
        cv2.putText(frame, str(int(angle)), elbow_pixel,
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)

        # Draw both arm angles (smaller text)
        l_elbow_px = tuple(np.multiply(l_elbow, [w, h]).astype(int))
        r_elbow_px = tuple(np.multiply(r_elbow, [w, h]).astype(int))
        cv2.putText(frame, f"L:{int(l_angle)}", (l_elbow_px[0], l_elbow_px[1] + 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
        cv2.putText(frame, f"R:{int(r_angle)}", (r_elbow_px[0], r_elbow_px[1] + 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)

        # --- Rep counting with hysteresis ---
        # LEFT ARM
        if l_angle > 140:
            self.l_stage = "DOWN"
        if l_angle < 70 and self.l_stage == "DOWN":
            self.l_stage = "UP"
            self.counter += 1
            self.num_reps_rated += 1
            # Calculate rep quality (0.0-1.0)
            # More generous baseline (even a deep curl gets ~0.4 min)
            rep_quality = max(0.4, 1.0 - abs(l_angle - 30) / 100)
            if shoulder_moving: rep_quality = max(0.2, rep_quality - 0.2)
            if l_torso_angle > 50: rep_quality = max(0.2, rep_quality - 0.1)
            
            self.score += rep_quality
            self.feedback = "Good Rep! (Left)"

        # RIGHT ARM
        if r_angle > 140:
            self.r_stage = "DOWN"
        if r_angle < 70 and self.r_stage == "DOWN":
            self.r_stage = "UP"
            self.counter += 1
            self.num_reps_rated += 1
            # Calculate rep quality (0.0-1.0)
            # More generous baseline (even a deep curl gets ~0.4 min)
            rep_quality = max(0.4, 1.0 - abs(r_angle - 30) / 100)
            if shoulder_moving: rep_quality = max(0.2, rep_quality - 0.2)
            if r_torso_angle > 50: rep_quality = max(0.2, rep_quality - 0.1)
            
            self.score += rep_quality
            self.feedback = "Good Rep! (Right)"

        # Update combined stage display
        if active_arm == "left":
            self.stage = self.l_stage
        else:
            self.stage = self.r_stage

        # --- Form feedback ---
        # Shoulder stability: shoulder shouldn't move much during a curl
        shoulder_moving = False
        active_shoulder_y = l_shoulder[1] if active_arm == "left" else r_shoulder[1]
        prev_y = self._prev_l_shoulder_y if active_arm == "left" else self._prev_r_shoulder_y

        if prev_y is not None:
            shoulder_delta = abs(active_shoulder_y - prev_y)
            if shoulder_delta > 0.015:
                shoulder_moving = True
                self.feedback = "Keep shoulders still!"

        # Update previous shoulder positions
        self._prev_l_shoulder_y = l_shoulder[1]
        self._prev_r_shoulder_y = r_shoulder[1]

        # Torso lean check
        active_torso = l_torso_angle if active_arm == "left" else r_torso_angle
        if active_torso > 50:
            self.feedback = "Don't swing - keep elbows tucked!"

        # Angle-based feedback (only if form is OK)
        if not shoulder_moving and active_torso <= 50:
            if angle < 30:
                self.feedback = "Perfect contraction!"
            elif angle > 120 and self.stage == "DOWN":
                self.feedback = "Curl up higher!"
            elif 50 <= angle <= 80:
                self.feedback = "Keep going!"
            elif angle > 150:
                self.feedback = "Fully extended - Ready"

        # --- Score logic moved to rep completion points above ---

        return frame

