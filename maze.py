from machine import Pin, I2C
import esp32_s3
import ssd1306
import random
import time
from complexbutton import ComplexButton

esp = esp32_s3.ESP32_S3(r=42, y=41, g=40, ldr=4, sw=2, sda=48, scl=47, PWM_FREQ=5000)
tm = ComplexButton()

# Maze patterns (4x4 grid with movement constraints)
maze_patterns = [
    [  # Pattern 0
        [0b0001, 0b0011, 0b0011, 0b0100],
        [0b0001, 0b0011, 0b0110, 0b1100],
        [0b0001, 0b0110, 0b1101, 0b1010],
        [0b0001, 0b1011, 0b1011, 0b0010]
    ],
    [  # Pattern 1
        [0b0101, 0b0011, 0b0111, 0b0110],
        [0b1001, 0b0110, 0b1100, 0b1000],
        [0b0101, 0b1110, 0b1101, 0b0010],
        [0b1000, 0b1000, 0b1001, 0b0010]
    ],
    [  # Pattern 2
        [0b0100, 0b0101, 0b0010, 0b0100],
        [0b1001, 0b1110, 0b0101, 0b1110],
        [0b0100, 0b1101, 0b1010, 0b1100],
        [0b1001, 0b1010, 0b0001, 0b1010]
    ],
    [  # Pattern 3
        [0b0101, 0b0011, 0b0110, 0b0100],
        [0b1001, 0b0010, 0b1101, 0b1010],
        [0b0101, 0b0011, 0b1110, 0b0100],
        [0b1000, 0b0001, 0b1011, 0b1010]
    ],
    [  # Pattern 4
        [0b0101, 0b0011, 0b0111, 0b0110],
        [0b1101, 0b0010, 0b1000, 0b1000],
        [0b1001, 0b0111, 0b0111, 0b0010],
        [0b0001, 0b1010, 0b1001, 0b0010]
    ],
    [  # Pattern 5
        [0b0100, 0b0101, 0b0011, 0b0110],
        [0b1001, 0b1110, 0b0101, 0b1010],
        [0b0101, 0b1010, 0b1001, 0b0110],
        [0b1001, 0b0011, 0b0010, 0b1000]
    ],
]

recog_patterns = {
    0: ((1,0), (2,1)),
    1: ((3,0), (0,1)),
    2: ((3,1), (0,3)),
    3: ((2,1), (2,3)),
    4: ((0,2), (3,2)),
    5: ((2,0), (3,3))
}

# Randomly choose a maze pattern
rand = random.randint(0, 5)
maze = maze_patterns[rand]
recog = recog_patterns[rand]

# Randomly select start and end points
def get_random_positions():
    while True:
        start = (random.randint(0, 1), random.randint(0, 1)) # Upper left corner if possible
        end = (random.randint(2, 3), random.randint(2, 3)) # Bottom RIght corner if possible
        if start != end:
            return start, end

(player_x, player_y), (goal_x, goal_y) = get_random_positions()

# Movement directions
DIRECTIONS = {
    (0, -1): 0b1000,  # Up (Decrease Y)
    (0, 1): 0b0100,   # Down (Increase Y)
    (-1, 0): 0b0010,  # Left (Decrease X)
    (1, 0): 0b0001   # Right (Increase X)
}

# Check if movement is valid
def can_move(new_x, new_y):
    global player_x, player_y
    
    dx, dy = new_x - player_x, new_y - player_y

    if (dx, dy) not in DIRECTIONS:  # Can only move 1 step
        return False

    possible_move = DIRECTIONS[(dx, dy)]
    return (maze[player_y][player_x] & possible_move) != 0

# Move player if valid
def move_to(new_x, new_y):
    global player_x, player_y

    if can_move(new_x, new_y):
        player_x, player_y = new_x, new_y
        update_display()

        if (player_x, player_y) == (goal_x, goal_y):
            print("You reached the goal!")
    else:
        esp.oled.text("Invalid", 70, 20, 1)
        esp.oled.text("move!", 80, 30, 1)
        esp.oled.show()
        print("Invalid move!")

# Update OLED display
def update_display():
    esp.oled.fill(0)  # Clear screen

    # Define cell size and margin for positioning
    cell_size = 16
    margin = 8  # Offset for centering the grid

    # Draw the 4x4 grid and handle player, goal, and recog patterns
    for row in range(4):
        for col in range(4):
            x, y = col * cell_size + margin, row * cell_size + margin  # Centered position for each cell

            # If the current cell is the goal
            if (col, row) == (goal_x, goal_y):
                esp.oled.text("X", x-2, y-2, 1)  # Draw "X" for the goal
                
            elif (col, row) == (player_x, player_y):
                esp.oled.fill_rect(x - 4, y - 4, 12, 12, 1)  # Draw a filled rectangle for the player
            
            # Draw the grid cell (dot for empty cells)
            else:
                esp.oled.fill_rect(x, y, 4, 4, 1)  # Small dot for each cell

            # Draw an ellipse (simulating a circle) around cells that match recog_patterns
            for pattern in recog:
                if (col, row) == pattern:
                    # Draw ellipse with equal width and height to simulate a circle
                    esp.oled.ellipse(x + 2, y + 2, 7, 7, 1)  # Width and height are the same for a circle

    esp.oled.show()  # Update the OLED display


# Game loop to read user input
def game_loop():
    print(f'rand = {rand}')
    print(f'recog = {recog}')
    print(f'Start:({player_x},{player_y})\nEnd:({goal_x},{goal_y})')
    update_display()  # Initial render
    
    xy = tm.get_xy()
    old_xy = xy
    while True:
        xy = tm.get_xy()
        if xy and xy != old_xy:
            old_xy = xy
            try:
                new_x, new_y = xy
                if 0 <= new_x < 4 and 0 <= new_y < 4:
                    move_to(new_x, new_y)
                    if (player_x, player_y) == (goal_x, goal_y):
                        esp.oled.fill(0)
                        esp.oled.text("Congratulations!", 0, 32, 1)
                        esp.oled.show()
                        break
                else:
                    print("Out of bounds!")
            except Exception:
                print("Invalid input! Use format: row,col (e.g., 1,2)")
            

# Start game loop
game_loop()
