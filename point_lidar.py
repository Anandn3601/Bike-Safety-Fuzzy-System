import serial
import struct
import time
import csv
from datetime import datetime

class TFminiSensor:
    def __init__(self, port="/dev/ttyUSB0", baud_rate=115200, timeout=2):
        self.port = port
        self.baud_rate = baud_rate
        try:
            self.ser = serial.Serial(self.port, self.baud_rate, timeout=timeout)
            time.sleep(2)
            self.ser.reset_input_buffer()
            print("TFmini Sensor initialized successfully.")
        except serial.SerialException as e:
            print(f"Error opening serial port: {e}")
            self.ser = None

    def read_data(self):
        if self.ser is None:
            return {"status": 503, "distance": -99999, "strength": -99999, "message": "Serial port not initialized"}

        try:
            while True:
                first_byte = self.ser.read(1)
                if first_byte == b'\x59':
                    second_byte = self.ser.read(1)
                    if second_byte == b'\x59':
                        break

            data = self.ser.read(7)
            if len(data) != 7:
                return {"status": 504, "distance": -99999, "strength": -99999, "message": "Incomplete data"}

            distance = struct.unpack('<H', data[0:2])[0]
            strength = struct.unpack('<H', data[2:4])[0]
            checksum = sum([0x59, 0x59] + list(data[:6])) & 0xFF

            if checksum != data[6]:
                return {"status": 504, "distance": -99999, "strength": -99999, "message": "Checksum error"}

            return {"status": 200, "distance": distance, "strength": strength}

        except Exception as e:
            return {"status": 500, "distance": -99999, "strength": -99999, "message": "Exception occurred"}

    def close(self):
        if self.ser is not None:
            self.ser.close()
            print("Serial connection closed.")


def main():
    sensor_front = TFminiSensor(port="/dev/ttyUSB0")

    if sensor_front.ser is not None:
        # Open CSV file for logging
        import os
        output_dir = "front_lidar"
        os.makedirs(output_dir, exist_ok=True)

        # Generate timestamped filename
        timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(output_dir, f"{timestamp_str}_front_lidar.csv")
        with open(filename, mode="w", newline="") as csvfile:
            fieldnames = ["timestamp", "distance_cm", "strength"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            try:
                while True:
                    result = sensor_front.read_data()
                    if result["status"] == 200:
                        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
                        writer.writerow({
                            "timestamp": timestamp,
                            "distance_cm": result["distance"],
                            "strength": result["strength"]
                        })
                        print(f"{timestamp} | Distance: {result['distance']} cm | Strength: {result['strength']}")
                        csvfile.flush()  # Make sure data is written to file
                    else:
                        print("Error:", result["message"])
                    # time.sleep(0.1)

            except KeyboardInterrupt:
                print("\nUser interrupted. Stopping sensor reading.")
                sensor_front.close()

    else:
        print("Sensor could not be initialized. Exiting program.")


if __name__ == "__main__":
    main()
