from picarx import Picarx
import time
import random
import threading


GoodDistance = 40
BadDistance  = 15
cancelT1 = False

def main():
    # Here we initialize the Picar-X object, all  servos to 0, and the distance angle when the program is first ran.
    car = Picarx()
    t1 = threading.Thread(target = keep_panning, args = (car,), daemon = True)
    t1.start()
    car.set_dir_servo_angle(0)
    car.set_cam_tilt_angle(-20)
    time.sleep(1.0)

    try:
        while True:
            # Here we get the distance and print to console.
            distance = car.ultrasonic.read()
            print("\nDistance to known object = ", distance, "cm\n")

            # If we do not see anything less than GoodDistance, go forward
            # If we see something between GoodDistance and BadDistance, lets be proactive and turn
            # if we see something within BadDistance, stop and try to move around it in a random direction.
            # (When driving a car, you slow down for turns)
            if distance >= GoodDistance:
                car.set_dir_servo_angle(0)
                car.forward(50)
                time.sleep(.5)
                print("We're good")
            elif distance <= 0:
                distance = GoodDistance
            elif distance >= BadDistance:
                left_or_right(car)
                car.forward(35)
                print("Seeing something here...")
                time.sleep(0.5)
            elif distance <= BadDistance:
                car.backward(50)
                time.sleep(1)
                car.forward(0)
                left_or_right(car)                
                car.forward(35)
                time.sleep(0.5)
                car.set_dir_servo_angle(0)
            time.sleep(0.1)

                                  

    except KeyboardInterrupt:
        cancelT1 = True
        car.set_cam_tilt_angle(-5)
        car.set_cam_pan_angle(0)  
        car.set_dir_servo_angle(0)  
        car.stop()
        print("It was nice driving around for you...")


# Helper function for any time we need to turn the wheels
# this generates at random either 1 or 2. 
# 1 = right turn
# 2 = left turn
def left_or_right(car):
    leftRight = random.randint(1, 2)
    if leftRight == 1:
        car.set_dir_servo_angle(30)
        print("We're going right here")
    elif leftRight == 2:
        car.set_dir_servo_angle(-30)
        print("We're going left here")

# Task for the thread is to continuously pan the distance sensor. I found that if it is 
# not in a thread, no matter how I tweak the numbers, it does not pan quickly enough.
def keep_panning(car):
    global cancelT1
    GetPanAngle = 0
    direction = 1
    
    while not cancelT1:
        car.set_cam_pan_angle(GetPanAngle)
        
        # this is to keep the distance sensor panning
        # I increment the angle and set the next direction it should be panning via - or +
        # and the next angle limit is set
        GetPanAngle += direction
        if GetPanAngle <= -30:
            GetPanAngle = -30
            direction = 1
        elif GetPanAngle >= 30:
            GetPanAngle = 30
            direction = -1
        time.sleep(0.01)
        

if __name__ == "__main__":
    main()