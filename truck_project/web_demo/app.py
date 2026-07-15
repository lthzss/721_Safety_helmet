from pathlib import Path
import cv2
import time
import atexit
from datetime import datetime
from flask import Flask, render_template, Response, jsonify
from ultralytics import YOLO
from picamera2 import Picamera2
from gpiozero import LED, DigitalOutputDevice
import lgpio

app = Flask(__name__)

project_root = Path(__file__).resolve().parent.parent
model_path = project_root / "heatyolo11" / "heatyolo11" / "weights" / "best.pt"
model = YOLO(str(model_path))

picam2 = Picamera2()
config = picam2.create_preview_configuration(main={"size": (640, 480)})
picam2.configure(config)
picam2.start()

PIN_BUZZER = 17
PIN_LED_RED = 22
PIN_LED_YELLOW = 23
PIN_LED_GREEN = 24
PIN_KEY1 = 25
PIN_KEY2 = 5
PIN_SERVO = 12
SERVO_FREQ = 50.0
SERVO_DUTY_A = 2.5
SERVO_DUTY_B = 7.5

lgpio_h = lgpio.gpiochip_open(0)
lgpio.gpio_claim_output(lgpio_h, PIN_SERVO)

def servo_set(duty):
    lgpio.tx_pwm(lgpio_h, PIN_SERVO, SERVO_FREQ, duty)
    time.sleep(0.15)
    lgpio.tx_pwm(lgpio_h, PIN_SERVO, 0, 0)

BUZZER_THRESHOLD = 0.5
buzzer = LED(PIN_BUZZER, active_high=False)
led_red = LED(PIN_LED_RED)
led_yellow = LED(PIN_LED_YELLOW)
led_green = LED(PIN_LED_GREEN)
key1 = DigitalOutputDevice(PIN_KEY1)
key2 = DigitalOutputDevice(PIN_KEY2)
servo_set(SERVO_DUTY_A)

def cleanup():
    lgpio.tx_pwm(lgpio_h, PIN_SERVO, 0, 0)
    lgpio.gpiochip_close(lgpio_h)

atexit.register(cleanup)

current_output_state = None

def set_output_state(state):
    global current_output_state
    if state == current_output_state:
        return
    current_output_state = state
    if state == "waiting":
        led_red.off()
        led_yellow.on()
        led_green.off()
        key1.off()
        key2.off()
        servo_set(SERVO_DUTY_A)
    elif state == "person":
        led_red.on()
        led_yellow.off()
        led_green.off()
        key1.on()
        key2.off()
        servo_set(SERVO_DUTY_A)
    elif state == "hat":
        led_red.off()
        led_yellow.off()
        led_green.on()
        key1.off()
        key2.on()
        servo_set(SERVO_DUTY_B)

set_output_state("waiting")

latest_label = "waiting"
latest_conf = 0.0
latest_fps = 0.0
latest_status = "running"
prev_time = time.time()

daily_counts = {"hat": 0, "person": 0}
daily_date = datetime.now().strftime("%Y-%m-%d")
COOLDOWN_SECONDS = 3
last_count_time = {"hat": 0.0, "person": 0.0}

timeline_data = {}
MAX_TIMELINE = 12
INTERVAL_SECONDS = 10

log_entries = []
MAX_LOG = 100

previous_label = "waiting"


def reset_daily_stats_if_needed():
    global daily_counts, daily_date, timeline_data, last_count_time
    today = datetime.now().strftime("%Y-%m-%d")
    if today != daily_date:
        daily_counts = {"hat": 0, "person": 0}
        daily_date = today
        last_count_time = {"hat": 0.0, "person": 0.0}
        timeline_data.clear()
        log_entries.clear()


