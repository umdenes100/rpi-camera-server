#!/usr/bin/env python3
import sys
import subprocess
import threading
import time
import shutil
import os
import signal

# ─────────────────────────────────────────────────────────────────
# 1) EDIT THESE VALUES TO MATCH YOUR NETWORK/SETUP
# ─────────────────────────────────────────────────────────────────

GST_HOST = "X.X.X.X"
GST_PORT = 554
CAP_WIDTH = 1280   # camera output width
CAP_HEIGHT = 720   # camera output height
CAP_FPS = 30       # camera output fps
JPEG_QUALITY = 80  # libcamera-vid MJPEG quality (1-100)

# ─────────────────────────────────────────────────────────────────

def require(cmd):
    if shutil.which(cmd) is None:
        print(f"✘ ERROR: '{cmd}' not found in PATH.")
        sys.exit(1)

def libcamera_process():
    """
    Start libcamera-vid to capture from the CSI Camera Module (RPi Cam v3 Wide)
    and emit an MJPEG byte stream on stdout.
    """
    # Notes:
    #  -t 0        : run forever
    # --codec mjpeg: MJPEG stream
    # --quality    : JPEG quality (1..100)
    # -o -         : write to stdout
    cmd = [
        "libcamera-vid",
        "-t", "0",
        "--width", str(CAP_WIDTH),
        "--height", str(CAP_HEIGHT),
        "--framerate", str(CAP_FPS),
        "--codec", "mjpeg",
        "--quality", str(JPEG_QUALITY),
        "-o", "-"
    ]
    # stderr captured for debugging
    return subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=0)

def gst_process():
    """
    Start GStreamer to read MJPEG from stdin and send as RTP/JPEG over UDP.
    """
    cmd = [
        "gst-launch-1.0", "-v",
        "fdsrc", "fd=0", "!",
        "jpegparse", "!",
        "rtpjpegpay", "pt=26", "!",
        "udpsink", f"host={GST_HOST}", f"port={GST_PORT}", "sync=false"
    ]
    return subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, bufsize=0)

def pump_stream(src_proc, dst_proc):
    """
    Read bytes from libcamera-vid stdout and write them into gst-launch stdin.
    """
    try:
        src = src_proc.stdout
        dst = dst_proc.stdin
        # Read in chunks; jpegparse will find frame boundaries
        while True:
            chunk = src.read(65536)
            if not chunk:
                break
            try:
                dst.write(chunk)
            except (BrokenPipeError, ValueError):
                break
    finally:
        try:
            if dst_proc.stdin:
                dst_proc.stdin.close()
        except Exception:
            pass

def print_proc_exit(tag, proc):
    if proc and proc.poll() is not None:
        try:
            err = (proc.stderr.read() if proc.stderr else b"").decode(errors="ignore").strip()
        except Exception:
            err = ""
        if err:
            print(f"✘ {tag} exited.\n--- {tag} stderr ---\n{err}\n--- end ---")

def terminate_tree(proc):
    if not proc:
        return
    try:
        if proc.poll() is None:
            # Try graceful first
            proc.terminate()
            proc.wait(timeout=2)
    except Exception:
        try:
            os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
        except Exception:
            pass

def main():
    require("libcamera-vid")
    require("gst-launch-1.0")

    cam = libcamera_process()
    if cam.stdout is None:
        print("✘ ERROR: libcamera-vid stdout not available.")
        sys.exit(1)

    gst = gst_process()
    print(f"✔ gst-launch started, streaming to {GST_HOST}:{GST_PORT}")

    t_pump = threading.Thread(target=pump_stream, args=(cam, gst), daemon=True)
    t_pump.start()

    # Monitor both processes (similar spirit to your original main loop)
    try:
        while True:
            time.sleep(0.2)
            cam_rc = cam.poll()
            gst_rc = gst.poll()
            if cam_rc is not None:
                print("ℹ libcamera-vid ended; stopping stream.")
                break
            if gst_rc is not None:
                print_proc_exit("gst-launch", gst)
                print("ℹ gst-launch ended; stopping stream.")
                break
    except KeyboardInterrupt:
        print("\nInterrupted by user.")
    finally:
        # Cleanup
        terminate_tree(gst)
        terminate_tree(cam)
        t_pump.join(timeout=2)
        print_proc_exit("libcamera-vid", cam)
        print_proc_exit("gst-launch", gst)
        print("✔ Streaming stopped and cleaned up.")

if __name__ == '__main__':
    main()
