# OpenCV Pixel Playground

A tiny local webcam app that shows what OpenCV does to an image. Press a key and
watch the live video turn gray, blur, flip, rotate, or zoom.

The point is to see that **OpenCV is very good at changing pixels and has no
idea what those pixels show.**

No cloud services, no AI models. Everything runs on your computer.

---

## Setup

You need **Python 3.11 or newer** and a webcam.

```bash
cd opencv-pixel-playground
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Run

```bash
python app.py
```

A window opens with your webcam feed. Click the window so it has focus, then
use these keys:

| Key | What happens                           |
| --- | -------------------------------------- |
| `n` | Normal color                           |
| `g` | Grayscale                              |
| `b` | Blur                                   |
| `f` | Horizontal flip (mirror)               |
| `r` | Rotate 180 degrees                     |
| `c` | Crop and zoom into the center          |
| `q` | Quit (`Esc` or closing the window also works) |

The current mode is shown in the top-left corner, and a footer along the bottom
lists every key, with the active mode highlighted.

**macOS note:** the first run may ask for camera permission. If the app says it
cannot open the webcam, allow your terminal app (Terminal, iTerm, VS Code, ...)
in **System Settings → Privacy & Security → Camera**, then run it again.

---

## How it works, in plain language

### 1. What is OpenCV?

OpenCV ("Open Source Computer Vision") is a free library of image and video
tools. It can read from cameras and files, show images in a window, and run
thousands of operations on them: change colors, blur, sharpen, resize, rotate,
find edges, and more. In this project we use it from Python.

### 2. What is a video frame?

A video is a fast slideshow. Each still picture in that slideshow is a
**frame**. A webcam typically delivers about 30 frames every second. The app
runs a simple loop:

1. grab one frame from the camera,
2. change it,
3. show it,
4. repeat.

It happens so fast that it looks like smooth, live video.

### 3. How does a webcam image become pixels?

Inside the webcam is a sensor covered in millions of tiny light detectors.
Each one measures how much red, green, or blue light hits it. The camera turns
those measurements into a grid of **pixels**, and each pixel is stored as
three numbers from 0 (none) to 255 (full).

For a 1280×720 webcam, one frame is a grid that is 720 rows tall and 1280
columns wide, with 3 numbers per pixel — about 2.7 million numbers. In Python,
OpenCV hands you that grid as a NumPy array:

```python
frame.shape   # (720, 1280, 3)  -> height, width, color channels
frame[0, 0]   # [ 34  51  60 ]  -> the top-left pixel (blue, green, red)
```

(OpenCV stores colors in **B, G, R** order rather than R, G, B — a historical
quirk.)

### 4. What can OpenCV do with those pixels?

Since an image is just a grid of numbers, every effect is just math on that
grid. Here is what each mode in `app.py` actually does:

- **Grayscale** — mixes each pixel's blue, green, and red into one brightness
  number.
- **Blur** — replaces each pixel with a weighted average of the pixels around
  it, so sharp differences get smoothed out.
- **Flip** — reverses the order of the columns, so left becomes right.
- **Rotate 180** — reverses both the rows and the columns.
- **Center zoom** — keeps only the middle part of the grid, then stretches it
  back to full size by filling in new pixels between the old ones.

The mode label itself is drawn the same way: OpenCV paints some pixels dark
and some white in the shape of letters.

### 5. Why doesn't OpenCV know there's a person, a hand, or a laptop in the image?

Because all it ever sees is the grid of numbers. To OpenCV, your face is not
"a face" — it is a patch of pixels with values like `[142, 168, 201]`. A
laptop is another patch with different values. Nothing in those numbers says
"person" or "laptop."

When you blur the image, OpenCV doesn't blur *you*; it averages numbers.
When you flip it, it doesn't flip *you*; it reorders columns. It would do
exactly the same thing to a photo of a cat, a wall, or random noise.

Recognizing *what* is in an image is a different, much harder problem. It
needs extra knowledge — usually a model trained on many labeled examples — that
connects certain pixel patterns to words like "hand" or "laptop." OpenCV can
run such models, but that knowledge does not come from OpenCV itself, and this
project intentionally does not use any.

**OpenCV handles the pixels. Understanding comes from somewhere else.**

---

## Files

```
opencv-pixel-playground/
├── app.py            # the whole app (~150 lines)
├── requirements.txt  # just opencv-python
└── README.md         # this file
```
