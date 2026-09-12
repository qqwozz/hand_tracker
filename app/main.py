import time

import cv2

from camera import Camera
from config import Config
from detector import HandsDetector
from drawing import draw_landmarks, draw_interface
from fps import FPSCounter
from landmarks import HAND_CONNECTIONS
from smoother import LandmarkSmoother


def print_controls():
    print("=== HAND TRACKER ===")
    print()
    print("Управление:")
    print("  M - зеркало вкл/выкл")
    print("  S - сохранить скриншот")
    print("  Q - выход")
    print()


def save_screenshot(frame):
    timestamp = int(time.time())
    filename = f"hand_{timestamp}.png"

    success = cv2.imwrite(filename, frame)

    if success:
        print(f"Скриншот сохранён: {filename}")
    else:
        print(f"Ошибка сохранения: {filename}")


def get_handedness(results):
    handedness = []

    if results is None or not results.handedness:
        return handedness

    for hand in results.handedness:
        if hand:
            handedness.append(hand[0].category_name)

    return handedness


def main():
    config = Config()

    print_controls()

    # ========================================================
    # CAMERA
    # ========================================================

    try:
        camera = Camera(config.CAMERA_INDEX)

    except RuntimeError as error:
        print(f"Ошибка камеры: {error}")
        return

    # ========================================================
    # DETECTOR
    # ========================================================

    try:
        detector = HandsDetector(
            model_path=config.MODEL_PATH,
            max_num_hands=config.MAX_NUM_HANDS,
            min_detection_confidence=config.MIN_DETECTION_CONFIDENCE,
            min_tracking_confidence=config.MIN_TRACKING_CONFIDENCE,
        )

    except FileNotFoundError as error:
        print(error)
        camera.release()
        return

    # ========================================================
    # SMOOTHERS
    # ========================================================

    smoothers = [
        LandmarkSmoother(
            alpha=config.SMOOTH_ALPHA
        )
        for _ in range(config.MAX_NUM_HANDS)
    ]

    # ========================================================
    # FPS
    # ========================================================

    fps_counter = FPSCounter()

    # ========================================================
    # STATE
    # ========================================================

    mirror = config.MIRROR

    frame_counter = 0
    last_results = None

    # ========================================================
    # WINDOW
    # ========================================================

    cv2.namedWindow(
        config.WINDOW_NAME,
        cv2.WINDOW_NORMAL,
    )

    # Большое окно
    cv2.resizeWindow(
        config.WINDOW_NAME,
        900,
        650,
    )

    # ========================================================
    # MAIN LOOP
    # ========================================================

    try:
        while True:

            # ------------------------------------------------
            # CAMERA FRAME
            # ------------------------------------------------

            frame = camera.read()

            if mirror:
                frame = camera.flip(frame)

            # ------------------------------------------------
            # FPS
            # ------------------------------------------------

            fps_counter.update()

            frame_counter += 1

            # ------------------------------------------------
            # HAND DETECTION
            # ------------------------------------------------

            if (
                frame_counter
                % config.PROCESS_EVERY_N_FRAMES
                == 0
            ):
                last_results = detector.process(frame)

            results = last_results

            # ------------------------------------------------
            # HAND DATA
            # ------------------------------------------------

            handedness = get_handedness(results)

            hands_count = 0

            # ------------------------------------------------
            # DRAW HANDS
            # ------------------------------------------------

            if (
                results is not None
                and results.hand_landmarks
            ):
                hands_count = len(
                    results.hand_landmarks
                )

                for i, hand_landmarks in enumerate(
                    results.hand_landmarks
                ):

                    # На случай, если рук стало больше
                    # чем было создано smoother'ов
                    if i >= len(smoothers):
                        smoothers.append(
                            LandmarkSmoother(
                                alpha=config.SMOOTH_ALPHA
                            )
                        )

                    smoother = smoothers[i]

                    smoothed = smoother.smooth(
                        hand_landmarks
                    )

                    label = None

                    if i < len(handedness):
                        label = handedness[i]

                    # Всегда рисуем:
                    # точки + линии
                    draw_landmarks(
                        frame,
                        smoothed,
                        HAND_CONNECTIONS,
                        frame.shape[1],
                        frame.shape[0],
                        label=label,
                    )

            # ------------------------------------------------
            # UI
            # ------------------------------------------------

            draw_interface(
                frame,
                fps=fps_counter.value,
                mirror=mirror,
                hands_count=hands_count,
                handedness=handedness,
            )

            # ------------------------------------------------
            # SHOW
            # ------------------------------------------------

            cv2.imshow(
                config.WINDOW_NAME,
                frame,
            )

            # ------------------------------------------------
            # KEYBOARD
            # ------------------------------------------------

            key = cv2.waitKey(1) & 0xFF

            # Q — quit
            if key == ord("q"):
                break

            # M — mirror
            elif key == ord("m"):
                mirror = not mirror

            # S — screenshot
            elif key == ord("s"):
                save_screenshot(frame)

    except KeyboardInterrupt:
        print("\nОстановка...")

    finally:
        camera.release()
        detector.close()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