def gen_frames():
    global latest_label, latest_conf, latest_fps, latest_status, prev_time
    global previous_label, timeline_data, last_count_time

    colors = {"hat": (0, 255, 0), "person": (255, 0, 0)}

    while True:
        frame_rgba = picam2.capture_array()
        frame = cv2.cvtColor(frame_rgba, cv2.COLOR_RGBA2BGR)

        results = model(frame, verbose=False)
        r = results[0]

        boxes = r.boxes
        if boxes is not None and len(boxes) > 0:
            top_box = boxes[0]
            top_cls = int(top_box.cls[0])
            top_label = r.names[top_cls]
            top_conf = float(top_box.conf[0])

            person_detected = False
            hat_detected = False
            for box in boxes:
                cls = int(box.cls[0])
                label = r.names[cls]
                conf = float(box.conf[0])
                if label == "person" and conf >= BUZZER_THRESHOLD:
                    person_detected = True
                if label == "hat":
                    hat_detected = True
                x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
                color = colors.get(label, (128, 128, 128))
                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                cv2.putText(frame, f"{label} {conf:.2f}", (x1, y1 - 8),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

            if person_detected:
                latest_label = "person"
                latest_conf = top_conf
                set_output_state("person")
                buzzer.on()
            elif hat_detected:
                latest_label = "hat"
                latest_conf = top_conf
                set_output_state("hat")
                buzzer.off()
            else:
                latest_label = top_label
                latest_conf = top_conf
                set_output_state("waiting")
                buzzer.off()

            reset_daily_stats_if_needed()
            now = time.time()
            if latest_label in daily_counts and now - last_count_time.get(latest_label, 0) >= COOLDOWN_SECONDS:
                daily_counts[latest_label] += 1
                last_count_time[latest_label] = now
                interval_key = str(int(now // INTERVAL_SECONDS))
                if interval_key not in timeline_data:
                    timeline_data[interval_key] = {"hat": 0, "person": 0}
                    if len(timeline_data) > MAX_TIMELINE:
                        oldest = sorted(timeline_data.keys())[0]
                        del timeline_data[oldest]
                timeline_data[interval_key][latest_label] = timeline_data[interval_key].get(latest_label, 0) + 1
            if latest_label != previous_label:
                ts = datetime.now().strftime("%H:%M:%S")
                log_entries.insert(0, {"time": ts, "label": latest_label, "conf": round(latest_conf, 4)})
                if len(log_entries) > MAX_LOG:
                    log_entries.pop()
                previous_label = latest_label
        else:
            latest_label = "waiting"
            latest_conf = 0.0
            set_output_state("waiting")

        current_time = time.time()
        latest_fps = 1.0 / (current_time - prev_time) if current_time != prev_time else 0.0
        prev_time = current_time

        latest_status = "running"

        cv2.putText(frame, f"Detections: {latest_label}", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0), 2)
        cv2.putText(frame, f"Conf: {latest_conf:.4f}", (20, 80), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 255), 2)
        cv2.putText(frame, f"FPS: {latest_fps:.2f}", (20, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 0, 0), 2)

        ret, buffer = cv2.imencode(".jpg", frame)
        if not ret:
            continue

        frame_bytes = buffer.tobytes()
        yield (
            b"--frame\r\n"
            b"Content-Type: image/jpeg\r\n\r\n" + frame_bytes + b"\r\n"
        )


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/video_feed")
def video_feed():
    return Response(gen_frames(), mimetype="multipart/x-mixed-replace; boundary=frame")


@app.route("/result")
def result():
    return jsonify({
        "label": latest_label,
        "conf": round(latest_conf, 4),
        "fps": round(latest_fps, 2),
        "status": latest_status
    })


@app.route("/stats")
def stats():
    reset_daily_stats_if_needed()
    return jsonify(daily_counts)


@app.route("/timeline")
def timeline():
    reset_daily_stats_if_needed()
    sorted_keys = sorted(timeline_data.keys(), key=lambda k: int(k))
    labels = []
    for k in sorted_keys:
        t = datetime.fromtimestamp(int(k) * INTERVAL_SECONDS)
        labels.append(t.strftime("%H:%M:%S"))
    return jsonify({
        "labels": labels,
        "hat": [timeline_data[k].get("hat", 0) for k in sorted_keys],
        "person": [timeline_data[k].get("person", 0) for k in sorted_keys]
    })


@app.route("/logs")
def logs():
    return jsonify(log_entries)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True, use_reloader=False)
