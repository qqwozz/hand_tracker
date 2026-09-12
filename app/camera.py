import cv2


class Camera:
    def __init__(self, camera_index=0):
        self.camera_index = camera_index
        self.cap = cv2.VideoCapture(camera_index)

        if not self.cap.isOpened():
            raise RuntimeError(
                f"Не удалось открыть камеру с индексом {camera_index}"
            )

    def read(self):
        success, frame = self.cap.read()

        if not success:
            raise RuntimeError("Не удалось получить кадр с камеры")

        return frame

    def release(self):
        if self.cap:
            self.cap.release()

    def flip(self, frame):
        return cv2.flip(frame, 1)