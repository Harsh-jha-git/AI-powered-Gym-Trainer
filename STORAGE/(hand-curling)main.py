import cv2
import mediapipe as mp
import numpy as np
from angle_utils import calculate_angle

# Initialize MediaPipe
mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils

pose = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)

# Webcam (set to max resolution: 2560x1440)
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 2560)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1440)

# Curl tracking variables
counter = 0
stage = None
feedback = ""
score = 0

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Convert BGR → RGB
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = pose.process(rgb_frame)

    if result.pose_landmarks:
        mp_drawing.draw_landmarks(frame, result.pose_landmarks, mp_pose.POSE_CONNECTIONS)

        try:
            landmarks = result.pose_landmarks.landmark

            # Get coordinates
            shoulder = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,
                        landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]

            elbow = [landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].x,
                     landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].y]

            wrist = [landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].x,
                     landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].y]

            # Calculate angle
            angle = calculate_angle(shoulder, elbow, wrist)

            # Convert to pixel coords
            elbow_pixel = tuple(np.multiply(elbow, [frame.shape[1], frame.shape[0]]).astype(int))

            # -----------------------------
            # 🎯 CURL LOGIC
            # -----------------------------

            # Stage detection
            if angle > 160:
                stage = "DOWN"
                feedback = "Lowered - Ready"

            if angle < 40 and stage == "DOWN":
                stage = "UP"
                counter += 1
                feedback = "Good Rep!"

            # Feedback improvements
            if angle > 120:
                feedback = "Lower your arm more"
            elif angle < 30:
                feedback = "Perfect contraction"

            # Score calculation (ideal curl ~ 30°)
            ideal_angle = 30
            score = max(0, 100 - abs(angle - ideal_angle))

            # -----------------------------
            # DISPLAY
            # -----------------------------

            # Angle near elbow
            cv2.putText(frame, str(int(angle)),
                        elbow_pixel,
                        cv2.FONT_HERSHEY_SIMPLEX, 1,
                        (255, 255, 255), 2, cv2.LINE_AA)

            # UI Panel
            cv2.rectangle(frame, (0, 0), (300, 120), (0, 0, 0), -1)

            cv2.putText(frame, f'Reps: {counter}', (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

            cv2.putText(frame, f'Stage: {stage}', (10, 60),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)

            cv2.putText(frame, f'Feedback: {feedback}', (10, 90),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 200, 255), 2)

            cv2.putText(frame, f'Score: {int(score)}', (180, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 255), 2)

        except:
            pass

    # Resize for display (fit to screen)
    display_frame = cv2.resize(frame, (1280, 720))
    cv2.imshow("AI Bicep Curl Trainer", display_frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()