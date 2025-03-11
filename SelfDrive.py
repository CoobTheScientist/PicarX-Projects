from picarx import Picarx
from vilib import Vilib
import time
import numpy as np
import math

# Global variables initialized for the map, direction of the car, distances, and bool to only stop at the stop sign once. 
SIZE = 20
CM = 15.0  
grid = np.zeros((SIZE, SIZE), dtype=np.uint8)
position = [10, 10]
facing = 0
GoodDistance = 40   
BadDistance  = 25   
StopFlag = False

# Helper to determine the direction  the car is facing. 0 degrees = straight. 90 = right. 180 = backwards. 270 = left.
def direct(direction):
    return direction * 90

# Here we use a line algorithm for determining where we essentially determine where to put the '1' in the grid
# if an obstacle is seen
# !!!!!!!!!!! This code was derived from https://mathematica.stackexchange.com/questions/45753/bresenhams-line-algorithm !!!!!!!!!!!!!!!
def line_algo(x1, y1, x2, y2):
    points = []
    diffx = abs(x2 - x1)
    diffy = abs(y2 - y1)
    
    #set left or right increment
    if x1 < x2:
        leftRightx = 1  
    else: -1
    if y1 < y2: 
        leftRighty = 1
    else: -1
    
    if diffx > diffy: 
        where = diffx - diffy 
    else: diffy - diffx

    x, y = x1, y1
    while True:
        points.append((x, y))
        if x == x2 and y == y2:
            break
        e2 = 2 * where
        if diffx > diffy:
            if e2 > -diffy:
                where -= diffy
                x += leftRightx
            if e2 < diffx:
                where += diffx
                y += leftRighty
        else:
            if e2 > -diffx:
                where -= diffx
                y += leftRighty
            if e2 < diffy:
                where += diffy
                x += leftRightx
    return points

#Function to mark 0s and 1s on the mapping grid. 1s represent an obstacle, 0s represent free of any osbtacles
def create_grid(distance, PanAngle):
    global grid, position, facing

    degree = direct(facing) + PanAngle
    rad = math.radians(degree)
    cell = distance / CM
    #Here we essentially set where the obstacle is detected in relation to the car (row an col of the grid)
    #then call the line algo function to draw the line
    row = round(cell * math.cos(rad))
    col = round(cell * math.sin(rad))
    stright = position[0] - row
    LeftOrRight = position[1] + col
    line = line_algo(position[0], position[1], stright, LeftOrRight)

    # set all other points as free on the grid(0)
    # then see if the obstacle is within the good distance set.
    for (ro, co) in line[:-1]:
        if 0 <= ro < SIZE and 0 <= co < SIZE:
            grid[ro, co] = 0
    r, c = line[-1]

    if distance < GoodDistance:
        if 0 <= r < SIZE and 0 <= c < SIZE:
            grid[r, c] = 1

# Funtion to scan with the ultrasonic sensor after every move. A new grid map is created each time we scan.
def keep_scanning(car):
    #sets the max angles to pan, and the amount of steps each iteration.
    for angle in range(-50, 50 + 1, 10):
        car.set_cam_pan_angle(angle)
        time.sleep(0.07)
        dist = car.ultrasonic.read()
        #create grid map again
        if dist is None or dist < 0:
            dist = 999
        create_grid(dist, angle)
    car.set_cam_pan_angle(0)

#function to print the grid map to console
def print():
    for row in grid:
        for item in row:
            print(item, end="")
            print()
    print("----------------------------------------")

#Function to add some "padding" around the 1s in a grid. This helps to not get close to any obstacles we see
## !!! THis was based on a somewhat similar robotics program I found online (stack overflow). *I cannot find the link anymore :(*!!!!
def add_pad(cells, pad=1):
    copy = np.copy(cells)
    #loop through all cells in the grid mapp
    for row in range(SIZE):
        for col in range(SIZE):
            #if we saw an obstacle -> pad around it
            if cells[row, col] == 1:
                for diffr in range(-pad, pad+1):
                    for diffc in range(-pad, pad+1):
                        nrow, ncol = row + diffr, col + diffc
                        if 0 <= nrow < SIZE and 0 <= ncol < SIZE:
                            copy[nrow, ncol] = 1
    return copy

