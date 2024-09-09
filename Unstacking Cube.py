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

# Function to pick and place cubes using the suction cup and unstack them
def unstack_cubes():
    for color, (rx, ry, rz) in right_coordinates.items():
        # Step 1: Move to the right position to pick the cube from the stack
        current_stack_height = stack_heights[color]
        print(f"Picking up {color} cube from right stack at height {current_stack_height}")
        
        # Move just above the cube
        move_robot(rx, ry, current_stack_height + 10)
        
        # Here, we move slightly lower than the top of the cube to grab it
        move_robot(rx, ry, current_stack_height - 5)  # Go down 5mm lower to ensure a good grip
        
        # Turn the suction on to pick the cube
        device.suck(True)  
        time.sleep(1)  # Wait for suction to grab the cube
        
        # Step 2: Lift the cube slightly after picking it up
        move_robot(rx, ry, current_stack_height + 20)  # Lift the cube by 20mm

        # Step 3: Move to the left position to place the cube back
        lx, ly, lz = left_coordinates[color]
        print(f"Placing {color} cube back on left at ({lx}, {ly}, {lz})")
        move_robot(lx, ly, lz + 25)  # Move above the left position
        move_robot(lx, ly, lz)  # Lower to the original left position
        
        # Step 4: Release the cube
        device.suck(False)  # Turn off the suction to release the cube
        time.sleep(1)  # Wait for the cube to be placed
        
        # Step 5: Lift the arm slightly after placing the cube to avoid disturbing it
        move_robot(lx, ly, lz + 20)  # Lift the arm by 20mm
        
        # Update the stack height for the next cube to be unstacked
        stack_heights[color] -= 25  # Adjust height for unstacking (-25mm per cube)
        
        print(f"{color} cube returned to original position on the left!\n")
    
    # Final Step: Move the arm to the home position after all cubes are unstacked
    print("Moving the arm to the home position")
    move_robot(*home_coordinates)  # Unpack and move to the home position

# Main function to run the cube unstacking process
if __name__ == "__main__":
    try:
        unstack_cubes()  # Start unstacking cubes
    finally:
        device.close()  # Close the connection to the Dobot after completing the task