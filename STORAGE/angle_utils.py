import numpy as np
import mediapipe as mp

mp_pose = mp.solutions.pose

def calculate_angle(a, b, c):
    """Calculate angle at point b given three points a, b, c."""
    a = np.array(a)
    b = np.array(b)
    c = np.array(c)

    radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - \
              np.arctan2(a[1]-b[1], a[0]-b[0])

    angle = np.abs(radians * 180.0 / np.pi)

    if angle > 180:
        angle = 360 - angle

    return angle


def get_coords(landmarks, landmark_enum):
    """Extract [x, y] coordinates from a landmark."""
    lm = landmarks[landmark_enum.value]
    return [lm.x, lm.y]


def get_visibility(landmarks, landmark_enum):
    """Get visibility score for a landmark."""
    return landmarks[landmark_enum.value].visibility


def body_orientation(landmarks):
    """
    Determine body orientation based on landmark positions.
    Returns: 'standing', 'horizontal', or 'unknown'
    
    Logic:
    - Standing: shoulders are significantly above hips (y difference > 0.15)
    - Horizontal: shoulders and hips are at similar y levels (y difference < 0.1)
    """
    PL = mp_pose.PoseLandmark

    l_shoulder = get_coords(landmarks, PL.LEFT_SHOULDER)
    l_hip = get_coords(landmarks, PL.LEFT_HIP)
    r_shoulder = get_coords(landmarks, PL.RIGHT_SHOULDER)
    r_hip = get_coords(landmarks, PL.RIGHT_HIP)

    # Average shoulder and hip y positions
    avg_shoulder_y = (l_shoulder[1] + r_shoulder[1]) / 2
    avg_hip_y = (l_hip[1] + r_hip[1]) / 2

    # In image coordinates, y increases downward
    # So shoulders above hips means shoulder_y < hip_y
    y_diff = avg_hip_y - avg_shoulder_y

    if y_diff > 0.15:
        return 'standing'
    elif y_diff < 0.08:
        return 'horizontal'
    else:
        return 'unknown'