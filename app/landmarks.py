HAND_CONNECTIONS = [
    (0, 1), (1, 2), (2, 3), (3, 4),       # Thumb
    (0, 5), (5, 6), (6, 7), (7, 8),       # Index
    (0, 9), (9, 10), (10, 11), (11, 12),  # Middle
    (0, 13), (13, 14), (14, 15), (15, 16),# Ring
    (0, 17), (17, 18), (18, 19), (19, 20),# Pinky
    (5, 9), (9, 13), (13, 17),            # Palm
]

FINGER_NAMES = {
    4: "Thumb",
    8: "Index",
    12: "Middle",
    16: "Ring",
    20: "Pinky",
}

FINGER_TIPS = {
    "Thumb": 4,
    "Index": 8,
    "Middle": 12,
    "Ring": 16,
    "Pinky": 20,
}

WRIST = 0