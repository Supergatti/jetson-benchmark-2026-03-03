import os
import time
import sys
from pathlib import Path

OUT_DIR = Path(__file__).resolve().parents[1] / 'outputs'
OUT_DIR.mkdir(parents=True, exist_ok=True)

LOGFILE = OUT_DIR / 'yolo_benchmark_results.txt'
IMG_PATH = OUT_DIR / 'sample.jpg'


def log(msg):
    print(msg)
    with open(LOGFILE, 'a') as f:
        f.write(msg + '\n')


def download_sample():
    if IMG_PATH.exists():
        return
    try:
        import urllib.request
        url = 'https://ultralytics.com/images/bus.jpg'
        urllib.request.urlretrieve(url, IMG_PATH)
        log(f'Downloaded sample image to {IMG_PATH}')
    except Exception as e:
        log(f'Could not download sample image: {e}')


def find_camera():
    # prefer /dev/video0
    dev = '/dev/video0'
    if Path(dev).exists():
        return 0
    # fallback: try sequential indices
    for i in range(1, 6):
        if Path(f'/dev/video{i}').exists():
            return i
    return None


def run_inference_with_ultralytics(model_name='yolov8n.pt', device='cuda', img_size=640, runs=50):
    try:
        from ultralytics import YOLO
    except Exception as e:
        log(f'ultralytics import failed: {e}')
        return False

    log(f'Loading model {model_name}')
    model = YOLO(model_name)

    # try device strategies: cuda (fp32) -> cuda(fp16) -> cpu
    strategies = []
    if device == 'cuda':
        strategies = ['cuda', 'cuda_fp16', 'cpu']
    elif device == 'cpu':
        strategies = ['cpu']
    else:
        strategies = [device, 'cpu']

    cam_idx = find_camera()
    if cam_idx is None:
        log('No camera found; falling back to image-based test')
        return False

    try:
        import cv2
    except Exception as e:
        log(f'OpenCV not available: {e}')
        return False

    cap = cv2.VideoCapture(cam_idx)
    if not cap.isOpened():
        log(f'Could not open camera index {cam_idx}')
        return False

    for strat in strategies:
        try:
            log(f'Trying strategy: {strat}')
            if strat == 'cuda':
                dev_arg = 'cuda'
            elif strat == 'cuda_fp16':
                dev_arg = 'cuda'
                try:
                    model.model.half()
                    log('Requested model half precision')
                except Exception:
                    log('Could not set model to half precision')
            else:
                dev_arg = 'cpu'

            # Warmup: read a couple frames
            warmup_frames = 2
            for _ in range(warmup_frames):
                ret, frame = cap.read()
                if not ret:
                    break
                try:
                    _ = model(frame, device=dev_arg)
                except Exception as e:
                    log(f'Warmup inference failed under {strat}: {e}')
                    raise

            # Timed capture
            times = []
            log(f'Starting capture-based timed runs ({runs} frames) on {dev_arg}...')
            for i in range(runs):
                t0 = time.time()
                ret, frame = cap.read()
                if not ret:
                    log('Camera read failed, ending')
                    break
                try:
                    _ = model(frame, device=dev_arg)
                    t1 = time.time()
                    times.append(t1 - t0)
                    if (i + 1) % 10 == 0:
                        log(f'Processed {i+1}/{runs} frames')
                except Exception as e:
                    log(f'Inference failed on frame {i+1} under {strat}: {e}')
                    raise

            if times:
                avg = sum(times) / len(times)
                fps = 1.0 / avg if avg > 0 else 0.0
                log(f'Strategy {strat} — Average time: {avg:.4f}s, FPS: {fps:.2f} (over {len(times)} frames)')
                cap.release()
                return True
            else:
                log(f'No successful frames for strategy {strat}')

        except Exception as e:
            log(f'Strategy {strat} failed: {e}')
            # continue to next strategy
            continue

    cap.release()
    log('All strategies failed')
    return False


def main():
    # Clear logfile
    if LOGFILE.exists():
        LOGFILE.unlink()
    log('YOLO camera verification started')
    download_sample()
    ok = run_inference_with_ultralytics('yolov8n.pt', device='cuda', img_size=640, runs=30)
    if not ok:
        log('Ultralytics camera inference failed; will retry on CPU')
        ok2 = run_inference_with_ultralytics('yolov8n.pt', device='cpu', img_size=640, runs=30)
        if not ok2:
            log('CPU fallback also failed; aborting')
            sys.exit(1)
    log('YOLO camera verification finished')


if __name__ == "__main__":
    main()
