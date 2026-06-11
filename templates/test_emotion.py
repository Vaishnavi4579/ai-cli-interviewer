try:
    from deepface import DeepFace
    import cv2
    _deepface_available = True
except Exception:
    _deepface_available = False

if not _deepface_available:
    print("DeepFace/OpenCV not installed. Install with 'pip install deepface opencv-python' to run the emotion demo.")
    # Exit cleanly when dependencies are not present.
    raise SystemExit(0)

cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()

    result = DeepFace.analyze(
        frame,
        actions=['emotion'],
        enforce_detection=False
    )

    emotion = result[0]['dominant_emotion']

    cv2.putText(
        frame,
        f"Emotion: {emotion}",
        (50, 50),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (0, 255, 0),
        2
    )

    cv2.imshow("Emotion Detection", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()