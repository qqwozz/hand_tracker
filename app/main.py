import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python.vision import HandLandmarker, HandLandmarkerOptions
import os
import time
import numpy as np

# ============================
#  КЛАСС ДЛЯ СГЛАЖИВАНИЯ КООРДИНАТ
# ============================
class LandmarkSmoother:
    def __init__(self, alpha=0.3):
        self.alpha = alpha
        self.prev = None

    def smooth(self, landmarks):
        """
        Принимает список объектов Landmark (с полями x, y, z).
        Возвращает список сглаженных координат (в виде простых объектов с атрибутами x, y, z).
        """
        if self.prev is None:
            self.prev = [(lm.x, lm.y, lm.z) for lm in landmarks]
            return landmarks  # возвращаем оригинал, но сохраняем

        smoothed = []
        for i, lm in enumerate(landmarks):
            px, py, pz = self.prev[i]
            x = self.alpha * lm.x + (1 - self.alpha) * px
            y = self.alpha * lm.y + (1 - self.alpha) * py
            z = self.alpha * lm.z + (1 - self.alpha) * pz
            # Создаём простой объект с атрибутами
            class SmoothedPoint:
                pass
            pt = SmoothedPoint()
            pt.x = x
            pt.y = y
            pt.z = z
            smoothed.append(pt)
        self.prev = [(pt.x, pt.y, pt.z) for pt in smoothed]
        return smoothed

# ============================
#  ОБЁРТКА ДЛЯ MEDIAPIPE
# ============================
class HandsWrapper:
    def __init__(self, max_num_hands=2, min_detection_confidence=0.5, min_tracking_confidence=0.5):
        self.max_num_hands = max_num_hands
        self.min_detection_confidence = min_detection_confidence
        self.min_tracking_confidence = min_tracking_confidence
        self.detector = None
        self._init_detector()

    def _init_detector(self):
        model_path = 'hand_landmarker.task'
        if not os.path.exists(model_path):
            raise FileNotFoundError(
                f"Модель {model_path} не найдена! Скачайте её по ссылке: "
                "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task"
            )
        options = HandLandmarkerOptions(
            base_options=python.BaseOptions(model_asset_path=model_path),
            num_hands=self.max_num_hands,
            min_hand_detection_confidence=self.min_detection_confidence,
            min_tracking_confidence=self.min_tracking_confidence
        )
        self.detector = HandLandmarker.create_from_options(options)

    def process(self, image):
        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
        return self.detector.detect(mp_image)

    def close(self):
        if self.detector:
            self.detector.close()

# ============================
#  ОТРИСОВКА
# ============================
# Соединения (стандартные)
HAND_CONNECTIONS = [
    (0,1), (1,2), (2,3), (3,4),
    (0,5), (5,6), (6,7), (7,8),
    (0,9), (9,10), (10,11), (11,12),
    (0,13), (13,14), (14,15), (15,16),
    (0,17), (17,18), (18,19), (19,20),
    (5,9), (9,13), (13,17)
]

# Названия пальцев (кончики)
FINGER_NAMES = {
    4: "Thumb",
    8: "Index",
    12: "Middle",
    16: "Ring",
    20: "Pinky"
}

