import os
import threading
import cv2


class VideoStream:
    def __init__(self, src):
        print(f"Opening video stream from {src}...")
        if isinstance(src, str):
            os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = (
                "rtsp_transport;tcp|fflags;nobuffer|flags;low_delay"
            )
            backend = cv2.CAP_FFMPEG
        else:
            backend = cv2.CAP_ANY
        self.stream = cv2.VideoCapture(src, backend)
        self.stream.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        if not self.stream.isOpened():
            print("Error: Could not open video stream.")
            exit()
        self.grabbed, self.frame = self.stream.read()
        self.stopped = False

    def start(self):
        threading.Thread(target=self.update, args=(), daemon=True).start()
        return self

    def update(self):
        while not self.stopped:
            self.grabbed, self.frame = self.stream.read()
            if not self.grabbed:
                self.stop()
                return

    def read(self):
        return self.frame

    def stop(self):
        self.stopped = True
        self.stream.release()
