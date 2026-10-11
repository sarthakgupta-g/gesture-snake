"""
Gesture-Controlled Snake
------------------------
Point your INDEX FINGER up/down/left/right of the center of the camera
view to steer the snake.
 
Install first:   pip install opencv-python mediapipe
Run:             python gesture_snake.py
Keys:            q = quit, r = restart
"""
 
import random
import time
 
import cv2
import mediapipe as mp
 
# ---------- SETTINGS (feel free to tweak!) ----------
GRID = 20             # the board is GRID x GRID squares
CELL = 25             # size of each square in pixels
SIZE = GRID * CELL    # board is SIZE x SIZE pixels
MOVE_DELAY = 0.15     # seconds between snake moves (smaller = faster)
DEAD_ZONE = 0.12      # how far from center your finger must move to steer
 
# Colors in OpenCV are (Blue, Green, Red)
BLACK = (0, 0, 0)
GREEN = (80, 220, 80)
DARK_GREEN = (40, 140, 40)
RED = (60, 60, 240)
WHITE = (255, 255, 255)
 
# Directions are (x change, y change)
UP, DOWN, LEFT, RIGHT = (0, -1), (0, 1), (-1, 0), (1, 0)
 
 
# ---------- GAME HELPERS ----------
def new_game():
    """Create a fresh game state."""
    start = (GRID // 2, GRID // 2)
    return {
        "snake": [start, (start[0] - 1, start[1]), (start[0] - 2, start[1])],
        "direction": RIGHT,
        "food": place_food([start]),
        "score": 0,
        "alive": True,
    }
 
 
def place_food(snake):
    """Pick a random empty square for the food."""
    while True:
        spot = (random.randint(0, GRID - 1), random.randint(0, GRID - 1))
        if spot not in snake:
            return spot
 
 
def direction_from_finger(fx, fy, current):
    """
    Turn the finger position (0-1 range, center = 0.5) into a direction.
    Returns the current direction if the finger is in the 'dead zone'
    or if the move would make the snake reverse into itself.
    """
    dx = fx - 0.5
    dy = fy - 0.5
 
    # Finger is near the center: don't change anything
    if max(abs(dx), abs(dy)) < DEAD_ZONE:
        return current
 
    # Whichever axis the finger moved further on wins
    if abs(dx) > abs(dy):
        new = RIGHT if dx > 0 else LEFT
    else:
        new = DOWN if dy > 0 else UP
 
    # Don't allow a 180-degree turn (the snake would hit itself)
    opposite = (-current[0], -current[1])
    if new == opposite:
        return current
    return new
 
 
def step(game):
    """Move the snake one square forward and handle eating / crashing."""
    head_x, head_y = game["snake"][0]
    dx, dy = game["direction"]
    new_head = (head_x + dx, head_y + dy)
 
    # Crashed into a wall or into itself?
    hit_wall = not (0 <= new_head[0] < GRID and 0 <= new_head[1] < GRID)
    hit_self = new_head in game["snake"]
    if hit_wall or hit_self:
        game["alive"] = False
        return
 
    game["snake"].insert(0, new_head)  # add new head
 
    if new_head == game["food"]:
        game["score"] += 1
        game["food"] = place_food(game["snake"])
    else:
        game["snake"].pop()  # remove tail (so the snake doesn't grow)
 
 
# ---------- DRAWING ----------
def draw_board(game):
    """Draw the game and return it as an image."""
    board = BLACK_IMAGE.copy()
 
    # Food
    fx, fy = game["food"]
    cv2.rectangle(board, (fx * CELL, fy * CELL),
                  ((fx + 1) * CELL - 1, (fy + 1) * CELL - 1), RED, -1)
 
    # Snake (head is a brighter green)
    for i, (x, y) in enumerate(game["snake"]):
        color = GREEN if i == 0 else DARK_GREEN
        cv2.rectangle(board, (x * CELL, y * CELL),
                      ((x + 1) * CELL - 1, (y + 1) * CELL - 1), color, -1)
 
    # Score
    cv2.putText(board, f"Score: {game['score']}", (10, 25),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, WHITE, 2)
 
    # Game over message
    if not game["alive"]:
        cv2.putText(board, "GAME OVER", (SIZE // 2 - 110, SIZE // 2),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.2, RED, 3)
        cv2.putText(board, "Press R to restart", (SIZE // 2 - 100, SIZE // 2 + 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, WHITE, 2)
    return board
 
 
def draw_camera_overlay(frame, finger_pos):
    """Draw the center box and a dot on your fingertip on the camera image."""
    h, w, _ = frame.shape
 
    # Dead zone box in the center
    x1 = int((0.5 - DEAD_ZONE) * w)
    x2 = int((0.5 + DEAD_ZONE) * w)
    y1 = int((0.5 - DEAD_ZONE) * h)
    y2 = int((0.5 + DEAD_ZONE) * h)
    cv2.rectangle(frame, (x1, y1), (x2, y2), WHITE, 2)
 
    # Dot on the fingertip
    if finger_pos is not None:
        px, py = int(finger_pos[0] * w), int(finger_pos[1] * h)
        cv2.circle(frame, (px, py), 12, GREEN, -1)
    return frame
 
 
# ---------- MAIN PROGRAM ----------
BLACK_IMAGE = cv2.UMat(SIZE, SIZE, cv2.CV_8UC3).get() * 0  # blank black board
 
 
def main():
    # Set up MediaPipe hand tracking
    hands = mp.solutions.hands.Hands(
        max_num_hands=1,
        min_detection_confidence=0.6,
        min_tracking_confidence=0.6,
    )
 
    camera = cv2.VideoCapture(0)  # 0 = your default webcam
    if not camera.isOpened():
        print("Could not open the webcam. Is another app using it?")
        return
 
    game = new_game()
    last_move = time.time()
 
    while True:
        ok, frame = camera.read()
        if not ok:
            break
 
        frame = cv2.flip(frame, 1)  # mirror so left is left
        frame = cv2.resize(frame, (SIZE, SIZE))
 
        # MediaPipe wants RGB, OpenCV gives BGR
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb)
 
        # Find the index fingertip (landmark number 8)
        finger_pos = None
        if results.multi_hand_landmarks:
            tip = results.multi_hand_landmarks[0].landmark[8]
            finger_pos = (tip.x, tip.y)
 
        # Steer the snake based on the finger
        if finger_pos is not None and game["alive"]:
            game["direction"] = direction_from_finger(
                finger_pos[0], finger_pos[1], game["direction"]
            )
 
        # Move the snake on a timer
        if game["alive"] and time.time() - last_move > MOVE_DELAY:
            step(game)
            last_move = time.time()
 
        # Draw everything side by side: game on the left, camera on the right
        board = draw_board(game)
        camera_view = draw_camera_overlay(frame, finger_pos)
        cv2.imshow("Gesture Snake", cv2.hconcat([board, camera_view]))
 
        # Keyboard controls
        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            break
        if key == ord("r"):
            game = new_game()
            last_move = time.time()
 
    camera.release()
    cv2.destroyAllWindows()
 
 
if __name__ == "__main__":
    main()
 
