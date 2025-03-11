import socket
import threading
from collections import deque
import signal
import time
import subprocess
from picarx import Picarx
from robot_hat import ADC

server_addr = '' #updated to pi's Bluetooth mac address
server_port = 1

buf_size = 1024

client_sock = None
server_sock = None
sock = None

exit_event = threading.Event()

message_queue = deque([])
output = ""

dq_lock = threading.Lock()
output_lock = threading.Lock()

def handler(signum, frame):
    exit_event.set()

signal.signal(signal.SIGINT, handler)

#Initialize the car, battery, and speed variables
car = Picarx()
adc = ADC("A4")
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

#Helper to get the pi temperature. Sourced from: https://forums.raspberrypi.com/viewtopic.php?t=309480
def pi_temp():
    temp =  subprocess.check_output(["vcgencmd", "measure_temp"]).decode()
    return float(temp.split("=")[1].split("'")[0])

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

def send_stats():
    battery = get_battery()
    temp = pi_temp()
    stats = (f"Battery = {battery}\n" f"CPU temp = {temp}\n" f"Speed = {speed}\r\n")
    message_queue.append(stats)

def start_client():
    global server_addr
    global server_port
    global server_sock       
    global sock
    global exit_event
    global message_queue
    global output
    global dq_lock
    global output_lock
    server_sock = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
    server_sock.bind((server_addr, server_port))
    server_sock.listen(1)
    server_sock.settimeout(60)
    sock, address = server_sock.accept()
    print("Connected")
    server_sock.settimeout(None)
    sock.setblocking(0)
    while not exit_event.is_set():
        if dq_lock.acquire(blocking=False):
            if(len(message_queue) > 0):
                try:
                    sent = sock.send(bytes(message_queue[0], 'utf-8'))
                except Exception as e:
                    exit_event.set()
                    continue
                if sent < len(message_queue[0]):
                    message_queue[0] = message_queue[0][sent:]
                else:
                    message_queue.popleft()
            dq_lock.release()
        
        if output_lock.acquire(blocking=False):
            data = ""
            try:
                try:
                    data = sock.recv(1024).decode('utf-8')
                except socket.error as e:
                    assert(1==1)
                    #no data

            except Exception as e:
                exit_event.set()
                continue
            output += data
            output_split = output.split("\r\n")
            for i in range(len(output_split) - 1):
                key = output_split[i].strip()

                movement(key)
                send_stats()

            output = output_split[-1]
            output_lock.release()
        time.sleep(.3)
    server_sock.close()
    sock.close()
    print("client thread end")


cth = threading.Thread(target=start_client)

cth.start()

j = 0
while not exit_event.is_set():
    dq_lock.acquire()
    message_queue.append("RPi " + str(j) + " \r\n")
    dq_lock.release()
    j += 1
    time.sleep(1)
    

print("Disconnected.")
print("All done.")
