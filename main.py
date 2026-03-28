import cv2
import mediapipe as mp
import numpy as np
import time
import winsound  # For alert sound (Windows)

# --------------------------
# Angle Calculation
# --------------------------
def calculate_angle(a, b, c):
    a = np.array(a)
    b = np.array(b)
    c = np.array(c)

    radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - \
              np.arctan2(a[1]-b[1], a[0]-b[0])

    angle = np.abs(radians * 180.0 / np.pi)

    if angle > 180:
        angle = 360 - angle

    return angle


# Setup
mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils
pose = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)

cap = cv2.VideoCapture(0)

# --------------------------
# TIMER VARIABLES
# --------------------------
bad_posture_start = None
good_posture_start = time.time()
good_posture_duration = 0

while True:
    ret, frame = cap.read()
    if not ret:
        break

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = pose.process(rgb)

    score = 100
    issues = []

    if result.pose_landmarks:
        mp_drawing.draw_landmarks(frame, result.pose_landmarks, mp_pose.POSE_CONNECTIONS)

        try:
            lm = result.pose_landmarks.landmark

            # Points
            left_shoulder = np.array([lm[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,
                                     lm[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y])

            right_shoulder = np.array([lm[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x,
                                      lm[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y])

            left_hip = np.array([lm[mp_pose.PoseLandmark.LEFT_HIP.value].x,
                                 lm[mp_pose.PoseLandmark.LEFT_HIP.value].y])

            nose = np.array([lm[mp_pose.PoseLandmark.NOSE.value].x,
                             lm[mp_pose.PoseLandmark.NOSE.value].y])

            # --------------------------
            # POSTURE ANALYSIS
            # --------------------------

            # Shoulder
            if abs(left_shoulder[1] - right_shoulder[1]) > 0.05:
                issues.append("Uneven shoulders")
                score -= 20

            # Head
            shoulder_center_x = (left_shoulder[0] + right_shoulder[0]) / 2
            if nose[0] > shoulder_center_x + 0.05:
                issues.append("Head forward")
                score -= 25

            # Spine
            vertical_point = np.array([left_hip[0], left_hip[1] - 0.2])
            spine_angle = calculate_angle(left_shoulder, left_hip, vertical_point)

            if spine_angle < 160:
                issues.append("Slouching")
                score -= 35

            score = max(0, score)

            # --------------------------
            # ALERT SYSTEM 🔔
            # --------------------------
            current_time = time.time()

            if len(issues) > 0:
                # Bad posture
                if bad_posture_start is None:
                    bad_posture_start = current_time

                elapsed_bad = current_time - bad_posture_start

                if elapsed_bad > 3:
                    winsound.Beep(1000, 500)  # frequency, duration
                    cv2.putText(frame, "FIX YOUR POSTURE!", (50, 200),
                                cv2.FONT_HERSHEY_SIMPLEX, 1,
                                (0, 0, 255), 3)

                # Reset good timer
                good_posture_start = current_time

            else:
                # Good posture
                bad_posture_start = None
                good_posture_duration = current_time - good_posture_start

            # --------------------------
            # FEEDBACK
            # --------------------------
            if len(issues) == 0:
                feedback = "Excellent posture"
            else:
                feedback = ", ".join(issues)

            # --------------------------
            # DISPLAY
            # --------------------------

            cv2.rectangle(frame, (0, 0), (450, 180), (0, 0, 0), -1)

            cv2.putText(frame, f'Score: {score}', (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

            cv2.putText(frame, f'Issues:', (10, 70),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

            cv2.putText(frame, feedback, (10, 100),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 200, 255), 2)

            cv2.putText(frame, f'Good Posture Time: {int(good_posture_duration)}s',
                        (10, 140),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)

            # Spine angle display
            hip_pixel = tuple(np.multiply(left_hip, [frame.shape[1], frame.shape[0]]).astype(int))
            cv2.putText(frame, f"{int(spine_angle)}",
                        hip_pixel,
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7,
                        (255, 255, 255), 2)

        except:
            pass

    cv2.imshow("AI Posture Corrector", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()