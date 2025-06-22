from rplidar import RPLidar
from datetime import datetime
import csv
import os
import math
import json


class RPLidarLogger:
    def __init__(self, port='/dev/ttyUSB0', baudrate=115200):
        self.port = port
        self.baudrate = baudrate
        self.lidar = None
        self.output_file = self._generate_filename()
        self.csv_file = None
        self.writer = None

    def _generate_filename(self):
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        os.makedirs('./data', exist_ok=True)
        return f'./data/rplidar_data_with_xy_{timestamp}.csv'

    def connect(self):
        self.lidar = RPLidar(self.port, baudrate=self.baudrate)
        print(f"[INFO] Connected to RPLIDAR on {self.port}")

    def setup_csv(self):
        self.csv_file = open(self.output_file, mode='w', newline='')
        self.writer = csv.writer(self.csv_file)
        self.writer.writerow(['timestamp', 'rotation_data'])

    def start_logging(self):
        try:
            print("[INFO] Starting scan loop...")
            for scan in self.lidar.iter_scans():
                current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
                rotation_data = []

                for measurement in scan:
                    quality, angle_deg, distance = measurement
                    angle_rad = math.radians(angle_deg)
                    x = distance * math.cos(angle_rad)
                    y = distance * math.sin(angle_rad)

                    rotation_data.append({
                        'quality': quality,
                        'angle_deg': angle_deg,
                        'distance_mm': distance,
                        'x_mm': round(x, 2),
                        'y_mm': round(y, 2)
                    })

                # Write one row per rotation
                self.writer.writerow([current_time, json.dumps(rotation_data)])
                print(f"[INFO] Rotation logged at {current_time} with {len(rotation_data)} points")

        except KeyboardInterrupt:
            print("\n[INFO] Scan interrupted by user.")

        except Exception as e:
            print(f"[ERROR] Exception during scan: {e}")

    def cleanup(self):
        print("[INFO] Stopping and disconnecting...")
        if self.lidar:
            self.lidar.stop()
            self.lidar.disconnect()
        if self.csv_file:
            self.csv_file.close()
        print(f"[✅] Scan complete. Data saved to: {os.path.abspath(self.output_file)}")

    def run(self):
        self.connect()
        self.setup_csv()
        self.start_logging()
        self.cleanup()


# if __name__ == '__main__':
#     logger = RPLidarLogger()
#     logger.run()
