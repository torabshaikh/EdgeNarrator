import time
import cv2
from flask import Flask, Response, jsonify, render_template
import state

app = Flask(__name__)
_vs = None


@app.route('/')
def index():
    return render_template('index.html', prompt=state.prompt)


@app.route('/video_feed')
def video_feed():
    def generate():
        while True:
            try:
                frame = _vs.read()
                if frame is None:
                    time.sleep(0.1)
                    continue
                with state.lock:
                    fps = state.inference_fps
                display = frame.copy()
                cv2.putText(display, f"AI: {fps:.2f} fps", (10, 28),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                ret, buf = cv2.imencode('.jpg', display)
                if ret:
                    yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + buf.tobytes() + b'\r\n')
            except GeneratorExit:
                return
            except Exception:
                return

    return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/status')
def status():
    with state.lock:
        return jsonify({'text': state.current_description})


@app.route('/snapshot')
def snapshot():
    with state.lock:
        frame = state.current_frame_jpg
    if frame is None:
        return '', 204
    return Response(frame, mimetype='image/jpeg')


def start(vs, host='0.0.0.0', port=5000):
    global _vs
    _vs = vs
    app.run(host=host, port=port, threaded=True)