def draw_landmarks(frame, landmarks, connections,
                   show_skeleton=True, show_points=True, show_labels=True,
                   skeleton_color=(255,255,255), point_color=(0,0,0),
                   label_color=(255,255,255)):
    h, w, _ = frame.shape
    # Нормируем размеры точек и толщину линий относительно размера кадра
    point_radius = max(3, int(min(w, h) / 200))
    line_thickness = max(1, int(min(w, h) / 300))

    if show_skeleton and connections:
        for connection in connections:
            start_idx, end_idx = connection
            if start_idx < len(landmarks) and end_idx < len(landmarks):
                start = landmarks[start_idx]
                end = landmarks[end_idx]
                x1, y1 = int(start.x * w), int(start.y * h)
                x2, y2 = int(end.x * w), int(end.y * h)
                cv2.line(frame, (x1, y1), (x2, y2), skeleton_color, line_thickness)

    if show_points:
        for idx, lm in enumerate(landmarks):
            x, y = int(lm.x * w), int(lm.y * h)
            cv2.circle(frame, (x, y), point_radius, point_color, -1)

    if show_labels:
        for idx, name in FINGER_NAMES.items():
            if idx < len(landmarks):
                lm = landmarks[idx]
                x, y = int(lm.x * w), int(lm.y * h)
                cv2.putText(frame, name, (x + 10, y - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, label_color, 2)

# ============================
#  ГЛАВНАЯ ФУНКЦИЯ
# ============================
def main():
    # --- Параметры ---
    PROCESS_EVERY_N_FRAMES = 2   # обрабатывать каждый 2-й кадр (1 – все)
    SMOOTH_ALPHA = 0.3           # степень сглаживания (0..1)

    # --- Инициализация камеры ---
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Ошибка: не удалось открыть камеру")
        return

    # --- Инициализация детектора ---
    detector = HandsWrapper(max_num_hands=2)

    # --- Инициализация сглаживателя (для каждой руки отдельно) ---
    # Будем хранить сглаживатели в словаре по индексу руки? 
    # Но удобнее просто создавать один сглаживатель на все руки, 
    # или массив. Так как у нас может быть 2 руки, создадим список сглаживателей.
    smoothers = [LandmarkSmoother(alpha=SMOOTH_ALPHA) for _ in range(2)]

    # --- Переменные состояния ---
    mirror = True
    show_skeleton = True
    show_points = True
    show_labels = True
    # Режим: 1 – скелет, 2 – точки, 3 – подписи, 4 – всё
    mode = 4

    # --- Переменные для FPS ---
    fps = 0
    prev_time = time.time()
    frame_counter = 0

    print("=== Трекер рук с улучшениями ===")
    print("Управление:")
    print("  M - зеркало вкл/выкл")
    print("  S - сохранить скриншот")
    print("  1 - только скелет")
    print("  2 - только точки")
    print("  3 - только подписи")
    print("  4 - всё вместе")
    print("  Q - выход")

    while True:
        success, frame = cap.read()
        if not success:
            break

        # Зеркало
        if mirror:
            frame = cv2.flip(frame, 1)

        # Текущее время для FPS
        current_time = time.time()
        dt = current_time - prev_time
        if dt > 0:
            fps = 1.0 / dt
        prev_time = current_time

        # Обработка только каждый N-й кадр
        frame_counter += 1
        results = None
        if frame_counter % PROCESS_EVERY_N_FRAMES == 0:
            results = detector.process(frame)
            # Сохраняем результаты в переменную, чтобы использовать в промежуточных кадрах
            last_results = results
        else:
            # Используем последний обработанный результат
            results = last_results if 'last_results' in locals() else None

        # Если есть результаты, применяем сглаживание и рисуем
        if results and results.hand_landmarks:
            for i, hand_landmarks in enumerate(results.hand_landmarks):
                # Сглаживание для каждой руки
                smoother = smoothers[i] if i < len(smoothers) else LandmarkSmoother(alpha=SMOOTH_ALPHA)
                if i >= len(smoothers):
                    smoothers.append(LandmarkSmoother(alpha=SMOOTH_ALPHA))
                smoothed = smoother.smooth(hand_landmarks)

                # Определяем режим отображения
                sk = show_skeleton
                pts = show_points
                lbls = show_labels
                if mode == 1:
                    sk, pts, lbls = True, False, False
                elif mode == 2:
                    sk, pts, lbls = False, True, False
                elif mode == 3:
                    sk, pts, lbls = False, False, True
                else:
                    sk, pts, lbls = True, True, True

                draw_landmarks(
                    frame, smoothed, HAND_CONNECTIONS,
                    show_skeleton=sk,
                    show_points=pts,
                    show_labels=lbls,
                    skeleton_color=(255,255,255),
                    point_color=(0,0,0),
                    label_color=(255,255,255)
                )

        # --- Отрисовка информации на экране ---
        # FPS
        cv2.putText(frame, f"FPS: {int(fps)}", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (200, 200, 200), 2)
        # Режим и зеркало
        mode_text = f"Mode: {mode} ({'Skeleton' if mode==1 else 'Points' if mode==2 else 'Labels' if mode==3 else 'All'})"
        cv2.putText(frame, mode_text, (10, 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 2)
        cv2.putText(frame, f"Mirror: {'ON' if mirror else 'OFF'}", (10, 90),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 2)

        # --- Показ ---
        cv2.imshow('Hand Tracker (Enhanced)', frame)

        # --- Обработка клавиш ---
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('m'):
            mirror = not mirror
        elif key == ord('s'):
            timestamp = int(time.time())
            filename = f"hand_{timestamp}.png"
            cv2.imwrite(filename, frame)
            print(f"Скриншот сохранён как {filename}")
        elif key == ord('1'):
            mode = 1
        elif key == ord('2'):
            mode = 2
        elif key == ord('3'):
            mode = 3
        elif key == ord('4'):
            mode = 4

    cap.release()
    cv2.destroyAllWindows()
    detector.close()

if __name__ == "__main__":
    main()