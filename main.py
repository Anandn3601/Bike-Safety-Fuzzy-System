import threading
import time

# Import sensor and YOLO modules
from imu import main_Call as imu_main
from dlidar import TFminiSensor
from lidar_final import RPLidarLogger
from final_object_detection import YoloWebcamRecorder

# IMU function
def run_imu():
    print("[MAIN] Starting MPU6050 (IMU) sensor...")
    imu_main()

# TFmini LIDAR function
def run_tfmini():
    print("[MAIN] Starting TFmini LIDAR sensor...")
    sensor = TFminiSensor(port="/dev/ttyUSB1")
    if sensor.ser is not None:
        try:
            while True:
                data = sensor.read_data()
                print("[TFmini]", data)
                time.sleep(0.5)
        except KeyboardInterrupt:
            sensor.close()
            print("[MAIN] TFmini stopped by user.")
    else:
        print("[ERROR] TFmini could not be initialized.")

# RPLidar function
def run_rplidar():
    print("[MAIN] Starting RPLidar scanning...")
    try:
        lidar = RPLidarLogger()
        lidar.run()
    except KeyboardInterrupt:
        print("[MAIN] RPLidar interrupted.")

# YOLO video recording function
def run_yolo():
    print("[MAIN] Starting YOLOv8 video recorder...")
    recorder = YoloWebcamRecorder(
        model_path="yolov8n.pt",
        cam_index=0,
        width=640,
        height=480,
        save_path="./data/videos",
        segment_duration=10 * 60,  # 10 minutes
        fps=5
    )
    recorder.run()

if __name__ == "__main__":
    print("[MAIN] Starting all modules...")

    threads = [
        threading.Thread(target=run_imu),
        threading.Thread(target=run_tfmini),
        threading.Thread(target=run_rplidar),
        threading.Thread(target=run_yolo)
    ]

    for thread in threads:
        thread.start()

    try:
        for thread in threads:
            thread.join()
    except KeyboardInterrupt:
        print("\n[MAIN] Interrupted by user. Exiting...")
