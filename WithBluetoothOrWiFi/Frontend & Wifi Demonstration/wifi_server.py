import socket
import time
import subprocess
from picarx import Picarx
from robot_hat import ADC

HOST = " " # IP address of my Raspberry PI
PORT = 65432          # Port to listen on (non-privileged ports are > 1023)

#Initialize the car, battery, and speed variables
adc = ADC("A4")
car = Picarx()
speed = 0

#Helper to get battery percentage. The voltage range for Picar-X standard 18065 batteries should be
# > 8.4 - 6.6. Sourced, but modifed, from: https://forum.sunfounder.com/t/picar-x-help-and-suggestions/271/12
def get_battery():
    voltage = adc.read()
    voltage = voltage * 3.3 / 4095
    voltage = voltage * 3
    
    percent = ( voltage - 6.6 ) / ( 8.4 - 6.6 ) * 100
    percent = max(0, min(100, percent))
    return int(percent)

#Function for moving the car with wsad keys
def movement(key):
    global speed
    key = key.lower()
    if key in('wsadc'): 
        if 'w' == key:
            car.set_dir_servo_angle(0)
            car.forward(50)
            time.sleep(1)
            speed = 50
            car.stop()
        elif 's' == key:
            car.set_dir_servo_angle(0)
            car.backward(50)
            time.sleep(1)
            car.stop()
            speed = 50
        elif 'a' == key:
            car.set_dir_servo_angle(-30)
            car.forward(30)
            time.sleep(1)
            car.stop()
            speed = 30
        elif 'd' == key:
            car.set_dir_servo_angle(30)
            car.forward(30)
            time.sleep(1)
            car.stop()
            speed = 30
        elif 'c' == key:
            car.stop()
            speed = 0

#Helper to get the pi temperature. Sourced from: https://forums.raspberrypi.com/viewtopic.php?t=309480
def pi_temp():
    temp =  subprocess.check_output(["vcgencmd", "measure_temp"]).decode()
    return float(temp.split("=")[1].split("'")[0])

def send_stats():
    battery = get_battery()
    temp = pi_temp()
    stats = (f"{battery}\n" f"{temp}\n" f"{speed}\r\n")
    return stats

def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()

        try:
            while 1:
                client, clientInfo = s.accept()
                print("server recv from: ", clientInfo)
                data = client.recv(1024)      # receive 1024 Bytes of message in binary format
                if data != b"":
                    key = data.decode("utf-8").strip()
                    movement(key)
                    stats = send_stats()
                    client.sendall(stats.encode("utf-8")) # Echo back to client
        except: 
            print("Closing socket")
            client.close()
            s.close()

if __name__ == "__main__":
    main()
