import os

import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python.vision import (
    HandLandmarker,
    HandLandmarkerOptions,
)


class HandsDetector:
    def __init__(
        self,
        model_path,
        max_num_hands=2,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5,
    ):
        self.model_path = model_path
        self.max_num_hands = max_num_hands
        self.min_detection_confidence = min_detection_confidence
        self.min_tracking_confidence = min_tracking_confidence

        self.detector = None

        self._init_detector()

    def _init_detector(self):
        if not os.path.exists(self.model_path):
            raise FileNotFoundError(
                f"Модель '{self.model_path}' не найдена.\n"
                "Скачайте её по адресу:\n"
                "https://storage.googleapis.com/"
                "mediapipe-models/hand_landmarker/"
                "hand_landmarker/float16/1/"
                "hand_landmarker.task"
            )

        options = HandLandmarkerOptions(
            base_options=python.BaseOptions(
                model_asset_path=self.model_path
            ),
            num_hands=self.max_num_hands,
            min_hand_detection_confidence=self.min_detection_confidence,
            min_tracking_confidence=self.min_tracking_confidence,
        )

        self.detector = HandLandmarker.create_from_options(options)

    def process(self, frame):
        rgb = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2RGB
        )

        mp_image = mp.Image(
            image_format=mp.ImageFormat.SRGB,
            data=rgb,
        )

        return self.detector.detect(mp_image)

    def close(self):
        if self.detector is not None:
            self.detector.close()
            self.detector = None