import cv2


# ============================================================
# COLORS
# ============================================================

BLACK = (8, 8, 8)
WHITE = (245, 245, 245)
GRAY = (145, 145, 145)
DARK_GRAY = (55, 55, 55)
GREEN = (170, 220, 185)


# ============================================================
# TEXT
# ============================================================

def put_text(
    image,
    text: str,
    position,
    size: float = 0.45,
    color=WHITE,
    thickness: int = 1,
):
    cv2.putText(
        image,
        text,
        position,
        cv2.FONT_HERSHEY_SIMPLEX,
        size,
        color,
        thickness,
        cv2.LINE_AA,
    )


# ============================================================
# THIN LINE
# ============================================================

def line(
    image,
    x1: int,
    y1: int,
    x2: int,
    y2: int,
    color=WHITE,
    thickness: int = 1,
):
    cv2.line(
        image,
        (x1, y1),
        (x2, y2),
        color,
        thickness,
        cv2.LINE_AA,
    )


# ============================================================
# LANDMARKS
# ============================================================

def draw_landmarks(
    image,
    hand_landmarks,
    connections,
    width: int,
    height: int,
    label: str | None = None,
):
    """
    Минималистичная отрисовка руки:
    только линии + точки.
    """

    points = []

    for landmark in hand_landmarks:
        x = int(landmark.x * width)
        y = int(landmark.y * height)

        points.append((x, y))

    # --------------------------------------------------------
    # HAND SKELETON
    # --------------------------------------------------------

    for start, end in connections:

        if start >= len(points) or end >= len(points):
            continue

        cv2.line(
            image,
            points[start],
            points[end],
            WHITE,
            2,
            cv2.LINE_AA,
        )

    # --------------------------------------------------------
    # LANDMARK POINTS
    # --------------------------------------------------------

    for index, point in enumerate(points):

        # Большая точка для wrist
        if index == 0:
            radius = 5
        else:
            radius = 4

        cv2.circle(
            image,
            point,
            radius,
            BLACK,
            -1,
            cv2.LINE_AA,
        )

        cv2.circle(
            image,
            point,
            radius,
            WHITE,
            1,
            cv2.LINE_AA,
        )


# ============================================================
# HEADER
# ============================================================

def draw_header(
    image,
    width: int,
    height: int,
):
    """
    Очень минимальный header.
    """

    # маленькая вертикальная линия
    line(
        image,
        28,
        25,
        28,
        62,
        WHITE,
        1,
    )

    put_text(
        image,
        "HAND TRACKER",
        (40, 43),
        0.55,
        WHITE,
        1,
    )

    put_text(
        image,
        "COMPUTER VISION",
        (40, 60),
        0.28,
        GRAY,
        1,
    )

    # LIVE

    live_x = width - 85

    cv2.circle(
        image,
        (live_x, 34),
        3,
        GREEN,
        -1,
        cv2.LINE_AA,
    )

    put_text(
        image,
        "LIVE",
        (live_x + 10, 39),
        0.32,
        GRAY,
        1,
    )


# ============================================================
# TOP INFORMATION
# ============================================================

def draw_info(
    image,
    fps: float,
    hands_count: int,
    handedness: list[str],
):
    """
    Минимальная информация сверху.
    """

    height, width = image.shape[:2]

    y = 88

    # FPS

    put_text(
        image,
        f"{fps:.0f} FPS",
        (30, y),
        0.32,
        GRAY,
        1,
    )

    # separator

    line(
        image,
        92,
        y - 13,
        92,
        y + 3,
        DARK_GRAY,
    )

    # hands

    hand_text = (
        f"{hands_count} HAND"
        if hands_count == 1
        else f"{hands_count} HANDS"
    )

    put_text(
        image,
        hand_text,
        (108, y),
        0.32,
        GRAY,
        1,
    )

    # Handedness

    if handedness:

        separator_x = 205

        line(
            image,
            separator_x,
            y - 13,
            separator_x,
            y + 3,
            DARK_GRAY,
        )

        labels = " / ".join(
            label.upper()
            for label in handedness
        )

        put_text(
            image,
            labels,
            (220, y),
            0.32,
            GRAY,
            1,
        )


