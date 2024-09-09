from serial.tools import list_ports
import time
import pydobot

# List available ports and select the first one
available_ports = list_ports.comports()
print(f'available ports: {[x.device for x in available_ports]}')
port = available_ports[0].device

# Initialize the Dobot
device = pydobot.Dobot(port="/dev/tty.usbserial-0001")


# Set initial home position
device.move_to(250, 0, 50, 0) 

# Define pick-up and drop-off positions for each cube
positions = [
    # Cube 1
    {
        "pickup": (180, 88, -46, 0),
        "dropoff": (180, -88, 0, 0)
    },
    # Cube 2
    {
        "pickup": (208, 113, -46, 0),  
        "dropoff": (205, -115, 0, 0)  
    },
    # Cube 3
    {
        "pickup": (233, 138 , -46, 0),  
        "dropoff": (235, -140, 0, 0)  
    }
]

# Function to pick up and drop off a cube
def move_cube(pickup_position, dropoff_position):
    # Move to directly above pick up
    device.move_to(pickup_position[0], pickup_position[1], pickup_position[2]+ 43, pickup_position[3])
    time.sleep(0.5)
    # Move to pick-up position
    
    device.move_to(*pickup_position)

    # Activate the suction cup to pick up the cube
    device.suck(True)
    time.sleep(1.5) 

    # Lift the cube slightly
    device.move_to(pickup_position[0], pickup_position[1], pickup_position[2] +150, pickup_position[3])
    time.sleep(1)
    
    # Move to the drop-off position
    device.move_to(*dropoff_position)
    time.sleep(0.7)
    # Lower the cube
    device.move_to(dropoff_position[0], dropoff_position[1], dropoff_position[2] -40, dropoff_position[3])
    time.sleep(1)

    # Deactivate the suction cup to release the cube
    device.suck(False)  
    time.sleep(1)

    # Return to the home position
    device.move_to(250, 0, 50, 0)
    time.sleep(1)

# Loop through the positions and move each cube
for position in positions:
    move_cube(position["pickup"], position["dropoff"])

# Disconnect from Dobot
device.close()
