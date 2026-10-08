# Build Prompt: OpenCV Pixel Playground

> Copy everything below the line into your coding agent (Claude Code, Cursor,
> Codex, etc.) from inside an empty folder. The agent should build the whole
> project from this description.

---

## Goal

Build **OpenCV Pixel Playground**: a small local Python app that opens the
webcam in a window and lets the user press keys to switch between simple
pixel effects (grayscale, blur, flip, rotate, center zoom).

It's a teaching project. It should show that **OpenCV is very good at
changing pixels and has no idea what those pixels show.** Keep it small,
readable, and beginner-friendly. No cloud services, no AI or ML models, no
network calls. Everything runs locally.

## Constraints

- **Language:** Python 3.11+
- **Dependencies:** only `opencv-python>=4.8` (NumPy comes with it). Put
  exactly that in `requirements.txt`.
- **Files:** exactly three:
  ```
  opencv-pixel-playground/
  ├── app.py            # the whole app, ~150 lines
  ├── requirements.txt  # opencv-python>=4.8
  └── README.md         # setup, usage, plain-language explanation
  ```
- Don't add frameworks, config files, classes, CLI argument parsing, or extra
  modules. One script, plain functions.
- Comment for a beginner: short comments that say what the pixel math does
  (e.g. "Replace each pixel with a weighted average of its neighbors").

## `app.py` specification

### Module docstring
Describe the app in one or two sentences (it moves, mixes, and reshapes
pixels and never "understands" them), then list the keys.

### Constants
- `WINDOW_NAME = "OpenCV Pixel Playground"`
- `MODES`: an ordered dict that maps key to mode name:
  | Key | Mode name     |
  |-----|---------------|
  | `n` | `Normal`      |
  | `g` | `Grayscale`   |
  | `b` | `Blur`        |
  | `f` | `Flip`        |
  | `r` | `Rotate 180`  |
  | `c` | `Center Zoom` |
- Font `cv2.FONT_HERSHEY_SIMPLEX`. Colors in **BGR** order: `WHITE
  (255,255,255)`, `GRAY (170,170,170)`, `YELLOW (0,220,255)`. Add a comment
  noting that OpenCV colors are (blue, green, red).

### `apply_mode(frame, mode) -> np.ndarray`
Returns a new frame with the effect applied. The docstring explains that the
frame is a `(height, width, 3)` NumPy array of 0–255 BGR values and that every
mode is just math on that grid.
- **Grayscale:** `cvtColor` BGR→GRAY, then GRAY→BGR so the image still has 3
  channels and the colored overlay text still works.
- **Blur:** `cv2.GaussianBlur(frame, (31, 31), 0)`.
- **Flip:** `cv2.flip(frame, 1)` (mirror left/right).
- **Rotate 180:** `cv2.rotate(frame, cv2.ROTATE_180)`.
- **Center Zoom:** slice out the middle half
  (`frame[h//4 : h//4 + h//2, w//4 : w//4 + w//2]`), then
  `cv2.resize` it back to `(w, h)` with `INTER_LINEAR`.
- **Normal / anything else:** return the frame unchanged.

### `darken(frame, top_left, bottom_right) -> None`
Copy the frame, draw a filled black rectangle on the copy, then blend it back
in place with `cv2.addWeighted(overlay, 0.5, frame, 0.5, 0, dst=frame)`. This
gives a semi-transparent backing so the text is readable.

### `draw_label(frame, mode) -> None`
Draws on the frame in place. Size everything relative to the frame width so
it looks the same at 720p and 1080p:
- `scale = max(0.4, width / 1280 * 0.55)`
- `thickness = 1 if width < 1600 else 2`
- `pad = max(6, int(10 * width / 1280))`

1. **Mode label (top-left):** measure the text with `cv2.getTextSize`, place
   it at `(pad*2, pad*2 + text_h)`, call `darken` on a padded box behind it,
   then draw it in white with `cv2.LINE_AA`.