# ============================================================
# CORNER FRAME
# ============================================================

def draw_corner_frame(
    image,
):
    """
    Очень тонкие угловые маркеры.
    """

    height, width = image.shape[:2]

    margin = 18
    length = 16

    # top left
    line(
        image,
        margin,
        margin,
        margin + length,
        margin,
        DARK_GRAY,
    )

    line(
        image,
        margin,
        margin,
        margin,
        margin + length,
        DARK_GRAY,
    )

    # top right
    line(
        image,
        width - margin,
        margin,
        width - margin - length,
        margin,
        DARK_GRAY,
    )

    line(
        image,
        width - margin,
        margin,
        width - margin,
        margin + length,
        DARK_GRAY,
    )

    # bottom left
    line(
        image,
        margin,
        height - margin,
        margin + length,
        height - margin,
        DARK_GRAY,
    )

    line(
        image,
        margin,
        height - margin,
        margin,
        height - margin - length,
        DARK_GRAY,
    )

    # bottom right
    line(
        image,
        width - margin,
        height - margin,
        width - margin - length,
        height - margin,
        DARK_GRAY,
    )

    line(
        image,
        width - margin,
        height - margin,
        width - margin,
        height - margin - length,
        DARK_GRAY,
    )


# ============================================================
# BOTTOM INFO
# ============================================================

def draw_bottom(
    image,
    mirror: bool,
):
    """
    Минимальная нижняя строка.
    """

    height, width = image.shape[:2]

    y = height - 28

    # left

    mirror_state = "ON" if mirror else "OFF"

    put_text(
        image,
        f"M MIRROR {mirror_state}",
        (30, y),
        0.30,
        GRAY,
        1,
    )

    # right

    quit_text = "Q QUIT"

    text_size = cv2.getTextSize(
        quit_text,
        cv2.FONT_HERSHEY_SIMPLEX,
        0.30,
        1,
    )[0]

    put_text(
        image,
        quit_text,
        (width - text_size[0] - 30, y),
        0.30,
        GRAY,
        1,
    )


# ============================================================
# DETECTION STATUS
# ============================================================

def draw_detection_status(
    image,
    hands_count: int,
):
    """
    Небольшой индикатор состояния.
    """

    height, width = image.shape[:2]

    if hands_count > 0:
        status = "TRACKING"
        color = WHITE
    else:
        status = "SEARCHING"
        color = GRAY

    text_size = cv2.getTextSize(
        status,
        cv2.FONT_HERSHEY_SIMPLEX,
        0.30,
        1,
    )[0]

    x = width - text_size[0] - 30
    y = height - 52

    cv2.circle(
        image,
        (x - 10, y - 5),
        3,
        color,
        -1,
        cv2.LINE_AA,
    )

    put_text(
        image,
        status,
        (x, y),
        0.30,
        color,
        1,
    )


# ============================================================
# MAIN INTERFACE
# ============================================================

def draw_interface(
    image,
    fps: float,
    mirror: bool,
    hands_count: int,
    handedness: list[str],
    mode: int = 4,
):
    """
    Полностью минималистичный CV dashboard.

    mode оставлен в сигнатуре для совместимости
    с main.py, но больше нигде не используется.
    """

    height, width = image.shape[:2]

    # тонкие угловые маркеры
    draw_corner_frame(image)

    # header
    draw_header(
        image,
        width,
        height,
    )

    # metrics
    draw_info(
        image,
        fps,
        hands_count,
        handedness,
    )

    # status
    draw_detection_status(
        image,
        hands_count,
    )

    # bottom
    draw_bottom(
        image,
        mirror,
    )