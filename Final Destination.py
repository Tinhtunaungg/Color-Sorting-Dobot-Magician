import cv2
import numpy as np
import time
from serial.tools import list_ports
import pydobot

# Define refined color ranges in HSV space for red, green, blue, and yellow
color_ranges = {
    'r': [(0, 120, 70), (10, 255, 255)],  # Red
    'g': [(35, 100, 100), (85, 255, 255)],  # Green
    'b': [(90, 100, 100), (130, 255, 255)],  # Blue
    'y': [(20, 100, 100), (30, 255, 255)]  # Yellow
}

# Function to detect color objects
def detect_color_objects(frame, color_abbreviation, lower_bound, upper_bound):
    hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv_frame, np.array(lower_bound), np.array(upper_bound))

    # Morphological operations
    kernel = np.ones((12, 12), np.uint8)
    mask = cv2.erode(mask, kernel, iterations=2)

    # Find contours
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    objects_positions = []

    for contour in contours:
        area = cv2.contourArea(contour)
        if area > 500:  # Filter small objects
            x, y, w, h = cv2.boundingRect(contour)
            aspect_ratio = float(w) / h
            if 0.75 <= aspect_ratio <= 1.25:  # Nearly square shapes
                cx, cy = x + w // 2, y + h // 2
                if cx < frame.shape[1] // 2:  # Left half of the frame
                    objects_positions.append((cx, cy, color_abbreviation))
    return objects_positions

# Function to move the robot to a specific position
def move_robot(x, y, z, r=0.0):
    device.move_to(x, y, z, r=r)
    time.sleep(1)

# Function to pick and place cubes using the suction cup
def stack_cubes(color_sequence):
    for i, color in enumerate(color_sequence):
        cube_name = f'L-cube{i + 1}'
        lx, ly, lz = left_coordinates[cube_name]
        if color not in right_coordinates:
            print(f"Invalid color for {cube_name}. Skipping.")
            continue

        # Move to the left position
        move_robot(lx, ly, lz + 10)
        device.suck(True)  # Pick up the cube
        time.sleep(1)
        move_robot(lx, ly, lz)
        move_robot(lx, ly, lz + 20)

        # Calculate current stack height
        current_stack_height = right_coordinates[color][2] + (stack_heights[color] * 25)
        print(f"Placing {color} cube at {current_stack_height}")

        # Move to the right stack position
        rx, ry, _ = right_coordinates[color]
        move_robot(rx, ry, current_stack_height + 25)
        move_robot(rx, ry, current_stack_height)
        device.suck(False)  # Release the cube
        time.sleep(1)
        move_robot(rx, ry, current_stack_height + 20)

        # Update stack height
        stack_heights[color] += 1

    # Return to home
    move_robot(*home_coordinates)

# Main function to integrate color detection and robotic arm movement
def main():
    cap = cv2.VideoCapture(0)
    
    available_ports = list_ports.comports()
    port = available_ports[0].device
    global device
    device = pydobot.Dobot(port="/dev/tty.usbserial-0001")

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            detected_objects = []

            for color_abbreviation, (lower_bound, upper_bound) in color_ranges.items():
                objects = detect_color_objects(frame, color_abbreviation, lower_bound, upper_bound)
                detected_objects.extend(objects)

            # Sort by y-coordinate (bottom to top)
            detected_objects.sort(key=lambda pos: pos[1], reverse=True)

            # Get the color sequence
            color_order = [color_abbreviation for _, _, color_abbreviation in detected_objects[:4]]

            if color_order:
                color_sequence = [color_map[color] for color in color_order]
                stack_cubes(color_sequence)
                break  # Stop after stacking the detected cubes

    finally:
        cap.release()
        cv2.destroyAllWindows()
        device.close()

if __name__ == "__main__":
    # Define the necessary coordinates and maps here
    left_coordinates = {
        'L-cube1': (181, 88, -46),
        'L-cube2': (207, 111, -46),
        'L-cube3': (233, 135, -46),
        'L-cube4': (259, 160, -46)
    }
    right_coordinates = {
        'yellow': (209, -114, -18),
        'green': (234, -140, -18),
        'blue': (183, -90, -18),
        'red': (260, -165, -18)
    }
    stack_heights = {
        'yellow': 0,
        'green': 0,
        'blue': 0,
        'red': 0
    }
    home_coordinates = (259.1344909667969, 0.0, -8.571266174316406, 0.0)
    color_map = {'y': 'yellow', 'g': 'green', 'b': 'blue', 'r': 'red'}
    
    main()
