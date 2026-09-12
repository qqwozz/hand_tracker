import cv2


BLACK = (8, 8, 8)
WHITE = (245, 245, 245)
GRAY = (145, 145, 145)
DARK_GRAY = (55, 55, 55)
GREEN = (170, 220, 185)


def put_text(image, text, position, size=0.45, color=WHITE, thickness=1):
    cv2.putText(
        image, text, position,
        cv2.FONT_HERSHEY_SIMPLEX,
        size, color, thickness, cv2.LINE_AA
    )


def line(image, x1, y1, x2, y2, color=WHITE, thickness=1):
    cv2.line(
        image, (x1, y1), (x2, y2),
        color, thickness, cv2.LINE_AA
    )


def draw_landmarks(
    image,
    hand_landmarks,
    connections,
    width,
    height,
    label=None,
):
    points = [
        (int(p.x * width), int(p.y * height))
        for p in hand_landmarks
    ]

    for start, end in connections:
        if start < len(points) and end < len(points):
            line(
                image,
                *points[start],
                *points[end],
                WHITE,
                2,
            )

    for i, point in enumerate(points):
        radius = 5 if i == 0 else 4

        cv2.circle(image, point, radius, BLACK, -1, cv2.LINE_AA)
        cv2.circle(image, point, radius, WHITE, 1, cv2.LINE_AA)


def draw_header(image, width):
    line(image, 28, 25, 28, 62)

    put_text(image, "HAND TRACKER", (40, 43), 0.55)
    put_text(image, "COMPUTER VISION", (40, 60), 0.28, GRAY)

    x = width - 85
    cv2.circle(image, (x, 34), 3, GREEN, -1, cv2.LINE_AA)
    put_text(image, "LIVE", (x + 10, 39), 0.32, GRAY)


def draw_info(image, fps, hands_count, handedness):
    y = 88

    put_text(image, f"{fps:.0f} FPS", (30, y), 0.32, GRAY)
    line(image, 92, y - 13, 92, y + 3, DARK_GRAY)

    hands = f"{hands_count} HAND" if hands_count == 1 else f"{hands_count} HANDS"
    put_text(image, hands, (108, y), 0.32, GRAY)

    if handedness:
        line(image, 205, y - 13, 205, y + 3, DARK_GRAY)
        labels = " / ".join(x.upper() for x in handedness)
        put_text(image, labels, (220, y), 0.32, GRAY)


def draw_corner_frame(image):
    height, width = image.shape[:2]
    m, length = 18, 16

    corners = [
        (m, m, 1, 1),
        (width - m, m, -1, 1),
        (m, height - m, 1, -1),
        (width - m, height - m, -1, -1),
    ]

    for x, y, dx, dy in corners:
        line(image, x, y, x + dx * length, y, DARK_GRAY)
        line(image, x, y, x, y + dy * length, DARK_GRAY)


def draw_bottom(image, mirror):
    height, width = image.shape[:2]
    y = height - 28

    state = "ON" if mirror else "OFF"
    put_text(image, f"M MIRROR {state}", (30, y), 0.30, GRAY)

    text = "Q QUIT"
    size = cv2.getTextSize(
        text,
        cv2.FONT_HERSHEY_SIMPLEX,
        0.30,
        1,
    )[0]

    put_text(image, text, (width - size[0] - 30, y), 0.30, GRAY)


def draw_detection_status(image, hands_count):
    height, width = image.shape[:2]

    status = "TRACKING" if hands_count else "SEARCHING"
    color = WHITE if hands_count else GRAY

    size = cv2.getTextSize(
        status,
        cv2.FONT_HERSHEY_SIMPLEX,
        0.30,
        1,
    )[0]

    x = width - size[0] - 30
    y = height - 52

    cv2.circle(
        image,
        (x - 10, y - 5),
        3,
        color,
        -1,
        cv2.LINE_AA,
    )

    put_text(image, status, (x, y), 0.30, color)


def draw_interface(
    image,
    fps,
    mirror,
    hands_count,
    handedness,
    mode=4,
):
    height, width = image.shape[:2]

    draw_corner_frame(image)
    draw_header(image, width)
    draw_info(image, fps, hands_count, handedness)
    draw_detection_status(image, hands_count)
    draw_bottom(image, mirror)