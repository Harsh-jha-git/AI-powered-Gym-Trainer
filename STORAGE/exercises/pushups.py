import cv2
import numpy as np
import mediapipe as mp
from .base import BaseExercise
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from angle_utils import calculate_angle, get_coords

mp_pose = mp.solutions.pose
PL = mp_pose.PoseLandmark


class PushupExercise(BaseExercise):
    """Push-up tracker — counts reps based on elbow angle in horizontal position."""

    NAME = "PUSH-UPS"
    COLOR = (255, 100, 0)  # Blue

    def process(self, landmarks, frame):
        # Arms
        l_shoulder = get_coords(landmarks, PL.LEFT_SHOULDER)
        l_elbow = get_coords(landmarks, PL.LEFT_ELBOW)
        l_wrist = get_coords(landmarks, PL.LEFT_WRIST)

        r_shoulder = get_coords(landmarks, PL.RIGHT_SHOULDER)
        r_elbow = get_coords(landmarks, PL.RIGHT_ELBOW)
        r_wrist = get_coords(landmarks, PL.RIGHT_WRIST)

        # Body alignment (shoulder → hip → ankle)
        l_hip = get_coords(landmarks, PL.LEFT_HIP)
        l_ankle = get_coords(landmarks, PL.LEFT_ANKLE)
        body_angle = calculate_angle(l_shoulder, l_hip, l_ankle)

        l_arm_angle = calculate_angle(l_shoulder, l_elbow, l_wrist)
        r_arm_angle = calculate_angle(r_shoulder, r_elbow, r_wrist)
        arm_angle = (l_arm_angle + r_arm_angle) / 2

        # Draw angle near elbow
        elbow_pixel = tuple(np.multiply(l_elbow, [frame.shape[1], frame.shape[0]]).astype(int))
        cv2.putText(frame, str(int(arm_angle)), elbow_pixel,
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)

        # Push-up logic
        if arm_angle > 155:
            self.stage = "UP"
            self.feedback = "Arms extended"

        if arm_angle < 90 and self.stage == "UP":
            self.stage = "DOWN"
            self.counter += 1
            self.num_reps_rated += 1
            # Calculate rep quality (0-10)
            rep_quality = max(0, 10 - abs(arm_angle - 80) / 10)
            if body_angle < 150 or body_angle > 175: rep_quality = max(0, rep_quality - 3)
            self.total_quality += rep_quality
            self.score = self.total_quality / self.num_reps_rated
            self.feedback = "Good Rep!"

        # Detailed feedback
        if arm_angle < 70:
            self.feedback = "Great depth!"
        elif 90 <= arm_angle <= 120 and self.stage == "UP":
            self.feedback = "Go lower!"

        # Body alignment feedback
        if body_angle < 150:
            self.feedback = "Keep body straight - no sagging!"
        elif body_angle > 175:
            self.feedback = "Don't pike your hips!"

        # --- Score logic moved to rep completion points above ---

        return frame
