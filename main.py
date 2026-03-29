import argparse
import threading
import analyzer
import server
import state
from video_stream import VideoStream


def parse_args():
    parser = argparse.ArgumentParser(description="EdgeNarrator: live video scene narrator")
    parser.add_argument("url", type=str, help="Stream URL or camera index (e.g. 0, rtsp://...)")
    parser.add_argument("--prompt", type=str, default=analyzer.PROMPT, help="Inference prompt")
    parser.add_argument("--model", type=str, default=analyzer.DEFAULT_MODEL_PATH, help="Path to text model GGUF")
    parser.add_argument("--mmproj", type=str, default=analyzer.DEFAULT_CLIP_PATH, help="Path to vision projector GGUF")
    return parser.parse_args()


def main():
    args = parse_args()
    src = int(args.url) if args.url.isdigit() else args.url

    print(f"Connecting to {src}...")
    vs = VideoStream(src).start()

    state.prompt = args.prompt
    threading.Thread(target=analyzer.run, args=(vs, args.prompt, args.model, args.mmproj), daemon=True).start()

    print("Dashboard ready at http://localhost:5000")
    server.start(vs)


if __name__ == "__main__":
    main()
