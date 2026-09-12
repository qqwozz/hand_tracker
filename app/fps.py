import time
from collections import deque


class FPSCounter:
    def __init__(self, history_size=30):
        self.history = deque(
            maxlen=history_size
        )

        self.previous_time = time.perf_counter()

    def update(self):
        current_time = time.perf_counter()

        dt = current_time - self.previous_time
        self.previous_time = current_time

        if dt <= 0:
            return self.value

        fps = 1.0 / dt

        self.history.append(fps)

        return self.value

    @property
    def value(self):
        if not self.history:
            return 0.0

        return sum(self.history) / len(self.history)