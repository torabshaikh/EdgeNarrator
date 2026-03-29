# EdgeNarrator

Real-time scene description for live video streams. Frames are analyzed by a local [Moondream](https://huggingface.co/vikhyatk/moondream2) vision model via [llama-cpp-python](https://github.com/abetlen/llama-cpp-python), and the resulting description is overlaid on a browser-accessible dashboard with optional text-to-speech.


## Demo (Nvidia Jetson Orin Nano 8GB)

[![EdgeNarrator Demo](https://img.youtube.com/vi/LHt7xKSdf30/maxresdefault.jpg)](https://youtu.be/LHt7xKSdf30)


## Features

- Works with local webcams and RTSP streams
- Runs inference locally — no cloud dependency
- GPU-accelerated via CUDA (Jetson and discrete NVIDIA GPUs)
- Live web dashboard: MJPEG video feed with inference FPS overlay
- Scrolling sidebar showing each result alongside a thumbnail of the analyzed frame
- Browser text-to-speech — speaks the latest result, never interrupts mid-sentence

---

## Requirements

- Python 3.13+
- CUDA toolkit (for GPU inference)
- OpenCV-compatible camera or RTSP stream

---

## Installation

```bash
git clone https://github.com/torabshaikh/EdgeNarrator.git
cd EdgeNarrator
python -m venv .venv
source .venv/bin/activate
pip install opencv-python flask
```

Install llama-cpp-python with CUDA support:

```bash
# Standard (x86_64)
CMAKE_ARGS="-DGGML_CUDA=on" pip install llama-cpp-python

# Jetson Orin (sm_87)
CMAKE_ARGS="-DGGML_CUDA=on -DCMAKE_CUDA_ARCHITECTURES=87" pip install llama-cpp-python
```

---

## Models

Model files are not included in this repo. Download from Hugging Face:

```bash
pip install huggingface-hub
huggingface-cli download vikhyatk/moondream2-gguf \
    moondream2-text-model-f16.gguf \
    moondream2-mmproj-f16.gguf \
    --local-dir models/
```

The F16 text model works as-is. For faster inference, quantize it locally:

```bash
git clone --depth 1 https://github.com/ggerganov/llama.cpp
cd llama.cpp
cmake -B build && cmake --build build --target llama-quantize -j$(nproc)
./build/bin/llama-quantize ../models/moondream2-text-model-f16.gguf ../models/moondream2-text-model-q4_k_m.gguf Q4_K_M
cd ..
```

The projector (`mmproj`) should stay at F16.

---

## Usage

```bash
python main.py <source> [--prompt "..."]
```

| Argument | Example |
|----------|---------|
| Local webcam | `python main.py 0` |
| RTSP stream | `python main.py rtsp://192.168.1.10:554/stream` |
| Custom prompt | `python main.py 0 --prompt "Is there any person in the scene?"` |
| Custom model | `python main.py 0 --model models/moondream2-text-model-f16.gguf` |
| Custom projector | `python main.py 0 --mmproj models/moondream2-mmproj-f16.gguf` |

Then open **http://localhost:5000** in a browser.

---

## Project Structure

```
EdgeNarrator/
├── main.py           # Entry point: arg parsing, wires modules together
├── state.py          # Shared state: description, analyzed frame, inference FPS
├── video_stream.py   # Threaded VideoStream class (webcam + RTSP)
├── analyzer.py       # Inference loop (llama-cpp-python + Moondream)
├── server.py         # Flask web dashboard (MJPEG feed, sidebar, TTS)
└── utils.py          # CUDA runtime detection
```

---

## Configuration

The prompt can be changed at runtime via `--prompt` (see Usage above).

To change the model or resolution, edit the constants at the top of `analyzer.py`:

| Flag | Default | Description |
|------|---------|-------------|
| `--model` | `moondream2-text-model-q4_k_m.gguf` | Text model GGUF |
| `--mmproj` | `moondream2-mmproj-f16.gguf` | Vision projector GGUF |
| `--prompt` | `"Please describe the scene within 20 words"` | Inference prompt |

---

## License

[MIT](LICENSE)
