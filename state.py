import threading

lock = threading.Lock()
current_description = "Initializing..."
current_frame_jpg = None   # raw JPEG bytes of the last analyzed frame
inference_fps = 0.0        # updated by analyzer after each inference
prompt = ""                # active inference prompt, set at startup
