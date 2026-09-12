class Config:
    # Камера
    CAMERA_INDEX = 0

    # MediaPipe
    MAX_NUM_HANDS = 2
    MIN_DETECTION_CONFIDENCE = 0.5
    MIN_TRACKING_CONFIDENCE = 0.5

    # Обработка кадров
    PROCESS_EVERY_N_FRAMES = 2

    # Сглаживание
    SMOOTH_ALPHA = 0.3

    # Отображение
    MIRROR = True
    SHOW_SKELETON = True
    SHOW_POINTS = True
    SHOW_LABELS = True

    # 1 — скелет
    # 2 — точки
    # 3 — подписи
    # 4 — всё
    DISPLAY_MODE = 4

    # Окно
    WINDOW_NAME = "Hand Tracker"

    # Модель
    MODEL_PATH = "hand_landmarker.task"