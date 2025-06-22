import serial
import struct
import time

class TFminiSensor:
    def __init__(self, port="COM8", baud_rate=115200, timeout=2):
        """Initialize the TFmini sensor with the given serial port and baud rate."""
        self.port = port
        self.baud_rate = baud_rate
        try:
            self.ser = serial.Serial(self.port, self.baud_rate, timeout=timeout)
            time.sleep(2)  
            self.ser.reset_input_buffer()
            print("TFmini Sensor initialized successfully.")
        except serial.SerialException as e:
            print(f"Error opening serial port: {e}")
            self.ser = None  # Mark serial connection as failed
        
    def read_data(self):
        """Reads a single frame of data from the TFmini sensor with frame synchronization."""
        if self.ser is None:
            return {"status": 503, "distance": -99999, "strength": -99999, "message": "Serial port not initialized"}

        try:
           
            while True:
                first_byte = self.ser.read(1)
                if first_byte == b'\x59':  
                    second_byte = self.ser.read(1)
                    if second_byte == b'\x59':  
                        break  

            # Read the remaining 7 bytes (since we already read 2)
            data = self.ser.read(7)

            if len(data) != 7:
                print("Incomplete data received:", data)
                return {"status": 504, "distance": -99999, "strength": -99999, "message": "Incomplete data"}

            # Parse the frame
            distance = struct.unpack('<H', data[0:2])[0]
            strength = struct.unpack('<H', data[2:4])[0]
            checksum = sum([0x59, 0x59] + list(data[:6])) & 0xFF  # Compute checksum

            # Validate checksum
            if checksum != data[6]:
                print("Checksum mismatch, invalid data frame:", data.hex())
                return {"status": 504, "distance": -99999, "strength": -99999, "message": "Checksum error"}

            print(f"Distance: {distance} cm, Strength: {strength}")
            return {"status": 200, "distance": distance, "strength": strength}

        except Exception as e:
            print(f"Error reading data: {e}")
            return {"status": 500, "distance": -99999, "strength": -99999, "message": "Exception occurred"}

    def close(self):
        """Closes the serial connection."""
        if self.ser is not None:
            self.ser.close()
            print("Serial connection closed.")

  
sensor_front = TFminiSensor(port="/dev/ttyUSB0")
if sensor_front.ser is not None:  
    try:
        while True:
            result = sensor_front.read_data()
            print("Front",result)  
    except KeyboardInterrupt:
        print("\nUser interrupted. Stopping sensor reading.")
        sensor_front.close()
else:
    print("Sensor could not be initialized. Exiting program.")


