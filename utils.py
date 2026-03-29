
import ctypes
import platform


def is_cuda_runtime_available() -> bool:
    system = platform.system()
    try:
        if system == "Linux":
            ctypes.cdll.LoadLibrary("libcudart.so")
        else:
            print("CUDA Runtime library not found. Defaulting to CPU.")
            return False
            
        print("CUDA Runtime library found.")
        return True
    except OSError:
        print("Error while checking CUDA Runtime availability. Defaulting to CPU.")
        return False