#calc manhattan distance for A*
def manhattan(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

#Implementation of the A* algorithm (using manhattan distance) to get a path from the starting point to the end point
#!!!!!!!! Derived from https://medium.com/@nicholas.w.swift/easy-a-star-pathfinding-7e6689c7f7b2 !!!!!!!!!!
def astar(map, start, end):
    open_list = [start]
    OriginPath = {}
    actual = {start: 0}
    estimate = {start: manhattan(start, end)}
    rows, cols = map.shape

    while open_list:
        current = min(open_list, key=lambda node: estimate[node])
        if current == end:
            path = []
            while current in OriginPath:
                path.append(current)
                current = OriginPath[current]
            path.append(start)
            path.reverse()
            return path
        open_list.remove(current)
        for d in [(-1,0), (1,0), (0,-1), (0,1)]:
            noder, nodec = current[0] + d[0], current[1] + d[1]
            if 0 <= noder < rows and 0 <= nodec < cols and map[noder, nodec] == 0:
                new_g = actual[current] + 1
                if (noder, nodec) not in actual or new_g < actual[(noder, nodec)]:
                    OriginPath[(noder, nodec)] = current
                    actual[(noder, nodec)] = new_g
                    estimate[(noder, nodec)] = new_g + manhattan((noder, nodec), end)
                    if (noder, nodec) not in open_list:
                        open_list.append((noder, nodec))
    return None

# Function for stop sign detection. True is returned if one is seen.
def stop_sign():
    return Vilib.traffic_sign_obj_parameter['t'] == 'stop'

#Function to return the move value of the direction we took. 0 = right, 1 = right, 2 = back, 3 = left
def move_update(direction):
    if direction == 0: 
        return (-1, 0)
    if direction == 1: 
        return (0, 1)
    if direction == 2: 
        return (1, 0)
    if direction == 3: 
        return (0, -1)
    return (0,0)

# function is the oppsoite of the one above. Converts the direction to the move value
def opp_move_update(move_value):
    if move_value == (-1,0): 
        return 0
    if move_value == (0,1):  
        return 1
    if move_value == (1,0):  
        return 2
    if move_value == (0,-1): 
        return 3
    return None

#Function to move the car forward, right, left as needed. Each move is set to be around 15cm in real life.
# This was reused, but modified to fit, from my Lab1A submission.
def drive(car, target_orientation):
    global position, facing

    #right
    diff = (target_orientation - facing) % 4
    if diff == 1:  
        car.set_dir_servo_angle(30)
        car.forward(40)
        time.sleep(.9)
        car.stop()
        facing = (facing + 1) % 4

    #left
    elif diff == 3:
        car.set_dir_servo_angle(-30)
        car.forward(40)
        time.sleep(0.9)
        car.stop()
        facing = (facing - 1) % 4

    # forward
    car.set_dir_servo_angle(0)
    car.forward(40)
    time.sleep(0.4) 
    car.stop()

    # Updates globals for mapping later
    row, col = move_update(facing)
    position[0] += row
    position[1] += col
    print("Moved 1 cell -> pos=", position, "orientation=", facing)

# Function to get to the destination based on the current location on the grid map. 
def navigate(car, destination):
    global StopFlag, position

    #while were not at the destination...
    while tuple(position) != destination:
        # check stop sign
        if not StopFlag and stop_sign():
            print("Stop sign detected -> waiting 5s.")
            car.stop()
            time.sleep(5)
            StopFlag = True

        #scan environment before moving
        print("Scanning environment...")
        keep_scanning(car)
        print()

        #add some padding to obstacles we see, get a path, print path.
        padded = add_pad(grid, clearance=1)
        path = astar(padded, tuple(position), destination)
        print("Path to target ", destination, ":", path)

        next = path[1]
        here = (next[0] - position[0], next[1] - position[1])
        face = opp_move_update(here)
        if face is None:
            print("Not sure where to go.")
            car.stop()
            return

        #Logic for a close obstacle and negative readings. 
        dist = car.ultrasonic.read()
        if dist is None or dist < 0:
            dist = 999
        if dist < BadDistance:
            print("Obstacle extremely close. Let's pause and re-scan.")
            car.stop()
            time.sleep(1)
            continue

        #Now we can move where we need to go
        drive(car, face)

    # End of loop is destination
    print("Arrived at ", destination, "!")
    car.stop()

def main():
    global position, StopFlag

    # Here we initialize the car, servos, and Vilib for the camera and stop sign detection
    #!!!!!!! This code for intializing Vilib was based on provided examples from Sunfounder in the Vilib library !!!!!!!!
    car = Picarx()
    car.set_dir_servo_angle(0)
    car.set_cam_tilt_angle(-10)
    time.sleep(1)
    Vilib.camera_start(vflip=False, hflip=False)
    Vilib.show_fps()
    Vilib.display(local=True, web=True)
    Vilib.traffic_detect_switch(True)
    time.sleep(1)

    #if we start out and see a stop sign
    if stop_sign():
        print("Stop sign at startup -> waiting 5s.")
        car.stop()
        time.sleep(5)
        StopFlag = True  

    print("Starting position = ", position)

    #Set the destination here and then the navigate() function is called
    destination = (0, 16)
    print("Go to destination = ", destination)
    navigate(car, destination)

    car.stop()
    car.set_cam_tilt_angle(-5)
    car.set_cam_pan_angle(0)
    car.set_dir_servo_angle(0)
    Vilib.camera_close()

if __name__ == "__main__":
    main()
