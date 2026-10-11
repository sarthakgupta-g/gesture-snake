# Gesture Snake

Play the classic Snake game with your hand! Your webcam tracks your index finger
using MediaPipe and OpenCV, and the snake turns to follow it.

## How to play

- Hold your hand up to the camera.
- Keep your index finger inside the white box to go straight.
- Move your finger up, down, left, or right of the box to turn.
- Press `R` to restart and `Q` to quit.

## Setup

1. Make sure you have Python 3.9+ installed.
2. Clone this repo:
```
   git clone https://github.com/YOUR-USERNAME/gesture-snake.git
   cd gesture-snake
```
3. Install the dependencies:
```
   pip install -r requirements.txt
```
4. Run the game:
```
   python gesture_snake.py
```

## Tweaking

At the top of `gesture_snake.py` you can change:

- `MOVE_DELAY` - snake speed (smaller = faster)
- `DEAD_ZONE` - how far your finger must move to steer
- `GRID` / `CELL` - board size

## Built with

- [OpenCV](https://opencv.org/)
- [MediaPipe](https://developers.google.com/mediapipe)
