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
    """Bicep Curl tracker — counts reps based on elbow angle."""

    NAME = "BICEP CURLS"
    COLOR = (0, 200, 255)  # Orange

    def process(self, landmarks, frame):
        # Get coordinates (left arm)
        shoulder = get_coords(landmarks, PL.LEFT_SHOULDER)
        elbow = get_coords(landmarks, PL.LEFT_ELBOW)
        wrist = get_coords(landmarks, PL.LEFT_WRIST)

        # Also check right arm
        r_shoulder = get_coords(landmarks, PL.RIGHT_SHOULDER)
        r_elbow = get_coords(landmarks, PL.RIGHT_ELBOW)
        r_wrist = get_coords(landmarks, PL.RIGHT_WRIST)

        l_angle = calculate_angle(shoulder, elbow, wrist)
        r_angle = calculate_angle(r_shoulder, r_elbow, r_wrist)

        # Use the arm that's curling more (smaller angle = more curled)
        if r_angle < l_angle:
            angle = r_angle
            elbow_draw = r_elbow
        else:
            angle = l_angle
            elbow_draw = elbow

        # Draw angle near elbow
        elbow_pixel = tuple(np.multiply(elbow_draw, [frame.shape[1], frame.shape[0]]).astype(int))
        cv2.putText(frame, str(int(angle)), elbow_pixel,
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)

        # Curl logic
        if angle > 160:
            self.stage = "DOWN"
            self.feedback = "Lowered - Ready"

        if angle < 40 and self.stage == "DOWN":
            self.stage = "UP"
            self.counter += 1
            self.feedback = "Good Rep!"

        # Detailed feedback
        if angle > 120:
            self.feedback = "Lower your arm more"
        elif angle < 30:
            self.feedback = "Perfect contraction!"

        # Score (ideal curl ~ 30°)
        self.score = max(0, 100 - abs(angle - 30))

        return frame
