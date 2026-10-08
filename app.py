"""OpenCV Pixel Playground.

A tiny webcam app that shows what OpenCV does to an image: it moves, mixes,
and reshapes pixels. It never "understands" what those pixels depict.

Keys:
    n  normal color
    g  grayscale
    b  blur
    f  horizontal flip
    r  rotate 180 degrees
    c  crop / zoom into the center
    q  quit (Esc also works)
"""

import sys

import cv2
import numpy as np

WINDOW_NAME = "OpenCV Pixel Playground"

# Map each key to the mode it switches on.
MODES = {
    "n": "Normal",
    "g": "Grayscale",
    "b": "Blur",
    "f": "Flip",
    "r": "Rotate 180",
    "c": "Center Zoom",
}


def apply_mode(frame: np.ndarray, mode: str) -> np.ndarray:
    """Return a new frame with the selected pixel operation applied.

    `frame` is a NumPy array of shape (height, width, 3): one blue, green,
    and red number (0-255) per pixel. Every mode is just math on that grid.
    """
    if mode == "Grayscale":
        # Combine B, G, R into a single brightness value per pixel...
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        # ...then copy it back into 3 channels so the colored label still works.
        return cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)

    if mode == "Blur":
        # Replace each pixel with a weighted average of its neighbors.
        return cv2.GaussianBlur(frame, (31, 31), 0)

    if mode == "Flip":
        # 1 = flip around the vertical axis (left <-> right), like a mirror.
        return cv2.flip(frame, 1)

    if mode == "Rotate 180":
        return cv2.rotate(frame, cv2.ROTATE_180)

    if mode == "Center Zoom":
        # Keep the middle half of the image, then stretch it back to full size.
        height, width = frame.shape[:2]
        top, left = height // 4, width // 4
        center = frame[top : top + height // 2, left : left + width // 2]
        return cv2.resize(center, (width, height), interpolation=cv2.INTER_LINEAR)

    return frame  # "Normal": leave the pixels untouched.


FONT = cv2.FONT_HERSHEY_SIMPLEX
WHITE = (255, 255, 255)
GRAY = (170, 170, 170)
YELLOW = (0, 220, 255)  # OpenCV colors are (blue, green, red)


def darken(frame: np.ndarray, top_left, bottom_right) -> None:
    """Blend a dark rectangle over part of the frame so text on it is readable."""
    overlay = frame.copy()
    cv2.rectangle(overlay, top_left, bottom_right, (0, 0, 0), cv2.FILLED)
    cv2.addWeighted(overlay, 0.5, frame, 0.5, 0, dst=frame)


def draw_label(frame: np.ndarray, mode: str) -> None:
    """Draw a small mode label in the top-left corner and a key-help footer."""
    height, width = frame.shape[:2]
    # Size text relative to the frame so it looks the same on 720p and 1080p.
    scale = max(0.4, width / 1280 * 0.55)
    thickness = 1 if width < 1600 else 2
    pad = max(6, int(10 * width / 1280))

    # --- Mode label (top-left) ---
    (text_w, text_h), baseline = cv2.getTextSize(mode, FONT, scale, thickness)
    x, y = pad * 2, pad * 2 + text_h
    darken(frame, (x - pad, y - text_h - pad), (x + text_w + pad, y + baseline + pad // 2))
    cv2.putText(frame, mode, (x, y), FONT, scale, WHITE, thickness, cv2.LINE_AA)

    # --- Footer: one entry per key, with the current mode highlighted ---
    entries = [(key, name, name == mode) for key, name in MODES.items()]
    entries.append(("q", "Quit", False))

    (_, text_h), baseline = cv2.getTextSize("Ag", FONT, scale, thickness)
    footer_top = height - text_h - baseline - pad * 2
    darken(frame, (0, footer_top), (width, height))

    x = pad * 2
    y = height - baseline - pad
    gap = pad * 3
    for key, name, active in entries:
        key_text = f"[{key}] "
        cv2.putText(frame, key_text, (x, y), FONT, scale, YELLOW, thickness, cv2.LINE_AA)
        x += cv2.getTextSize(key_text, FONT, scale, thickness)[0][0]

        cv2.putText(frame, name, (x, y), FONT, scale, WHITE if active else GRAY, thickness, cv2.LINE_AA)
        x += cv2.getTextSize(name, FONT, scale, thickness)[0][0] + gap


def main() -> int:
    camera = cv2.VideoCapture(0)  # 0 = the default webcam
    if not camera.isOpened():
        print(
            "Could not open the webcam.\n"
            "  - Is another app using it?\n"
            "  - On macOS, allow camera access for your terminal in\n"
            "    System Settings > Privacy & Security > Camera.",
            file=sys.stderr,
        )
        return 1

    cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_AUTOSIZE)
    mode = "Normal"
    print("Running. Press n / g / b / f / r / c to change mode, q to quit.")

    try:
        while True:
            ok, frame = camera.read()  # one frame = one still image
            if not ok:
                print("Lost the webcam feed.", file=sys.stderr)
                break

            output = apply_mode(frame, mode)
            draw_label(output, mode)
            cv2.imshow(WINDOW_NAME, output)

            # Wait ~1 ms for a key press; this also lets the window repaint.
            key = cv2.waitKey(1) & 0xFF
            char = chr(key).lower() if key != 255 else ""

            if char == "q" or key == 27:  # 27 = Esc
                break
            if char in MODES:
                mode = MODES[char]

            # Stop if the user closed the window with the mouse.
            if cv2.getWindowProperty(WINDOW_NAME, cv2.WND_PROP_VISIBLE) < 1:
                break
    finally:
        camera.release()
        cv2.destroyAllWindows()

    return 0


if __name__ == "__main__":
    sys.exit(main())
