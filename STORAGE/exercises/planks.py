import cv2
import numpy as np
import mediapipe as mp
import time
from .base import TimedExercise
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from angle_utils import calculate_angle, get_coords

mp_pose = mp.solutions.pose
PL = mp_pose.PoseLandmark


class PlankExercise(TimedExercise):
    """Plank tracker — time-based, tracks hold duration and body alignment."""

    NAME = "PLANK"
    COLOR = (0, 255, 255)  # Yellow

    def process(self, landmarks, frame):
        # Body alignment points
        l_shoulder = get_coords(landmarks, PL.LEFT_SHOULDER)
        l_hip = get_coords(landmarks, PL.LEFT_HIP)
        l_ankle = get_coords(landmarks, PL.LEFT_ANKLE)

        # Elbow/wrist for arm position
        l_elbow = get_coords(landmarks, PL.LEFT_ELBOW)

        # Body angle: shoulder → hip → ankle (should be ~170-180° for good plank)
        body_angle = calculate_angle(l_shoulder, l_hip, l_ankle)

        # Draw body angle near hip
        hip_pixel = tuple(np.multiply(l_hip, [frame.shape[1], frame.shape[0]]).astype(int))
        cv2.putText(frame, str(int(body_angle)), hip_pixel,
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)

        # Check if in plank position (body roughly horizontal and straight)
        is_horizontal = abs(l_shoulder[1] - l_hip[1]) < 0.12
        is_straight = body_angle > 150

        current_time = time.time()

        if is_horizontal and is_straight:
            # Good plank form
            if self.hold_start is None:
                self.hold_start = current_time

            self.hold_duration = current_time - self.hold_start

            # Feedback based on alignment
            if body_angle > 170:
                self.feedback = "Perfect form!"
                self.score = 100
            elif body_angle > 160:
                self.feedback = "Good form - stay tight!"
                self.score = 80
            else:
                self.feedback = "Straighten your body!"
                self.score = 60

            # Hip sag detection
            if l_hip[1] > l_shoulder[1] + 0.05 and l_hip[1] > l_ankle[1]:
                self.feedback = "Hips sagging - lift up!"
                self.score = max(30, self.score - 30)

            # Hip pike detection
            if l_hip[1] < l_shoulder[1] - 0.05:
                self.feedback = "Hips too high - lower them!"
                self.score = max(30, self.score - 30)

        else:
            # Not in plank
            if self.hold_start is not None:
                self.feedback = f"Hold broken at {int(self.hold_duration)}s"
            else:
                self.feedback = "Get into plank position"
            self.hold_start = None
            self.score = 0

        # Draw hold time on frame
        if self.hold_duration > 0:
            mins = int(self.hold_duration) // 60
            secs = int(self.hold_duration) % 60
            time_str = f"{mins}:{secs:02d}" if mins > 0 else f"{secs}s"

            # Big timer in center
            h, w = frame.shape[:2]
            cv2.putText(frame, time_str, (w // 2 - 60, h // 2),
                        cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 255), 4)

        return frame
