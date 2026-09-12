# MediaPipe Hand Landmarks
#
# 0  - Wrist
#
# Thumb:
# 1  - CMC
# 2  - MCP
# 3  - IP
# 4  - Tip
#
# Index:
# 5  - MCP
# 6  - PIP
# 7  - DIP
# 8  - Tip
#
# Middle:
# 9  - MCP
# 10 - PIP
# 11 - DIP
# 12 - Tip
#
# Ring:
# 13 - MCP
# 14 - PIP
# 15 - DIP
# 16 - Tip
#
# Pinky:
# 17 - MCP
# 18 - PIP
# 19 - DIP
# 20 - Tip


HAND_CONNECTIONS = [
    # Thumb
    (0, 1),
    (1, 2),
    (2, 3),
    (3, 4),

    # Index
    (0, 5),
    (5, 6),
    (6, 7),
    (7, 8),

    # Middle
    (0, 9),
    (9, 10),
    (10, 11),
    (11, 12),

    # Ring
    (0, 13),
    (13, 14),
    (14, 15),
    (15, 16),

    # Pinky
    (0, 17),
    (17, 18),
    (18, 19),
    (19, 20),

    # Palm
    (5, 9),
    (9, 13),
    (13, 17),
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