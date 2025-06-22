from smbus2 import SMBus
import time
import csv
import os
from datetime import datetime

class MPU6050:
    def __init__(self, bus_id=1, address=0x68, verbose=True):
        self.address = address
        self.verbose = verbose
        try:
            self.bus = SMBus(bus_id)
            self.PWR_MGMT_1 = 0x6B
            self.ACCEL_XOUT_H = 0x3B
            self.GYRO_XOUT_H = 0x43
            self.bus.write_byte_data(self.address, self.PWR_MGMT_1, 0)  # Wake up MPU6050
            if self.verbose:
                print("MPU6050 initialized successfully.")
        except Exception as e:
            print(f"Failed to initialize MPU6050: {e}")
            self.bus = None

    def read_raw_data(self, reg):
        if self.bus is None:
            raise IOError("I2C bus is not initialized.")
        try:
            high = self.bus.read_byte_data(self.address, reg)
            low = self.bus.read_byte_data(self.address, reg + 1)
            value = (high << 8) | low
            return value - 65536 if value > 32767 else value
        except Exception as e:
            if self.verbose:
                print(f"Error reading raw data from reg 0x{reg:X}: {e}")
            return None

    def get_accel_data(self):
        try:
            ax = self.read_raw_data(self.ACCEL_XOUT_H)
            ay = self.read_raw_data(self.ACCEL_XOUT_H + 2)
            az = self.read_raw_data(self.ACCEL_XOUT_H + 4)

            if None in (ax, ay, az):
                raise ValueError("Incomplete accelerometer data.")

            return {
                "status": 200,
                "accel": {
                    'x': ax / 16384.0,
                    'y': ay / 16384.0,
                    'z': az / 16384.0
                }
            }
        except Exception as e:
            return {
                "status": 500,
                "accel": {'x': None, 'y': None, 'z': None},
                "message": str(e)
            }

    def get_gyro_data(self):
        try:
            gx = self.read_raw_data(self.GYRO_XOUT_H)
            gy = self.read_raw_data(self.GYRO_XOUT_H + 2)
            gz = self.read_raw_data(self.GYRO_XOUT_H + 4)

            if None in (gx, gy, gz):
                raise ValueError("Incomplete gyroscope data.")

            return {
                "status": 200,
                "gyro": {
                    'x': gx / 131.0,
                    'y': gy / 131.0,
                    'z': gz / 131.0
                }
            }
        except Exception as e:
            return {
                "status": 500,
                "gyro": {'x': None, 'y': None, 'z': None},
                "message": str(e)
            }

    def close(self):
        if self.bus:
            self.bus.close()
            if self.verbose:
                print("I2C bus closed.")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

# Main program loop with CSV logging
def main_Call():
    filename = "imu_data.csv"

    # Create CSV file and write headers if it doesn't exist
    file_exists = os.path.isfile(filename)
    with open(filename, mode='a', newline='') as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow([
                "timestamp",
                "accel_x", "accel_y", "accel_z",
                "gyro_x", "gyro_y", "gyro_z"
            ])

    with MPU6050(verbose=True) as sensor:
        if sensor.bus is None:
            return {
                "status": 503,
                "message": "MPU6050 not available",
                "accel": None,
                "gyro": None
            }

        try:
            with open(filename, mode='a', newline='') as file:
                writer = csv.writer(file)

                while True:
                    accel_data = sensor.get_accel_data()
                    gyro_data = sensor.get_gyro_data()

                    if accel_data["status"] == 200 and gyro_data["status"] == 200:
                        a = accel_data["accel"]
                        g = gyro_data["gyro"]
                        timestamp = datetime.now().isoformat()

                        # Write to CSV
                        writer.writerow([timestamp, a['x'], a['y'], a['z'], g['x'], g['y'], g['z']])

                        print(f"{timestamp} | Accel: X={a['x']:.2f}g Y={a['y']:.2f}g Z={a['z']:.2f}g | "
                              f"Gyro: X={g['x']:.2f}°/s Y={g['y']:.2f}°/s Z={g['z']:.2f}°/s")
                    else:
                        print("Sensor read error:", accel_data.get("message", ""), gyro_data.get("message", ""))

                    time.sleep(0.5)

        except KeyboardInterrupt:
            print("\nUser interrupted. Exiting MPU6050 reading.")
            return {
                "status": 999,
                "message": "User interrupted the sensor reading loop."
            }

# Call main if run directly
if __name__ == "__main__":
    final_result = main_Call()
    print("Final Result:", final_result)
