import numpy as np
from collections import deque
import time

class TemporalPostureAnalyzer:
    """
    Simulates LSTM-like posture analysis by tracking a sequence of landmarks.
    Analyzes stability, velocity, and symmetry over a sliding window of frames.
    """
    def __init__(self, window_size=30):
        self.window_size = window_size
        self.history = deque(maxlen=window_size)
        self.last_analysis_time = 0
        self.min_interval = 0.5  # Analyze every 500ms
        
    def update(self, landmarks):
        """Add new landmarks to the temporal history."""
        # Convert landmarks to a flat array of [x, y, z] for key points
        # Only track essential points to keep it fast
        key_indices = [11, 12, 13, 14, 23, 24] # Shoulders, Elbows, Hips
        frame_data = []
        for idx in key_indices:
            lm = landmarks[idx]
            frame_data.extend([lm.x, lm.y, lm.z])
            
        self.history.append(np.array(frame_data))
        
    def analyze(self):
        """Perform temporal analysis on the landmark sequence."""
        if len(self.history) < self.window_size:
            return None
            
        now = time.time()
        if now - self.last_analysis_time < self.min_interval:
            return None
            
        self.last_analysis_time = now
        data = np.array(self.history) # Shape: (window_size, num_features)
        
        # 1. Calculate Velocity (1st Derivative)
        velocity = np.diff(data, axis=0)
        avg_velocity = np.mean(np.abs(velocity))
        
        # 2. Calculate Jitter/Stability (Variance of Velocity)
        # High jitter = shaky movement
        jitter = np.var(velocity, axis=0).mean()
        
        # 3. Symmetry Check (Comparing left/right features)
        # Features are: [L_Sh_x, L_Sh_y, L_Sh_z, R_Sh_x, R_Sh_y, R_Sh_z, ...]
        l_side = data[:, :3] # Left Shoulder
        r_side = data[:, 3:6] # Right Shoulder
        symmetry_diff = np.abs(l_side - r_side).mean()
        
        # 4. Consistency (How much the rep speed varies)
        speed_consistency = np.std(np.linalg.norm(velocity, axis=1))

        metrics = {
            "avg_velocity": float(avg_velocity),
            "stability_score": float(1.0 / (1.0 + jitter * 100)), # Normalized 0-1
            "is_shaky": bool(jitter > 0.0005),
            "symmetry_score": float(1.0 - symmetry_diff),
            "consistency": float(1.0 / (1.0 + speed_consistency * 10)),
            "posture_trend": "Improving" if np.mean(data[-5:]) > np.mean(data[:5]) else "Degrading"
        }
        
        return metrics

    def get_summary_for_llm(self, metrics):
        """Format metrics into a concise string for Llama."""
        if not metrics: return "Normal movement detected."
        
        summary = []
        if metrics["is_shaky"]: summary.append("User is shaking/unstable.")
        if metrics["stability_score"] < 0.7: summary.append(f"Low stability: {metrics['stability_score']:.2f}")
        if metrics["consistency"] < 0.6: summary.append("Inconsistent rep speed.")
        if metrics["symmetry_score"] < 0.8: summary.append("Asymmetric movement detected.")
        
        return " | ".join(summary) if summary else "Stable, controlled movement."
