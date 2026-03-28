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
        self._audio_manager = None
        self._prev_feedback = ""

    def set_audio_manager(self, audio_manager):
        """Attach an AudioManager for voice coaching."""
        self._audio_manager = audio_manager

    def reset(self):
        """Reset all tracking state."""
        self.counter = 0
        self.stage = None
        self.feedback = ""
        self.score = 0
        self._prev_feedback = ""
        if self._audio_manager:
            self._audio_manager.reset_tracking(self.NAME)

    def _trigger_audio(self):
        """
        Called after process() to trigger audio feedback if something changed.
        Automatically speaks new feedback and plays ding on new reps.
        """
        if not self._audio_manager:
            return

        # Play ding on new reps
        self._audio_manager.play_rep_sound(self.NAME, self.counter)

        # Speak feedback if it changed
        if self.feedback and self.feedback != self._prev_feedback:
            self._audio_manager.speak_feedback(self.feedback)
            self._prev_feedback = self.feedback

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

        # Audio status indicator
        if self._audio_manager:
            mute_icon = "MUTED" if self._audio_manager.muted else "AUDIO ON"
            mute_color = (0, 0, 200) if self._audio_manager.muted else (0, 200, 0)
            cv2.putText(frame, mute_icon, (320, 100),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.45, mute_color, 1)

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

        # Audio status indicator
        if self._audio_manager:
            mute_icon = "MUTED" if self._audio_manager.muted else "AUDIO ON"
            mute_color = (0, 0, 200) if self._audio_manager.muted else (0, 200, 0)
            cv2.putText(frame, mute_icon, (320, 65),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.45, mute_color, 1)

        cv2.putText(frame, f'{self.feedback}', (10, 100),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 200, 255), 2)

        return frame