2. **Footer (bottom edge, full width):** build entries for every mode plus
   `("q", "Quit")`. Darken a strip across the bottom, sized from the height
   of `"Ag"`. For each entry draw `"[key] "` in yellow, then the name in
   **white if it's the active mode, gray otherwise**. Move x forward by each
   measured text width, plus a gap of `pad*3` between entries.

### `main() -> int`
1. `cv2.VideoCapture(0)`. If it doesn't open, print a helpful message to
   stderr and return `1`. The message should ask whether another app is
   using the camera, and on macOS point to *System Settings > Privacy &
   Security > Camera*.
2. Create the window with `cv2.WINDOW_AUTOSIZE`. Start in `"Normal"` and
   print a one-line usage hint.
3. Loop inside `try/finally`:
   - Read a frame. If the read fails, print "Lost the webcam feed." to stderr
     and break.
   - `output = apply_mode(frame, mode)`, then `draw_label(output, mode)`,
     then `cv2.imshow`.
   - `key = cv2.waitKey(1) & 0xFF`. Turn it into a lowercase char, using
     `""` when key is 255 (no key pressed).
   - Quit on `q` or Esc (27). If the char is in `MODES`, switch to that mode.
   - Also quit if the user closed the window with the mouse
     (`cv2.getWindowProperty(WINDOW_NAME, cv2.WND_PROP_VISIBLE) < 1`).
4. In the `finally` block: `camera.release()` and `cv2.destroyAllWindows()`.
   Return `0`.

Close the file with `if __name__ == "__main__": sys.exit(main())`.

## `README.md` specification

Write it for a non-expert. Sections:

1. **Title and intro:** what the app does and the core point (OpenCV changes
   pixels and doesn't know what they show). Mention there are no cloud
   services or AI models.
2. **Setup:** needs Python 3.11+ and a webcam. Commands: create a `.venv`,
   activate it (include the Windows variant), `pip install -r
   requirements.txt`.
3. **Run:** `python app.py`, plus a key table (n/g/b/f/r/c/q, noting that Esc
   or closing the window also quits). Mention the top-left label and the
   footer with the active mode highlighted. Add a **macOS camera permission
   note**.
4. **How it works, in plain language,** with these subsections:
   1. What is OpenCV?
   2. What is a video frame? (a fast slideshow at ~30 fps; the
      grab → change → show → repeat loop)
   3. How does a webcam image become pixels? (sensor → grid of 0–255 RGB
      values; for 1280×720 that's ~2.7M numbers; show `frame.shape` →
      `(720, 1280, 3)` and `frame[0, 0]`; mention the BGR quirk)
   4. What can OpenCV do with those pixels? (one plain sentence per mode
      describing the math; note the label text is also just painted pixels)
   5. Why doesn't OpenCV know there's a person, a hand, or a laptop in the
      image? (it only sees numbers; blurring averages numbers, it doesn't
      blur *you*; recognition needs a trained model, which this project
      deliberately doesn't use). End with the bolded line: **"OpenCV
      handles the pixels. Understanding comes from somewhere else."**
5. **Files:** a small tree of the three files.

## Done when

- [ ] `pip install -r requirements.txt` works in a fresh venv
- [ ] `python -c "import ast; ast.parse(open('app.py').read())"` passes
- [ ] `apply_mode` returns a frame of the **same shape** as its input for
      every mode. Check this headless with a dummy
      `np.zeros((720, 1280, 3), np.uint8)`.
- [ ] `draw_label` runs on that dummy frame without errors
- [ ] `python app.py` opens the webcam window, every key switches modes, and
      q / Esc / closing the window exits cleanly. *(This is a manual check
      that needs a real camera. If you're an agent without one, say so
      instead of claiming it passed.)*
- [ ] `app.py` stays around 150 lines and has no dependencies beyond OpenCV
      and NumPy
