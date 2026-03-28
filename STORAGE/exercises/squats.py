import cv2
import numpy as np
import mediapipe as mp
from .base import BaseExercise
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from angle_utils import calculate_angle, get_coords

mp_pose = mp.solutions.pose
PL = mp_pose.PoseLandmark


class SquatExercise(BaseExercise):
    """Squat tracker — counts reps based on knee angle."""

    NAME = "SQUATS"
    COLOR = (0, 255, 100)  # Green

    def process(self, landmarks, frame):
        # Left leg
        # Get key points for both legs
        l_hip = get_coords(landmarks, PL.LEFT_HIP)
        l_knee = get_coords(landmarks, PL.LEFT_KNEE)
        l_ankle = get_coords(landmarks, PL.LEFT_ANKLE)
        
        r_hip = get_coords(landmarks, PL.RIGHT_HIP)
        r_knee = get_coords(landmarks, PL.RIGHT_KNEE)
        r_ankle = get_coords(landmarks, PL.RIGHT_ANKLE)

        # Calculate angles
        l_angle = calculate_angle(l_hip, l_knee, l_ankle)
        r_angle = calculate_angle(r_hip, r_knee, r_ankle)

        # Average both knees
        angle = (l_angle + r_angle) / 2

        # Draw angle near knee
        knee_pixel = tuple(np.multiply(l_knee, [frame.shape[1], frame.shape[0]]).astype(int))
        cv2.putText(frame, str(int(angle)), knee_pixel,
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)

        # Squat logic
        if angle > 160:
            self.stage = "UP"
            self.feedback = "Standing - Ready"

        if angle < 100 and self.stage == "UP":
            self.stage = "DOWN"
            self.counter += 1
            self.num_reps_rated += 1
            # Calculate rep quality (0.0-1.0)
            # More generous baseline
            rep_quality = max(0.5, 1.0 - abs(angle - 90) / 100)
            if abs(l_knee[0] - l_ankle[0]) > 0.05: rep_quality = max(0.3, rep_quality - 0.2)
            self.score += rep_quality
            self.feedback = "Good Rep!"

        # Detailed feedback
        if 100 <= angle <= 130 and self.stage == "UP":
            self.feedback = "Go deeper!"
        elif angle < 80:
            self.feedback = "Great depth!"
        elif angle > 160:
            self.feedback = "Standing tall"

        # Check knee alignment (knees shouldn't cave inward)
        if abs(l_knee[0] - l_ankle[0]) > 0.05:
            self.feedback = "Watch knee alignment!"

        # --- Score logic moved to rep completion points above ---

        return frame
