# SunFounder PiCar-X Code

This repository contains code I’ve created for the [SunFounder PiCar-X](https://www.sunfounder.com/products/picar-x) project. The PiCar-X is a Raspberry Pi-based robot car kit that allows for a wide range of functionalities, from simple remote-control operations to autonomous navigation.

---


### Top-Level Scripts

1. **Roomba.py**  
   - A script that allows the PiCar-X to function similarly to a “Roomba.”  
   - The car roams around, detects obstacles, and avoids them.

2. **SelfDrive.py**  
   - A script that allows the PiCar-X to navigate to a certain point on a 20×20 grid.  
   - Input the desired `(x, y)` coordinates, and the car will autonomously navigate there.

---

### WithBluetoothOrWiFi Directory

This directory contains demonstrations of controlling the PiCar-X via either Bluetooth or WiFi. Each subfolder contains distinct examples and supporting code.

#### 1. Bluetooth Demonstration

- **pi_socket.py**  
  - The **server-side** Python script. Run this on the Raspberry Pi.  
  - Listens for Bluetooth connections and receives commands to control the car.

- **windows_socket.py**  
  - The **client-side** Python script. Run this on a Windows PC.  
  - Connects to the Pi via Bluetooth and sends movement commands.

> **Note**: Run both scripts simultaneously on their respective machines to establish a Bluetooth connection and drive the car around.

#### 2. Frontend & Wifi Demonstration

- **electron** (folder)  
  - Contains an **ElectronJS application** that should be run on a PC.  
  - Connects over WiFi to the Raspberry Pi, providing a GUI to control the car and display stats (battery, speed, temperature).

- **wifi_server.py**  
  - The **server-side** Python script to be run on the Raspberry Pi.  
  - Receives commands from the Electron client and sends back status updates about the car.

> **Note**: Start `wifi_server.py` on the Pi, then launch the Electron application on your PC. Both devices must be on the same WiFi network.

---

## How to Use

1. **Hardware Setup**  
   - Assemble your SunFounder PiCar-X according to the manufacturer’s instructions.  
   - Make sure the Raspberry Pi is connected properly to the PiCar-X chassis and motors.

2. **Dependencies**  
   - Ensure the Raspberry Pi has Python (3.x).  
   - Install any required Python libraries for PiCar-X operations (e.g., `sunfounder_picarx`, `rpi.gpio`). Refer to [SunFounder’s PiCar-X documentation](https://www.sunfounder.com/products/picar-x) for more details.

3. **Running the Scripts**  
   - **Roomba-Style Movement**  
     ```bash
     python3 Roomba.py
     ```
     This starts the obstacle-avoiding roaming functionality.

   - **Self-Driving to Grid Point**  
     ```bash
     python3 SelfDrive.py
     ```
     Input `(x, y)` coordinates when prompted, and the PiCar-X will drive to that point.

4. **Bluetooth Control**  
   - **On the Raspberry Pi**:
     ```bash
     python3 WithBluetoothOrWiFi/Bluetooth Demonstration/pi_socket.py
     ```
   - **On Windows PC**:
     ```bash
     python3 WithBluetoothOrWiFi/Bluetooth Demonstration/windows_socket.py
     ```
   - Ensure both devices have Bluetooth enabled and are paired if necessary.

5. **WiFi Control & Frontend**  
   - **On the Raspberry Pi**:
     ```bash
     python3 WithBluetoothOrWiFi/Frontend & Wifi Demonstration/wifi_server.py
     ```
   - **On your PC (within the electron folder)**:
     ```bash
     npm install
     npm start
     ```
   - The ElectronJS application should detect the Pi if both are on the same WiFi network.  
   - You can then use the GUI to control the PiCar-X and view real-time telemetry.

---

## Contributing

Contributions, fixes, and suggestions are welcome! Feel free to open an issue or submit a pull request to discuss any changes you’d like to see.

---

## Contact

For any questions or support, please open an issue in this repository.

Enjoy your SunFounder PiCar-X adventures!
