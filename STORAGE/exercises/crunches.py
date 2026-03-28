import cv2
import numpy as np
import mediapipe as mp
from .base import BaseExercise
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from angle_utils import calculate_angle, get_coords

mp_pose = mp.solutions.pose
PL = mp_pose.PoseLandmark


class CrunchExercise(BaseExercise):
    """Abdominal Crunch tracker — counts reps based on torso curl angle."""

    NAME = "CRUNCHES"
    COLOR = (100, 255, 100)  # Light green

    def process(self, landmarks, frame):
        # Core points for crunch detection
        l_shoulder = get_coords(landmarks, PL.LEFT_SHOULDER)
        r_shoulder = get_coords(landmarks, PL.RIGHT_SHOULDER)
        l_hip = get_coords(landmarks, PL.LEFT_HIP)
        r_hip = get_coords(landmarks, PL.RIGHT_HIP)
        l_knee = get_coords(landmarks, PL.LEFT_KNEE)
        r_knee = get_coords(landmarks, PL.RIGHT_KNEE)

        # Average positions
        shoulder_mid = [(l_shoulder[0] + r_shoulder[0]) / 2,
                        (l_shoulder[1] + r_shoulder[1]) / 2]
        hip_mid = [(l_hip[0] + r_hip[0]) / 2,
                   (l_hip[1] + r_hip[1]) / 2]
        knee_mid = [(l_knee[0] + r_knee[0]) / 2,
                    (l_knee[1] + r_knee[1]) / 2]

        # Crunch angle: shoulder → hip → knee
        crunch_angle = calculate_angle(shoulder_mid, hip_mid, knee_mid)

        # Draw angle near hip
        hip_pixel = tuple(np.multiply(hip_mid, [frame.shape[1], frame.shape[0]]).astype(int))
        cv2.putText(frame, str(int(crunch_angle)), hip_pixel,
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)

        # Crunch logic
        # Lying flat: angle ~160-180°
        # Crunched up: angle ~90-120°
        if crunch_angle > 150:
            self.stage = "DOWN"
            self.feedback = "Lying flat - Ready"

        if crunch_angle < 120 and self.stage == "DOWN":
            self.stage = "UP"
            self.counter += 1
            self.num_reps_rated += 1
            # Calculate rep quality (0.0-1.0)
            # More generous baseline
            rep_quality = max(0.5, 1.0 - abs(crunch_angle - 100) / 100)
            self.score += rep_quality
            self.feedback = "Good Rep!"

        # Detailed feedback
        if crunch_angle < 100:
            self.feedback = "Great contraction!"
        elif 120 <= crunch_angle <= 140 and self.stage == "DOWN":
            self.feedback = "Crunch higher!"

        # --- Score logic moved to rep completion points above ---

        return frame
