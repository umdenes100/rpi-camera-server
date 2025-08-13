#!/usr/bin/env python3
import cv2
import sys
import subprocess

# ─────────────────────────────────────────────────────────────────
# 1) EDIT THESE VALUES TO MATCH YOUR NETWORK/SETUP
# ─────────────────────────────────────────────────────────────────

GST_HOST = "X.X.X.X"
GST_PORT = 554
CAP_WIDTH = 1920
CAP_HEIGHT = 1080
CAP_FPS = 30

# ─────────────────────────────────────────────────────────────────
def main():
    # Open camera
    cap = cv2.VideoCapture(0, cv2.CAP_V4L2)
    if not cap.isOpened():
        print("✘ ERROR: Unable to open camera")
        sys.exit(1)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAP_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAP_HEIGHT)
    cap.set(cv2.CAP_PROP_FPS, CAP_FPS)

    # Build gst-launch pipeline arguments for RTP/JPEG
    gst_cmd = [
        "gst-launch-1.0", "-v",
        "fdsrc", "fd=0", "!",
        "jpegparse", "!",
        "rtpjpegpay", "pt=26", "!",
        "udpsink", f"host={GST_HOST}", f"port={GST_PORT}", "sync=false"
    ]

    proc = subprocess.Popen(gst_cmd, stdin=subprocess.PIPE)
    print(f"✔ Started gst-launch pipeline sending to {GST_HOST}:{GST_PORT}")

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("✘ WARNING: Frame grab failed")
                break
            # Encode frame as MJPEG chunk
            ret2, mjpeg = cv2.imencode('.jpg', frame)
            if not ret2:
                continue
            # Write JPEG bytes, and a GST frame delimiter (JPEG parse can handle raw concatenated JPEGs)
            proc.stdin.write(mjpeg.tobytes())
    except KeyboardInterrupt:
        print("\nInterrupted by user.")
    finally:
        cap.release()
        proc.stdin.close()
        proc.terminate()
        proc.wait()
        print("✔ Cleaned up.")

if __name__ == '__main__':
    main()
