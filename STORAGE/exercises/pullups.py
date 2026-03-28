import cv2
import numpy as np
import mediapipe as mp
from .base import BaseExercise
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from angle_utils import calculate_angle, get_coords

mp_pose = mp.solutions.pose
PL = mp_pose.PoseLandmark


class PullupExercise(BaseExercise):
    """Pull-up tracker — counts reps based on elbow angle with arms overhead."""

    NAME = "PULL-UPS"
    COLOR = (200, 0, 255)  # Purple

    def process(self, landmarks, frame):
        # Arms
        l_shoulder = get_coords(landmarks, PL.LEFT_SHOULDER)
        l_elbow = get_coords(landmarks, PL.LEFT_ELBOW)
        l_wrist = get_coords(landmarks, PL.LEFT_WRIST)

        r_shoulder = get_coords(landmarks, PL.RIGHT_SHOULDER)
        r_elbow = get_coords(landmarks, PL.RIGHT_ELBOW)
        r_wrist = get_coords(landmarks, PL.RIGHT_WRIST)

        l_arm_angle = calculate_angle(l_shoulder, l_elbow, l_wrist)
        r_arm_angle = calculate_angle(r_shoulder, r_elbow, r_wrist)
        arm_angle = (l_arm_angle + r_arm_angle) / 2

        # Check if wrists are above shoulders (hanging/pulling)
        wrist_above = (l_wrist[1] < l_shoulder[1]) or (r_wrist[1] < r_shoulder[1])

        # Nose position relative to wrists (chin over bar)
        nose = get_coords(landmarks, PL.NOSE)
        chin_over = nose[1] < ((l_wrist[1] + r_wrist[1]) / 2)

        # Draw angle
        elbow_pixel = tuple(np.multiply(l_elbow, [frame.shape[1], frame.shape[0]]).astype(int))
        cv2.putText(frame, str(int(arm_angle)), elbow_pixel,
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)

        # Pull-up logic
        if arm_angle > 155:
            self.stage = "DOWN"
            self.feedback = "Hanging - Ready"

        if arm_angle < 80 and self.stage == "DOWN":
            self.stage = "UP"
            self.counter += 1
            self.num_reps_rated += 1
            # Calculate rep quality (0-10)
            rep_quality = max(0, 10 - abs(arm_angle - 60) / 10)
            if chin_over: rep_quality = min(10.0, rep_quality + 2)
            self.total_quality += rep_quality
            self.score = self.total_quality / self.num_reps_rated
            self.feedback = "Good Rep!"

        # Detailed feedback
        if arm_angle < 60:
            self.feedback = "Excellent pull!"
        elif 80 <= arm_angle <= 120 and self.stage == "DOWN":
            self.feedback = "Pull higher!"

        if chin_over and self.stage == "UP":
            self.feedback = "Chin over bar - Perfect!"

        # --- Score logic moved to rep completion points above ---

        return frame
