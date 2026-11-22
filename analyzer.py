import contextlib
import ctypes
import os
import time
import cv2
import base64
from typing import cast
import state
from llama_cpp import CreateChatCompletionResponse, Llama, llama_log_set, llama_log_callback
from llama_cpp.llama_chat_format import MoondreamChatHandler
from utils import is_cuda_runtime_available

PROMPT = "Please describe the scene within 20 words"
DEFAULT_MODEL_PATH = "models/moondream2-text-model-q4_k_m.gguf"
DEFAULT_CLIP_PATH = "models/moondream2-mmproj-f16.gguf"


@llama_log_callback
def _noop_log(*_):
    pass


@contextlib.contextmanager
def _quiet():
    saved = os.dup(2)
    devnull = os.open(os.devnull, os.O_WRONLY)
    os.dup2(devnull, 2)
    try:
        yield
    finally:
        os.dup2(saved, 2)
        os.close(saved)
        os.close(devnull)


llama_log_set(_noop_log, ctypes.c_void_p())


def run(vs, prompt=PROMPT, model_path=DEFAULT_MODEL_PATH, clip_model_path=DEFAULT_CLIP_PATH):
    with _quiet():
        chat_handler = MoondreamChatHandler(clip_model_path=clip_model_path, verbose=False)
        model = Llama(
            model_path=model_path,
            chat_handler=chat_handler,
            n_ctx=1280,
            n_gpu_layers=-1 if is_cuda_runtime_available() else 0,
            n_batch=512,
            flash_attn=True,
            offload_kqv=True,
            verbose=False,
        )

    try:
        with _quiet():
            warmup = cast(CreateChatCompletionResponse, model.create_chat_completion(
                messages=[{'role': 'user', 'content': 'hi'}],
                max_tokens=16,
                temperature=0.1,
            ))
        print(f"Model ready: {(warmup['choices'][0]['message']['content'] or '').strip()}")
    except Exception as e:
        print(f"Error: model failed to initialise — {e}")
        return

    while (frame := vs.read()) is None:
        time.sleep(0.1)

    img_width = frame.shape[1]
    cell_w = 384
    cell_h = int(cell_w / (img_width / frame.shape[0]))

    while True:
        frame = vs.read()
        if frame is None:
            time.sleep(0.1)
            continue

        try:
            resized = cv2.resize(frame, (cell_w, cell_h))
            _, buf = cv2.imencode('.jpg', resized)
            b64 = base64.b64encode(buf).decode('utf-8')

            start = time.time()
            with _quiet():
                response = cast(CreateChatCompletionResponse, model.create_chat_completion(
                    messages=[{
                        'role': 'user',
                        'content': [
                            {'type': 'text', 'text': prompt},
                            {'type': 'image_url', 'image_url': {'url': 'data:image/jpeg;base64,' + b64}},
                        ],
                    }],
                    max_tokens=256,
                    temperature=0.4,
                ))
            text = (response['choices'][0]['message']['content'] or '').strip()
            latency = time.time() - start

            with state.lock:
                state.current_description = text
                state.current_frame_jpg = buf.tobytes()
                state.inference_fps = 1.0 / latency

            print(f"({latency:.2f}s) {text}")

        except Exception as e:
            print(f"Error: {e}")
            time.sleep(1)
