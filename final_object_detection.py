import cv2
import os
import time
from datetime import datetime
from ultralytics import YOLO


class YoloWebcamRecorder:
    def __init__(self, model_path="yolov8n.pt", cam_index=0, width=640, height=480,
                 save_path="videos", segment_duration=10, fps=10):
        self.model = YOLO(model_path)
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

        fps = self.fps
        print(f"[INFO] Using fixed FPS: {fps}")

        frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        segment_count = 0
        segment_start_time = time.time()

        out, raw_out = self._create_writer(fourcc, fps, segment_count, frame_width, frame_height)

        print("[INFO] Press 'q' to quit.")
        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    print("[ERROR] Failed to read frame")
                    break

                
                raw_out.write(frame)

                
                results = self.model(frame)
                annotated_frame = results[0].plot()

                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                cv2.putText(annotated_frame, timestamp, (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

                
                out.write(annotated_frame)

                cv2.imshow("YOLOv8 Live", annotated_frame)

                
                if time.time() - segment_start_time >= self.segment_duration:
                    out.release()
                    raw_out.release()
                    segment_count += 1
                    out, raw_out = self._create_writer(fourcc, fps, segment_count, frame_width, frame_height)
                    segment_start_time = time.time()

                if cv2.waitKey(1) & 0xFF == ord('q'):
                    print("[INFO] 'q' pressed. Exiting...")
                    break

        except KeyboardInterrupt:
            print("\n[INFO] Ctrl+C detected. Exiting...")

        finally:
            cap.release()
            out.release()
            raw_out.release()
            cv2.destroyAllWindows()
            print("[INFO] All resources released.")

    def _create_writer(self, fourcc, fps, segment_count, width, height):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        annotated_filename = os.path.join(self.save_path, f"segment_{timestamp}_{segment_count:03d}.avi")
        raw_filename = os.path.join(self.save_path, f"raw_segment_{timestamp}_{segment_count:03d}.avi")

        print(f"[INFO] Saving annotated video: {annotated_filename}")
        print(f"[INFO] Saving raw video: {raw_filename}")

        annotated_writer = cv2.VideoWriter(annotated_filename, fourcc, fps, (width, height))
        raw_writer = cv2.VideoWriter(raw_filename, fourcc, fps, (width, height))

        if not annotated_writer.isOpened() or not raw_writer.isOpened():
            print("[ERROR] Failed to open one of the VideoWriters!")

        return annotated_writer, raw_writer


# if __name__ == "__main__":
#     recorder = YoloWebcamRecorder(
#         model_path="yolov8n.pt",
#         cam_index=0,
#         width=640,
#         height=480,
#         save_path="./data/videos",
#         segment_duration=10 * 60,  # 10 minutes
#         fps=1
#     )
#     recorder.run()







# import cv2
# import os
# import time
# import datetime
# from ultralytics import YOLO

# class YoloWebcamRecorder:
#     def __init__(self, model_path="yolov8n.pt", cam_index=0, width=640, height=480,
#                  save_path="videos", segment_duration=10,fps=10):
#         self.model = YOLO(model_path)
#         self.cam_index = cam_index
#         self.width = width
#         self.height = height
#         self.segment_duration = segment_duration  # in seconds
#         self.save_path = save_path
#         self.fps=fps
#         os.makedirs(save_path, exist_ok=True)

#     def run(self):
#         cap = cv2.VideoCapture(self.cam_index)
#         cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
#         cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
#         #fps = cap.get(cv2.CAP_PROP_FPS)
#         fps=self.fps
#         # if fps == 0:
#         #     fps = 5  # fallback if camera reports 0

#         frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
#         frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

#         fourcc = cv2.VideoWriter_fourcc(*'XVID')  # 'mp4v' for .mp4, 'XVID' for .avi
#         segment_count = 0
#         segment_start_time = time.time()

#         out, raw_out = self._create_writer(fourcc, fps, segment_count, frame_width, frame_height)

#         print("[INFO] Press 'q' to quit.")
#         try:
#             while True:
#                 ret, frame = cap.read()
#                 if not ret:
#                     print("[ERROR] Failed to read frame")
#                     break

#                 # Write unannotated frame
#                 raw_out.write(frame)

#                 # Run YOLO detection
#                 results = self.model(frame)
#                 annotated_frame = results[0].plot()

#                 # Write annotated frame
#                 if annotated_frame is not None:
#                     out.write(annotated_frame)
#                 else:
#                     print("[WARNING] Annotated frame is None!")

#                 # Show annotated frame
#                 cv2.imshow("YOLOv8 Live", annotated_frame)

#                 # Segment recording
#                 if time.time() - segment_start_time >= self.segment_duration:
#                     out.release()
#                     raw_out.release()
#                     segment_count += 1
#                     out, raw_out = self._create_writer(fourcc, fps, segment_count, frame_width, frame_height)
#                     segment_start_time = time.time()

#                 if cv2.waitKey(1) & 0xFF == ord('q'):
#                     print("[INFO] 'q' pressed. Exiting...")
#                     break

#         except KeyboardInterrupt:
#             print("\n[INFO] Ctrl+C detected. Exiting...")

#         finally:
#             cap.release()
#             out.release()
#             raw_out.release()
#             cv2.destroyAllWindows()
#             print("[INFO] All resources released.")

#     def _create_writer(self, fourcc, fps, segment_count, width, height):
#         timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
#         annotated_filename = os.path.join(self.save_path, f"segment_{timestamp}_{segment_count:03d}.avi")
#         raw_filename = os.path.join(self.save_path, f"raw_segment_{timestamp}_{segment_count:03d}.avi")

#         print(f"[INFO] Saving annotated video: {annotated_filename}")
#         print(f"[INFO] Saving raw video: {raw_filename}")

#         annotated_writer = cv2.VideoWriter(annotated_filename, fourcc, fps, (width, height))
#         raw_writer = cv2.VideoWriter(raw_filename, fourcc, fps, (width, height))

#         if not annotated_writer.isOpened() or not raw_writer.isOpened():
#             print("[ERROR] Failed to open one of the VideoWriters!")

#         return annotated_writer, raw_writer

# if __name__ == "__main__":
#     recorder = YoloWebcamRecorder(
#         model_path="yolov8n.pt", 
#         cam_index=0, 
#         width=640, 
#         height=480, 
#         save_path="videos", 
#         segment_duration=10*60 ,
#         fps=10 # seconds
#     )
#     recorder.run()





# import cv2
# import os
# import time
# import datetime
# from ultralytics import YOLO

# class YoloWebcamRecorder:
#     def __init__(self, model_path="yolov8n.pt", cam_index=0, width=640, height=480,
#                  save_path="videos", segment_duration=10):
#         self.model = YOLO(model_path)
#         self.cam_index = cam_index
#         self.width = width
#         self.height = height
#         self.segment_duration = segment_duration  # in seconds
#         self.save_path = save_path
#         os.makedirs(save_path, exist_ok=True)

#     def run(self):
#         cap = cv2.VideoCapture(self.cam_index)
#         cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
#         cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
#         fps = cap.get(cv2.CAP_PROP_FPS)
#         if fps == 0:
#             fps = 30  # fallback if camera reports 0

#         frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
#         frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

#         fourcc = cv2.VideoWriter_fourcc(*'XVID')  # 'mp4v' for .mp4, 'XVID' for .avi
#         segment_count = 0
#         segment_start_time = time.time()

#         out = self._create_writer(fourcc, fps, segment_count, frame_width, frame_height)

#         print("[INFO] Press 'q' to quit.")
#         try:
#             while True:
#                 ret, frame = cap.read()
#                 if not ret:
#                     print("[ERROR] Failed to read frame")
#                     break

#                 # Run YOLO detection
#                 results = self.model(frame)
#                 annotated_frame = results[0].plot()

#                 # Write frame
#                 if annotated_frame is not None:
#                     out.write(annotated_frame)
#                 else:
#                     print("[WARNING] Annotated frame is None!")

#                 # Show frame
#                 cv2.imshow("YOLOv8 Live", annotated_frame)

#                 # Segment recording
#                 if time.time() - segment_start_time >= self.segment_duration:
#                     out.release()
#                     segment_count += 1
#                     out = self._create_writer(fourcc, fps, segment_count, frame_width, frame_height)
#                     segment_start_time = time.time()

#                 if cv2.waitKey(1) & 0xFF == ord('q'):
#                     print("[INFO] 'q' pressed. Exiting...")
#                     break

#         except KeyboardInterrupt:
#             print("\n[INFO] Ctrl+C detected. Exiting...")

#         finally:
#             cap.release()
#             out.release()
#             cv2.destroyAllWindows()
#             print("[INFO] All resources released.")

#     def _create_writer(self, fourcc, fps, segment_count, width, height):
#         now = str(datetime.datetime.now())
#         filename = os.path.join(self.save_path, f"segment_{now}_{segment_count:03d}.avi")
#         print(f"[INFO] Saving video: {filename}")
#         writer = cv2.VideoWriter(filename, fourcc, fps, (width, height))
#         if not writer.isOpened():
#             print("[ERROR] Failed to open VideoWriter!")
#         return writer

# # To run it:
# if __name__ == "__main__":
#     recorder = YoloWebcamRecorder(
#         model_path="yolov8n.pt", 
#         cam_index=0, 
#         width=640, 
#         height=480, 
#         save_path="videos", 
#         segment_duration=10*60  # seconds
#     )
#     recorder.run()
