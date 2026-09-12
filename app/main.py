import time
import cv2

from camera import Camera
from config import Config
from detector import HandsDetector
from drawing import draw_landmarks, draw_interface
from fps import FPSCounter
from landmarks import HAND_CONNECTIONS
from smoother import LandmarkSmoother


def save_screenshot(frame):
    filename = f"hand_{int(time.time())}.png"
    if cv2.imwrite(filename, frame):
        print(f"Сохранено: {filename}")
    else:
        print(f"Ошибка: {filename}")


def get_handedness(results):
    if not results or not results.handedness:
        return []

    return [
        hand[0].category_name
        for hand in results.handedness
        if hand
    ]


def main():
    config = Config()

    try:
        camera = Camera(config.CAMERA_INDEX)
        detector = HandsDetector(
            model_path=config.MODEL_PATH,
            max_num_hands=config.MAX_NUM_HANDS,
            min_detection_confidence=config.MIN_DETECTION_CONFIDENCE,
            min_tracking_confidence=config.MIN_TRACKING_CONFIDENCE,
        )
    except (RuntimeError, FileNotFoundError) as error:
        print(f"Ошибка: {error}")
        return

    smoothers = [
        LandmarkSmoother(config.SMOOTH_ALPHA)
        for _ in range(config.MAX_NUM_HANDS)
    ]

    fps = FPSCounter()
    mirror = config.MIRROR
    frame_count = 0
    results = None

    cv2.namedWindow(config.WINDOW_NAME, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(config.WINDOW_NAME, 900, 650)

    try:
        while True:
            frame = camera.read()

            if mirror:
                frame = camera.flip(frame)

            fps.update()
            frame_count += 1

            if frame_count % config.PROCESS_EVERY_N_FRAMES == 0:
                results = detector.process(frame)

            handedness = get_handedness(results)
            hands_count = 0

            if results and results.hand_landmarks:
                hands_count = len(results.hand_landmarks)

                for i, landmarks in enumerate(results.hand_landmarks):
                    if i >= len(smoothers):
                        smoothers.append(
                            LandmarkSmoother(config.SMOOTH_ALPHA)
                        )

                    landmarks = smoothers[i].smooth(landmarks)
                    label = handedness[i] if i < len(handedness) else None

                    draw_landmarks(
                        frame,
                        landmarks,
                        HAND_CONNECTIONS,
                        frame.shape[1],
                        frame.shape[0],
                        label=label,
                    )

            draw_interface(
                frame,
                fps=fps.value,
                mirror=mirror,
                hands_count=hands_count,
                handedness=handedness,
            )

            cv2.imshow(config.WINDOW_NAME, frame)

            key = cv2.waitKey(1) & 0xFF

            if key == ord("q"):
                break
            if key == ord("m"):
                mirror = not mirror
            elif key == ord("s"):
                save_screenshot(frame)

    except KeyboardInterrupt:
        pass
    finally:
        camera.release()
        detector.close()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()