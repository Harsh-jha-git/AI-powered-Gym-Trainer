import cv2
import numpy as np
from abc import ABC, abstractmethod


class BaseExercise(ABC):
    """Base class for all exercise trackers."""

    NAME = "Unknown"
    COLOR = (0, 255, 0)  # Default green

    def __init__(self):
        self.counter = 0
        self.stage = None
        self.feedback = ""
        self.score = 0

    def reset(self):
        """Reset all tracking state."""
        self.counter = 0
        self.stage = None
        self.feedback = ""
        self.score = 0

    @abstractmethod
    def process(self, landmarks, frame):
        """
        Process a frame with detected landmarks.
        Should update self.counter, self.stage, self.feedback, self.score.
        Can draw exercise-specific overlays on the frame.
        
        Args:
            landmarks: MediaPipe pose landmarks
            frame: OpenCV frame (BGR) to draw on
        Returns:
            frame: annotated frame
        """
        pass

    def draw_ui(self, frame):
        """Draw the standard UI panel overlay."""
        h, w = frame.shape[:2]

        # Semi-transparent panel
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, 0), (420, 160), (20, 20, 20), -1)
        cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)

        # Exercise name badge
        cv2.rectangle(frame, (0, 0), (420, 35), self.COLOR, -1)
        cv2.putText(frame, f'{self.NAME}', (10, 25),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2)

        # Stats
        cv2.putText(frame, f'Reps: {self.counter}', (10, 65),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        cv2.putText(frame, f'Stage: {self.stage or "—"}', (220, 65),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)

        cv2.putText(frame, f'Score: {int(self.score)}', (10, 100),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 255), 2)

        cv2.putText(frame, f'{self.feedback}', (10, 140),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 200, 255), 2)

        return frame


class TimedExercise(BaseExercise):
    """Base class for time-based exercises (e.g., plank)."""

    def __init__(self):
        super().__init__()
        self.hold_start = None
        self.hold_duration = 0

    def reset(self):
        super().reset()
        self.hold_start = None
        self.hold_duration = 0

    def draw_ui(self, frame):
        """Draw UI with hold duration instead of reps."""
        h, w = frame.shape[:2]

        overlay = frame.copy()
        cv2.rectangle(overlay, (0, 0), (420, 160), (20, 20, 20), -1)
        cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)

        # Exercise name badge
        cv2.rectangle(frame, (0, 0), (420, 35), self.COLOR, -1)
        cv2.putText(frame, f'{self.NAME}', (10, 25),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2)

        # Stats
        cv2.putText(frame, f'Hold: {int(self.hold_duration)}s', (10, 65),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        cv2.putText(frame, f'Score: {int(self.score)}', (220, 65),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 255), 2)

        cv2.putText(frame, f'{self.feedback}', (10, 100),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 200, 255), 2)

        return frame
