import time
from serial.tools import list_ports
import pydobot

# Step 1: List available ports and select the first one
available_ports = list_ports.comports()
print(f'Available ports: {[x.device for x in available_ports]}')
port = available_ports[0].device

# Step 2: Initialize the Dobot
device = pydobot.Dobot(port="/dev/tty.usbserial-0001")
print('Dobot initialized!')

# Define the left side coordinates for each cube
left_coordinates = {
    'L-cube1': (181, 88, -45),
    'L-cube2': (207, 111, -45),
    'L-cube3': (233, 135, -45),
    'L-cube4': (259, 160, -45)
}

# Define the right side coordinates for each color (initial stacking z = -18)
right_coordinates = {
    'yellow': (209, -114, -18),  # Target z = -18 for initial stack height
    'green': (234, -140, -18),
    'blue': (183, -90, -18),
    'red': (260, -165, -18)
}

# Keep track of the number of cubes stacked for each color to adjust the z-axis
stack_heights = {
    'yellow': 0,  # Initial height for the first stack (0 cubes stacked)
    'green': 0,
    'blue': 0,
    'red': 0
}

# Home coordinates
home_coordinates = (259.1344909667969, 0.0, -8.571266174316406, 0.0)

# Map of short inputs to full color names
color_map = {
    'y': 'yellow',
    'g': 'green',
    'b': 'blue',
    'r': 'red'
}

# Function to move the robot to a specific position
def move_robot(x, y, z, r=0.0):
    device.move_to(x, y, z, r=r)  # Move to specified (x, y, z) with rotation r
    time.sleep(1)  # Add a delay to allow the robot to reach the position

# Function to pick and place cubes using the suction cup and stack them
def stack_cubes(color_sequence):
    for i, color in enumerate(color_sequence):
        cube_name = f'L-cube{i + 1}'
        lx, ly, lz = left_coordinates[cube_name]
        if color not in right_coordinates:
            print(f"Invalid color entered for {cube_name}. Skipping this cube.")
            continue

        # Step 1: Move to the left position to pick the cube
        print(f"Picking up {color} cube from left ({lx}, {ly}, {lz})")
        move_robot(lx, ly, lz + 10)  # Move just above the cube
        device.suck(True)  # Turn the suction on to pick the cube
        time.sleep(1)  # Wait for suction to grab the cube
        move_robot(lx, ly, lz)  # Move down to pick the cube
        
        # Step 2: Lift the cube slightly after picking it up
        move_robot(lx, ly, lz + 20)  # Lift the cube by 20mm

        # Step 3: Calculate the current stack height for the color
        current_stack_height = right_coordinates[color][2] + (stack_heights[color] * 25)
        print(f"Placing {color} cube on the right stack at height {current_stack_height}")
        
        # Step 4: Move to the right position to place the cube
        rx, ry, _ = right_coordinates[color]
        move_robot(rx, ry, current_stack_height + 25)  # Move above the stack position
        move_robot(rx, ry, current_stack_height)  # Lower to the current stacking height
        
        # Step 5: Release the cube
        device.suck(False)  # Turn off the suction to release the cube
        time.sleep(1)  # Wait for the cube to be placed
        
        # Step 6: Lift the arm slightly after placing the cube to avoid disturbing it
        move_robot(rx, ry, current_stack_height + 20)  # Lift the arm by 20mm
        
        # Update the stack height for the next cube
        stack_heights[color] += 1  # Increment the number of cubes stacked for this color
        
        print(f"{color} cube stacked successfully at {current_stack_height}!\n")
    
    # Final Step: Move the arm to the home position after all cubes are stacked
    print("Moving the arm to the home position")
    move_robot(*home_coordinates)  # Unpack and move to the home position

# Main function to collect input and run the cube stacking process
if __name__ == "__main__":
    # Collect all color inputs in one command
    input_str = input("Enter the colors for all cubes (e.g., b,g,b,g): ").strip().lower()
    short_color_sequence = input_str.split(',')
    
    # Convert short colors to full color names
    color_sequence = []
    for short_color in short_color_sequence:
        if short_color in color_map:
            color_sequence.append(color_map[short_color])
        else:
            print(f"Invalid color code '{short_color}' entered. Skipping this input.")
            continue

    # Validate that the number of colors does not exceed the number of cubes
    if len(color_sequence) > len(left_coordinates):
        print(f"Too many colors entered. Only the first {len(left_coordinates)} will be processed.")
        color_sequence = color_sequence[:len(left_coordinates)]

    if len(color_sequence) == 0:
        print("No valid colors entered. Exiting.")
    else:
        try:
            stack_cubes(color_sequence)  # Start stacking cubes after all inputs are collected
        finally:
            device.close()  # Close the connection to the Dobot after completing the task