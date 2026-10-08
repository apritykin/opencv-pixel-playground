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

import sys  # used for printing errors to stderr and for the exit code

import cv2  # OpenCV: reads the webcam, changes pixels, draws, shows the window
import numpy as np  # OpenCV frames are NumPy arrays; imported for type hints

# The text shown in the title bar of the window.
WINDOW_NAME = "OpenCV Pixel Playground"

# Map each key to the mode it switches on. The order here is also the order
# the keys are listed in the footer.
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
        # (The image still looks gray: all three channels now hold the same number.)
        return cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)

    if mode == "Blur":
        # Replace each pixel with a weighted average of its neighbors.
        # (31, 31) is the size of the neighborhood in pixels (must be odd);
        # a bigger number means a stronger blur. The 0 lets OpenCV choose the
        # spread of the weights automatically.
        return cv2.GaussianBlur(frame, (31, 31), 0)

    if mode == "Flip":
        # 1 = flip around the vertical axis (left <-> right), like a mirror.
        return cv2.flip(frame, 1)

    if mode == "Rotate 180":
        # Reverses both the rows and the columns, so the image is upside down.
        return cv2.rotate(frame, cv2.ROTATE_180)

    if mode == "Center Zoom":
        # Keep the middle half of the image, then stretch it back to full size.
        height, width = frame.shape[:2]  # shape is (height, width, channels)
        # Start a quarter of the way in from the top and left edges...
        top, left = height // 4, width // 4
        # ...and keep half the height and half the width. This is NumPy slicing:
        # frame[rows, columns] picks out a rectangle of the pixel grid.
        center = frame[top : top + height // 2, left : left + width // 2]
        # Stretch the smaller grid back to the original size. OpenCV has to
        # invent new pixels in between; INTER_LINEAR fills them by averaging
        # the nearest original pixels. Note that resize takes (width, height).
        return cv2.resize(center, (width, height), interpolation=cv2.INTER_LINEAR)

    return frame  # "Normal": leave the pixels untouched.


# Font and colors used for the on-screen text.
FONT = cv2.FONT_HERSHEY_SIMPLEX
WHITE = (255, 255, 255)
GRAY = (170, 170, 170)
YELLOW = (0, 220, 255)  # OpenCV colors are (blue, green, red)


def darken(frame: np.ndarray, top_left, bottom_right) -> None:
    """Blend a dark rectangle over part of the frame so text on it is readable."""
    # Work on a copy so we can mix the original and the dark version together.
    overlay = frame.copy()
    # Paint a solid black rectangle on the copy (FILLED = not just an outline).
    cv2.rectangle(overlay, top_left, bottom_right, (0, 0, 0), cv2.FILLED)
    # Mix the two images 50/50 and write the result back into `frame`.
    # Only the rectangle differs between them, so only that area gets darker.
    cv2.addWeighted(overlay, 0.5, frame, 0.5, 0, dst=frame)


def draw_label(frame: np.ndarray, mode: str) -> None:
    """Draw a small mode label in the top-left corner and a key-help footer."""
    height, width = frame.shape[:2]
    # Size text relative to the frame so it looks the same on 720p and 1080p.
    scale = max(0.4, width / 1280 * 0.55)  # font size multiplier
    thickness = 1 if width < 1600 else 2  # stroke width of the letters
    pad = max(6, int(10 * width / 1280))  # breathing room around text, in pixels

    # --- Mode label (top-left) ---
    # Measure the text first so the dark box behind it fits exactly.
    # getTextSize returns ((text_width, text_height), space_below_baseline).
    (text_w, text_h), baseline = cv2.getTextSize(mode, FONT, scale, thickness)
    # putText positions text by its bottom-left corner, so y is the text's bottom.
    x, y = pad * 2, pad * 2 + text_h
    darken(frame, (x - pad, y - text_h - pad), (x + text_w + pad, y + baseline + pad // 2))
    # LINE_AA = anti-aliased, which smooths the jagged edges of the letters.
    cv2.putText(frame, mode, (x, y), FONT, scale, WHITE, thickness, cv2.LINE_AA)

    # --- Footer: one entry per key, with the current mode highlighted ---
    # Each entry is (key, name, is_this_the_active_mode).
    entries = [(key, name, name == mode) for key, name in MODES.items()]
    entries.append(("q", "Quit", False))

    # Measure a tall sample ("Ag" has both a capital and a descender) to get the
    # height of one line of text, then darken a strip across the whole bottom.
    (_, text_h), baseline = cv2.getTextSize("Ag", FONT, scale, thickness)
    footer_top = height - text_h - baseline - pad * 2
    darken(frame, (0, footer_top), (width, height))

    x = pad * 2  # where the next piece of text starts, moving left to right
    y = height - baseline - pad  # the footer text's baseline
    gap = pad * 3  # space between one entry and the next
    for key, name, active in entries:
        # Draw the key in yellow, like "[g] "...
        key_text = f"[{key}] "
        cv2.putText(frame, key_text, (x, y), FONT, scale, YELLOW, thickness, cv2.LINE_AA)
        # ...then move x right by the width of what we just drew.
        x += cv2.getTextSize(key_text, FONT, scale, thickness)[0][0]

        # Draw the mode name: white if active, gray otherwise.
        cv2.putText(frame, name, (x, y), FONT, scale, WHITE if active else GRAY, thickness, cv2.LINE_AA)
        # Move right again, plus a gap, ready for the next entry.
        x += cv2.getTextSize(name, FONT, scale, thickness)[0][0] + gap


def main() -> int:
    """Open the webcam and run the grab -> change -> show loop until quit."""
    camera = cv2.VideoCapture(0)  # 0 = the default webcam
    if not camera.isOpened():
        # Most common causes: another app has the camera, or permission is off.
        print(
            "Could not open the webcam.\n"
            "  - Is another app using it?\n"
            "  - On macOS, allow camera access for your terminal in\n"
            "    System Settings > Privacy & Security > Camera.",
            file=sys.stderr,
        )
        return 1  # a non-zero exit code tells the shell something went wrong

    # AUTOSIZE: the window fits the frame size exactly and can't be resized.
    cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_AUTOSIZE)
    mode = "Normal"  # the app starts with no effect applied
    print("Running. Press n / g / b / f / r / c to change mode, q to quit.")

    # try/finally guarantees the camera is released even if something crashes.
    try:
        while True:
            ok, frame = camera.read()  # one frame = one still image
            if not ok:
                print("Lost the webcam feed.", file=sys.stderr)
                break

            # Change the pixels, draw the labels on top, and show the result.
            # The label is drawn after the effect so it is never blurred/flipped.
            output = apply_mode(frame, mode)
            draw_label(output, mode)
            cv2.imshow(WINDOW_NAME, output)

            # Wait ~1 ms for a key press; this also lets the window repaint.
            # waitKey returns -1 if no key was pressed; `& 0xFF` keeps only the
            # lowest 8 bits, which turns -1 into 255 and gives plain key codes.
            key = cv2.waitKey(1) & 0xFF
            # Convert the key code to a lowercase letter ("" if nothing pressed),
            # so both "g" and "G" work.
            char = chr(key).lower() if key != 255 else ""

            if char == "q" or key == 27:  # 27 = Esc
                break
            if char in MODES:
                mode = MODES[char]  # switch effect; takes hold on the next frame

            # Stop if the user closed the window with the mouse.
            if cv2.getWindowProperty(WINDOW_NAME, cv2.WND_PROP_VISIBLE) < 1:
                break
    finally:
        camera.release()  # give the webcam back to the system
        cv2.destroyAllWindows()  # close the display window

    return 0  # success


# Only run main() when this file is executed directly (python app.py),
# not when it is imported by another script.
if __name__ == "__main__":
    sys.exit(main())  # pass main()'s return value on as the exit code
