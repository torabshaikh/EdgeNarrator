import time
import cv2
import ollama
import state

MODEL = "moondream"
FRAME_SIZE = (336, 336)
PROMPT = "Please describe the scene within 20 words"


def run(vs, prompt=PROMPT):
    print("Connecting to Ollama...")
    try:
        ollama.chat(model=MODEL, messages=[{'role': 'user', 'content': 'hi'}])
        print("AI engine ready.")
    except Exception as e:
        print("Error: Ollama is not running. Run 'ollama serve' in a terminal.")
        return

    while True:
        frame = vs.read()
        if frame is None:
            time.sleep(0.1)
            continue

        try:
            frame_resized = cv2.resize(frame, FRAME_SIZE)
            _, buffer = cv2.imencode('.jpg', frame_resized)
            img_bytes = buffer.tobytes()

            start = time.time()
            response = ollama.chat(
                model=MODEL,
                messages=[{
                    'role': 'user',
                    'content': prompt,
                    'images': [img_bytes],
                }]
            )
            text = response['message']['content'].strip()
            latency = time.time() - start

            with state.lock:
                state.current_description = text
                state.current_frame_jpg = img_bytes
                state.inference_fps = 1.0 / latency

            print(f"({latency:.2f}s) {text}")

        except Exception as e:
            print(f"Error: {e}")
            time.sleep(1)
