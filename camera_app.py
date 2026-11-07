import time
from pathlib import Path

import cv2
import mediapipe as mp

from gesture_recognition import detect_gesture
from stickers import load_stickers, overlay_sticker

PROJECT_DIR = Path(__file__).resolve().parent
MODEL_PATH = PROJECT_DIR / "hand_landmarker.task"

HAND_CONNECTIONS = [
    (0, 1), (1, 2), (2, 3), (3, 4),
    (0, 5), (5, 6), (6, 7), (7, 8),
    (5, 9), (9, 10), (10, 11), (11, 12),
    (9, 13), (13, 14), (14, 15), (15, 16),
    (13, 17), (17, 18), (18, 19), (19, 20),
    (0, 17),
]

def create_hand_detector():
    options = mp.tasks.vision.HandLandmarkerOptions(
        base_options=mp.tasks.BaseOptions(model_asset_path=str(MODEL_PATH)),
        running_mode=mp.tasks.vision.RunningMode.VIDEO,
        num_hands=2,
        min_hand_detection_confidence=0.7,
        min_tracking_confidence=0.7,
    )
    return mp.tasks.vision.HandLandmarker.create_from_options(options)


def draw_hand_landmarks(frame, hands) -> None:
    height, width = frame.shape[:2]

    for hand in hands:
        points = []
        for landmark in hand:
            point = (int(landmark.x * width), int(landmark.y * height))
            points.append(point)
            cv2.circle(frame, point, 5, (0, 255, 0), -1)

        for start, end in HAND_CONNECTIONS:
            cv2.line(frame, points[start], points[end], (255, 0, 0), 2)

        cv2.putText(
            frame,
            "Hand erkannt!",
            (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 255, 0),
            2,
        )


def create_virtual_camera(width: int, height: int, fps: float):
    try:
        import pyvirtualcam
    except ImportError as error:
        raise RuntimeError(
            "Das Paket pyvirtualcam fehlt. Installiere es mit: "
            "python -m pip install pyvirtualcam"
        ) from error

    try:
        return pyvirtualcam.Camera(
            width=width,
            height=height,
            fps=fps,
            fmt=pyvirtualcam.PixelFormat.BGR,
            device="OBS Virtual Camera",
            backend="obs",
        )
    except RuntimeError as error:
        raise RuntimeError(
            "OBS-Virtual-Camera-Ausgabe konnte nicht gestartet werden. "
            "Stoppe die Virtual Camera in OBS und beende alle weiteren "
            f"Instanzen dieses Skripts. Ursprünglicher Fehler: {error}"
        ) from error


def run_camera_app() -> None:
    stickers = load_stickers(PROJECT_DIR / "images")
    camera = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    if not camera.isOpened():
        camera.release()
        raise RuntimeError("Kamera konnte nicht geöffnet werden")

    try:
        width = int(camera.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(camera.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = camera.get(cv2.CAP_PROP_FPS)
        if not 1 <= fps <= 60:
            fps = 30

        virtual_camera = create_virtual_camera(width, height, fps)
        with virtual_camera:
            with create_hand_detector() as detector:
                while True:
                    success, frame = camera.read()
                    if not success:
                        break

                    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    mp_image = mp.Image(
                        image_format=mp.ImageFormat.SRGB,
                        data=rgb_frame,
                    )
                    timestamp = time.perf_counter_ns() // 1_000_000
                    result = detector.detect_for_video(mp_image, timestamp)

                    gesture = detect_gesture(
                        result.hand_landmarks,
                        result.hand_world_landmarks,
                    )
                    draw_hand_landmarks(frame, result.hand_landmarks)

                    if gesture:
                        overlay_sticker(frame, stickers[gesture])
                        cv2.putText(
                            frame,
                            f"{gesture} erkannt!",
                            (20, 80),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            1,
                            (0, 255, 0),
                            2,
                        )

                    virtual_camera.send(frame)
                    virtual_camera.sleep_until_next_frame()
                    cv2.imshow("Gesture Recognition", frame)

                    if cv2.waitKey(1) & 0xFF == ord("q"):
                        break
    finally:
        camera.release()
        cv2.destroyAllWindows()
