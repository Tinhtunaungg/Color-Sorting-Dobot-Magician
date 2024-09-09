from serial.tools import list_ports
import time
import pydobot

# Step 1: List available ports and select the first one
available_ports = list_ports.comports()
print(f'Available ports: {[x.device for x in available_ports]}')
port = available_ports[0].device

# Step 2: Initialize the Dobot
device = pydobot.Dobot(port="/dev/tty.usbserial-0001")
print('Dobot initialized!')

# Define the left side coordinates for each color
left_coordinates = {
    'yellow': (181, 88, -45),
    'green': (207, 111, -45),
    'blue': (233, 135, -45),
    'red': (259, 160, -45)
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
    'yellow': -18,  # Initial height for the first stack
    'green': -18,
    'blue': -18,
    'red': -18
}

# Home coordinates
home_coordinates = (259.1344909667969, 0.0, -8.571266174316406, 0.0)

# Function to move the robot to a specific position
def move_robot(x, y, z, r=0.0):
    device.move_to(x, y, z, r=r)  # Move to specified (x, y, z) with rotation r
    time.sleep(1)  # Add a delay to allow the robot to reach the position

# Function to pick and place cubes using the suction cup and stack them
def stack_cubes():
    for color, (lx, ly, lz) in left_coordinates.items():
        # Step 1: Move to the left position to pick the cube
        print(f"Picking up {color} cube from left ({lx}, {ly}, {lz})")
        move_robot(lx, ly, lz + 10)  # Move just above the cube
        device.suck(True)  # Turn the suction on to pick the cube
        time.sleep(1)  # Wait for suction to grab the cube
        move_robot(lx, ly, lz)  # Move down to pick the cube
        
        # Step 2: Lift the cube slightly after picking it up
        move_robot(lx, ly, lz + 20)  # Lift the cube by 20mm

        # Step 3: Adjust the height for the stack on the right
        current_stack_height = stack_heights[color]
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
        stack_heights[color] -= 25  # Adjust height for next cube to be stacked (-25mm per cube)
        
        print(f"{color} cube stacked successfully at {current_stack_height}!\n")
    
    # Final Step: Move the arm to the home position after all cubes are stacked
    print("Moving the arm to the home position")
    move_robot(*home_coordinates)  # Unpack and move to the home position

# Main function to run the cube stacking process
if __name__ == "__main__":
    try:
        stack_cubes()  # Start stacking cubes
    finally:
        device.close()  # Close the connection to the Dobot after completing the task