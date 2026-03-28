import cv2

cap = cv2.VideoCapture(0)

# Test common resolutions (width x height)
resolutions = [
    ("4K (3840x2160)", 3840, 2160),
    ("QHD (2560x1440)", 2560, 1440),
    ("1080p (1920x1080)", 1920, 1080),
    ("720p (1280x720)", 1280, 720),
    ("480p (640x480)", 640, 480),
    ("360p (480x360)", 480, 360),
    ("240p (320x240)", 320, 240),
]

print("Testing webcam resolutions...\n")

for name, w, h in resolutions:
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, w)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, h)
    actual_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    actual_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    match = "✓" if actual_w == w and actual_h == h else "✗"
    print(f"  {match} {name:25s} -> Actual: {actual_w}x{actual_h}")

# Show the highest supported
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 10000)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 10000)
max_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
max_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
print(f"\n>>> Highest resolution supported: {max_w}x{max_h}")

cap.release()
