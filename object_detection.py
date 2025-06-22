import cv2
import os
import time
import datetime

class WebcamRecorder:
    def __init__(self, cam_index=0, width=640, height=480,
                 save_path="./videos", segment_duration=10, fps=10):
        self.cam_index = cam_index
        self.width = width
        self.height = height
        self.segment_duration = segment_duration  # in seconds
        self.save_path = save_path
        self.fps = fps
        os.makedirs(save_path, exist_ok=True)

    def run(self):
        cap = cv2.VideoCapture(self.cam_index)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)

        frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        segment_count = 0
        segment_start_time = time.time()

        out = self._create_writer(fourcc, self.fps, segment_count, frame_width, frame_height)

        print("[INFO] Press 'q' to quit.")
        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    print("[ERROR] Failed to read frame")
                    break

                # Write the frame
                out.write(frame)

                # Show the frame
                cv2.imshow("Webcam Live", frame)

                # Handle segmentation (split videos into segments)
                if time.time() - segment_start_time >= self.segment_duration:
                    out.release()
                    segment_count += 1
                    out = self._create_writer(fourcc, self.fps, segment_count, frame_width, frame_height)
                    segment_start_time = time.time()

                if cv2.waitKey(1) & 0xFF == ord('q'):
                    print("[INFO] 'q' pressed. Exiting...")
                    break

        except KeyboardInterrupt:
            print("\n[INFO] Ctrl+C detected. Exiting...")

        finally:
            cap.release()
            out.release()
            cv2.destroyAllWindows()
            print("[INFO] All resources released.")

    def _create_writer(self, fourcc, fps, segment_count, width, height):
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(self.save_path, f"segment_{timestamp}_{segment_count:03d}.avi")

        print(f"[INFO] Saving video: {filename}")

        writer = cv2.VideoWriter(filename, fourcc, fps, (width, height))

        if not writer.isOpened():
            print("[ERROR] Failed to open VideoWriter!")

        return writer


if __name__ == "__main__":
    recorder = WebcamRecorder(
        cam_index=0,
        width=640,
        height=480,
        save_path="./videos",
        segment_duration=10 * 60,  # 10 minutes
        fps=10
    )
    recorder.run()
