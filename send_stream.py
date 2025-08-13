#!/usr/bin/env python3
import cv2
import sys
import subprocess
import threading
import queue

# ─────────────────────────────────────────────────────────────────
# 1) EDIT THESE VALUES TO MATCH YOUR NETWORK/SETUP
# ─────────────────────────────────────────────────────────────────

GST_HOST = "X.X.X.X"
GST_PORT = 554
CAP_WIDTH = 1280   # reduce resolution for speed
CAP_HEIGHT = 720
CAP_FPS = 30
JPEG_QUALITY = 80  # lower quality to speed encoding (0-100)

# ─────────────────────────────────────────────────────────────────

def gst_process():
    gst_cmd = [
        "gst-launch-1.0", "-v",
        "fdsrc", "fd=0", "!",
        "jpegparse", "!",
        "rtpjpegpay", "pt=26", "!",
        "udpsink", f"host={GST_HOST}", f"port={GST_PORT}", "sync=false"
    ]
    return subprocess.Popen(gst_cmd, stdin=subprocess.PIPE)


def capture_frames(cap, q):
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        q.put(frame)
    cap.release()


def encode_and_send(q, proc):
    encode_params = [int(cv2.IMWRITE_JPEG_QUALITY), JPEG_QUALITY]
    while True:
        frame = q.get()
        if frame is None:
            break
        ret, buf = cv2.imencode('.jpg', frame, encode_params)
        if not ret:
            continue
        try:
            proc.stdin.write(buf.tobytes())
        except BrokenPipeError:
            break
    proc.stdin.close()


def main():
    cap = cv2.VideoCapture(0, cv2.CAP_V4L2)
    if not cap.isOpened():
        print("✘ ERROR: Unable to open camera")
        sys.exit(1)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAP_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAP_HEIGHT)
    cap.set(cv2.CAP_PROP_FPS, CAP_FPS)

    proc = gst_process()
    print(f"✔ gst-launch started, streaming to {GST_HOST}:{GST_PORT}")

    frame_queue = queue.Queue(maxsize=CAP_FPS * 2)
    t_cap = threading.Thread(target=capture_frames, args=(cap, frame_queue), daemon=True)
    t_enc = threading.Thread(target=encode_and_send, args=(frame_queue, proc), daemon=True)
    t_cap.start()
    t_enc.start()

    try:
        while t_cap.is_alive():
            t_cap.join(timeout=1)
    except KeyboardInterrupt:
        print("\nInterrupted by user.")

    frame_queue.put(None)
    t_enc.join()
    proc.terminate()
    proc.wait()
    print("✔ Streaming stopped and cleaned up.")

if __name__ == '__main__':
    main()
