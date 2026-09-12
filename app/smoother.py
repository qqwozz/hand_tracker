from dataclasses import dataclass


@dataclass
class SmoothedPoint:
    x: float
    y: float
    z: float


class LandmarkSmoother:
    def __init__(self, alpha=0.3):
        if not 0 < alpha <= 1:
            raise ValueError("alpha должен быть в диапазоне (0, 1]")
        self.alpha = alpha
        self.prev = None

    def smooth(self, landmarks):
        if not landmarks:
            self.reset()
            return []
        # Первый кадр
        if self.prev is None:
            self.prev = [
                (lm.x, lm.y, lm.z)
                for lm in landmarks
            ]
            return [
                SmoothedPoint(lm.x, lm.y, lm.z)
                for lm in landmarks
            ]
        smoothed = []
        for i, lm in enumerate(landmarks):
            # Если количество landmarks изменилось
            if i >= len(self.prev):
                point = SmoothedPoint(
                    lm.x,
                    lm.y,
                    lm.z,
                )
                smoothed.append(point)
                continue
            prev_x, prev_y, prev_z = self.prev[i]
            x = (
                self.alpha * lm.x
                + (1 - self.alpha) * prev_x
            )
            y = (
                self.alpha * lm.y
                + (1 - self.alpha) * prev_y
            )
            z = (
                self.alpha * lm.z
                + (1 - self.alpha) * prev_z
            )
            smoothed.append(
                SmoothedPoint(x, y, z)
            )

        self.prev = [
            (point.x, point.y, point.z)
            for point in smoothed
        ]

        return smoothed

    def reset(self):
        self.prev = None