
import streamlit as st
import random
import time
import io
import wave
import math
import base64
from datetime import datetime
from collections import deque

st.set_page_config(page_title="DriveSentinel AI", page_icon="DS", layout="wide")


# Use Streamlit's built-in browser camera.
# This avoids native DLL dependencies such as av, cv2, and streamlit-webrtc.
CAMERA_READY = True
CAMERA_ERROR = ""


def alarm_audio_html():
    """Create a short repeating two-tone alarm as an in-memory WAV file."""
    sample_rate = 22050
    duration = 1.6
    frames = []

    for index in range(int(sample_rate * duration)):
        t = index / sample_rate
        frequency = 880 if int(t * 4) % 2 == 0 else 620
        envelope = 0.42
        sample = int(32767 * envelope * math.sin(2 * math.pi * frequency * t))
        frames.append(sample.to_bytes(2, byteorder="little", signed=True))

    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(b"".join(frames))

    encoded = base64.b64encode(buffer.getvalue()).decode("ascii")
    return f"""
    <audio autoplay loop>
        <source src="data:audio/wav;base64,{encoded}" type="audio/wav">
    </audio>
    """


defaults = {
    "monitoring": True,
    "alerts": 0,
    "events": deque(maxlen=12),
    "fatigue_history": deque([random.randint(8, 35) for _ in range(20)], maxlen=40),
    "emergency": False,
}
for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

if not st.session_state.events:
    st.session_state.events.extend([
        ("SYSTEM", "Monitoring session initialized", "INFO"),
        ("SYSTEM", "Driver profile loaded", "INFO"),
        ("SYSTEM", "Vision engine ready", "INFO"),
    ])


st.markdown("""
<style>
:root {
    --ink: #edf3ff;
    --muted: #9eabc0;
    --line: #34435b;
    --paper: #101827;
    --card: #1b2638;
    --navy: #263b63;
    --blue: #3f6fd9;
    --teal: #178f8b;
    --amber: #c58a24;
    --red: #c94b55;
}

* {
    font-family: "Segoe UI", Arial, sans-serif;
}

.stApp {
    background: linear-gradient(135deg, #0e1727 0%, #15233a 55%, #101827 100%);
    color: var(--ink);
}

[data-testid="stSidebar"] {
    background: #202d47;
    border-right: 1px solid #172238;
}

[data-testid="stSidebar"] * {
    color: #e9eef8;
}

[data-testid="stSidebar"] .stRadio label {
    padding: 7px 8px;
    border-radius: 6px;
}

.block-container {
    max-width: 1450px;
    padding: 2.2rem 2.6rem;
}

.brand {
    padding-bottom: 20px;
    border-bottom: 1px solid #40506b;
    margin-bottom: 22px;
}

.brand b {
    font-size: 22px;
    letter-spacing: -0.6px;
    color: #ffffff;
}

.brand b span {
    color: #66d2c7;
}

.brand small {
    display: block;
    color: #aab7ce;
    font-size: 9px;
    letter-spacing: 1.6px;
    margin-top: 7px;
}

.eyebrow {
    color: #60749a;
    font-size: 10px;
    font-weight: 750;
    letter-spacing: 1.7px;
}

.sub {
    color: var(--muted);
    font-size: 13px;
    margin-bottom: 25px;
}

.card, .kpi {
    background: var(--card);
    border: 1px solid var(--line);
    border-radius: 12px;
    padding: 21px;
    box-shadow: 0 3px 12px rgba(36, 52, 78, 0.045);
}

.kpi {
    min-height: 116px;
    border-top: 3px solid #dbe5f6;
}

.label {
    font-size: 10px;
    letter-spacing: 1.1px;
    color: #78849a;
    font-weight: 750;
}

.value {
    font-size: 29px;
    font-weight: 750;
    margin-top: 12px;
    color: var(--ink);
    letter-spacing: -0.7px;
}

.note {
    font-size: 11px;
    color: #8993a5;
    margin-top: 5px;
}

.head {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 17px;
}

.title {
    font-size: 15px;
    font-weight: 750;
    color: #edf3ff;
}

.caption {
    font-size: 11px;
    color: #8993a5;
    margin-top: 4px;
}

.pill {
    border: 1px solid #b8e1dc;
    background: #e9f8f5;
    color: #167d77;
    border-radius: 20px;
    padding: 6px 11px;
    font-size: 9px;
    font-weight: 750;
}

.status {
    padding: 19px;
    border-radius: 10px;
    margin-bottom: 18px;
    background: #edf7f5;
    border: 1px solid #c9e6e0;
}

.status strong {
    display: block;
    color: #167d77;
    font-size: 26px;
    margin-top: 7px;
}

.metric-line {
    display: flex;
    justify-content: space-between;
    padding: 11px 0;
    border-bottom: 1px solid #edf0f5;
    font-size: 11px;
}

.metric-line span:first-child {
    color: #78849a;
    font-size: 10px;
}

.metric-line span:last-child {
    color: #dbe6f7;
    font-weight: 650;
}

.event {
    padding: 11px 0;
    border-bottom: 1px solid #edf0f5;
}

.event small {
    color: #8993a5;
    font-size: 9px;
}

.event p {
    margin: 4px 0 0;
    color: #d4deed;
    font-size: 11px;
}

div.stButton > button {
    background: #223149;
    border: 1px solid #465a78;
    border-radius: 7px;
    color: #30415f;
    font-size: 12px;
    font-weight: 600;
    transition: border-color 0.15s ease, background 0.15s ease;
}

div.stButton > button:hover {
    border-color: var(--blue);
    background: #29456e;
    color: #2f5fc3;
}

.camera-note {
    padding: 15px;
    border: 1px dashed #b8c5d8;
    border-radius: 9px;
    background: #162236;
    color: #7a879c;
    font-size: 12px;
    text-align: center;
}

.risk-chip {
    display: inline-block;
    padding: 5px 10px;
    border-radius: 20px;
    background: #fff5df;
    color: #a26c13;
    border: 1px solid #efd8a6;
    font-size: 9px;
    font-weight: 750;
}

.feature-box {
    background: #1b2638;
    border: 1px solid var(--line);
    border-radius: 10px;
    padding: 15px;
    min-height: 92px;
}

.feature-box b {
    font-size: 23px;
    color: var(--ink);
}

.feature-box span {
    display: block;
    color: #8993a5;
    font-size: 10px;
    margin-top: 5px;
}

.alert-box {
    background: #fff0f1;
    border: 1px solid #efc4c8;
    color: #b13f4b;
    border-radius: 9px;
    padding: 14px;
    font-size: 12px;
}

[data-testid="stMetric"] {
    background: #1b2638;
    border: 1px solid var(--line);
    border-radius: 10px;
    padding: 12px;
}

[data-testid="stProgressBar"] > div > div {
    background: var(--teal);
}
</style>
""", unsafe_allow_html=True)


with st.sidebar:
    st.markdown('<div class="brand"><b>◈ DRIVESENTINEL<span>AI</span></b><small>DRIVER FATIGUE INTELLIGENCE</small></div>', unsafe_allow_html=True)
    page = st.radio("Workspace", ["Dashboard", "Live Camera", "Analytics", "Settings"], label_visibility="collapsed")
    st.markdown("---")
    st.markdown("#### Session profile")
    driver = st.text_input("Driver name", "Alex Morgan")
    vehicle = st.text_input("Vehicle ID", "DS-2048")
    sensitivity = st.select_slider("Detection sensitivity", ["Low", "Balanced", "High"], value="Balanced")
    st.session_state.monitoring = st.toggle("Monitoring active", value=st.session_state.monitoring)
    st.markdown("---")
    st.caption("Camera input: Browser mode")
    st.caption("Alert service: Ready")
    st.caption("Prototype mode")


if st.session_state.monitoring:
    fatigue = random.randint(8, 32)
    attention = random.randint(88, 98)
    eye_closure = round(random.uniform(0.08, 0.28), 2)
    blink = random.randint(14, 25)
    yawns = random.randint(0, 2)
else:
    fatigue, attention, eye_closure, blink, yawns = 0, 0, 0, 0, 0

state = "ALERT" if fatigue < 35 else "CAUTION" if fatigue < 65 else "DROWSY"
st.session_state.fatigue_history.append(fatigue)


st.markdown('<div class="eyebrow">DRIVESENTINEL / CONTROL CENTER</div>', unsafe_allow_html=True)
st.title("Driver Safety Overview")
st.markdown('<div class="sub">Live camera monitoring, fatigue indicators, intelligent alerts and session insights.</div>', unsafe_allow_html=True)

q1, q2, q3, q4 = st.columns(4)
quick = [("BLINK RATE", f"{blink}/min", "Eye activity"), ("YAWNS", str(yawns), "Detected events"), ("CONFIDENCE", f"{min(attention + 1, 99)}%", "Vision estimate"), ("SESSION", "ACTIVE" if st.session_state.monitoring else "PAUSED", "Monitoring state")]
for col, (name, value, desc) in zip([q1, q2, q3, q4], quick):
    with col:
        st.markdown(f'<div class="feature-box"><div class="label">{name}</div><b>{value}</b><span>{desc}</span></div>', unsafe_allow_html=True)

if st.button("Refresh sensor simulation"):
    st.rerun()

# Additional operational indicators.
session_mode = "Active monitoring" if st.session_state.monitoring else "Monitoring paused"
risk_band = "Low exposure" if fatigue < 35 else "Review recommended" if fatigue < 65 else "Immediate attention"
st.markdown(
    f'<div class="card" style="margin: 18px 0;">'
    f'<div class="head"><div><div class="title">Operational snapshot</div>'
    f'<div class="caption">Quick status indicators for the current driving session</div></div>'
    f'<span class="risk-chip">{risk_band}</span></div>'
    f'<div class="metric-line"><span>Session mode</span><span>{session_mode}</span></div>'
    f'<div class="metric-line"><span>Driver profile</span><span>{driver}</span></div>'
    f'<div class="metric-line"><span>Vehicle identifier</span><span>{vehicle}</span></div>'
    f'<div class="metric-line"><span>Detection profile</span><span>{sensitivity}</span></div>'
    f'</div>',
    unsafe_allow_html=True
)

kpis = [
    ("DRIVER STATE", state, "Current classification"),
    ("FATIGUE INDEX", f"{fatigue}%", "Simulated risk score"),
    ("ATTENTION", f"{attention}%", "Estimated attention"),
    ("ALERT EVENTS", str(st.session_state.alerts), "Session notifications"),
]
cols = st.columns(4)
for col, (label, value, note) in zip(cols, kpis):
    with col:
        st.markdown(f'<div class="kpi"><div class="label">{label}</div><div class="value">{value}</div><div class="note">{note}</div></div>', unsafe_allow_html=True)

st.write("")


left, right = st.columns([1.4, 1], gap="large")

with left:
    st.markdown('<div class="card"><div class="head"><div><div class="title">Live driver camera</div><div class="caption">Webcam stream with optional visual overlay</div></div><span class="pill">● CAMERA</span></div>', unsafe_allow_html=True)

    if page in ["Dashboard", "Live Camera"]:
        st.info(
            "Use the browser camera button below. This mode does not require "
            "WebRTC, PyAV, OpenCV, or native camera DLLs."
        )

        captured_image = st.camera_input(
            "Open camera and capture driver image",
            key="driver_snapshot"
        )

        if captured_image is not None:
            st.image(
                captured_image,
                caption="Captured driver image",
                use_container_width=True
            )

            st.success(
                "Image captured successfully. Live continuous video processing "
                "requires a separately working WebRTC environment."
            )

            st.markdown(
                '<div class="metric-line"><span>Capture status</span><span>Received</span></div>'
                '<div class="metric-line"><span>Input source</span><span>Browser camera</span></div>'
                '<div class="metric-line"><span>Processing mode</span><span>Still image prototype</span></div>',
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                '<div class="camera-note">'
                'Click the camera control, allow browser permission, and capture an image.'
                '</div>',
                unsafe_allow_html=True
            )

        with st.expander("If the camera button does not open"):
            st.markdown(
                """
                1. Open the app using `localhost`, not a blocked remote URL.
                2. Click the camera icon in the browser prompt.
                3. Select **Allow** for camera permission.
                4. Check Windows Settings → Privacy & security → Camera.
                5. Make sure your browser is allowed to use the camera.
                """
            )

        st.markdown('</div>', unsafe_allow_html=True)

    st.write("")
    st.markdown('<div class="card"><div class="head"><div><div class="title">Visual indicators</div><div class="caption">Current simulated sensor outputs</div></div></div>', unsafe_allow_html=True)
    a, b = st.columns(2)
    with a:
        st.markdown(
            f'<div class="metric-line"><span>Eye closure duration</span><span>{eye_closure}s</span></div>'
            f'<div class="metric-line"><span>Blink frequency</span><span>{blink} / min</span></div>'
            f'<div class="metric-line"><span>Head orientation</span><span>Centered</span></div>',
            unsafe_allow_html=True
        )
    with b:
        st.markdown(
            f'<div class="metric-line"><span>Yawn events</span><span>{yawns}</span></div>'
            f'<div class="metric-line"><span>Sensitivity</span><span>{sensitivity}</span></div>'
            f'<div class="metric-line"><span>Tracking confidence</span><span>{min(attention + 1, 99)}%</span></div>',
            unsafe_allow_html=True
        )
    st.markdown('</div>', unsafe_allow_html=True)


with right:
    st.markdown(
        f'<div class="card"><div class="head"><div><div class="title">Risk assessment</div><div class="caption">Fatigue classification engine</div></div><span class="label">LIVE</span></div>'
        f'<div class="status"><div class="label">CURRENT STATUS</div><strong>{state}</strong><div class="caption">Prototype-generated driver behavior classification.</div></div>'
        f'<div class="label">FATIGUE INDEX</div>',
        unsafe_allow_html=True
    )
    st.progress(fatigue / 100 if fatigue else 0)
    st.markdown(
        f'<div class="metric-line"><span>Eye state</span><span>Open / Normal</span></div>'
        f'<div class="metric-line"><span>Driver attention</span><span>{attention}%</span></div>'
        f'<div class="metric-line"><span>Alert threshold</span><span>65%</span></div>'
        f'<div class="metric-line"><span>Vehicle</span><span>{vehicle}</span></div></div>',
        unsafe_allow_html=True
    )

    st.write("")
    if st.button("Trigger emergency alert", use_container_width=True):
        st.session_state.alerts += 1
        st.session_state.events.appendleft(
            (datetime.now().strftime("%H:%M:%S"), "Emergency fatigue alert triggered", "ALERT")
        )
        st.session_state.emergency = True
        st.rerun()

    if st.session_state.emergency:
        st.error("Simulated emergency alert triggered.")
        st.markdown(alarm_audio_html(), unsafe_allow_html=True)
        st.warning("Emergency alarm is active. Click Clear emergency alert to stop it.")

        if st.button("Clear emergency alert", use_container_width=True):
            st.session_state.emergency = False
            st.rerun()

    st.write("")
    st.markdown('<div class="card"><div class="head"><div><div class="title">Driver recommendations</div><div class="caption">Rule-based prototype suggestions</div></div></div>', unsafe_allow_html=True)
    if fatigue >= 65:
        recommendation = "Stop safely, take a break and avoid continuing to drive."
    elif fatigue >= 35:
        recommendation = "Increase ventilation and monitor fatigue indicators closely."
    else:
        recommendation = "Maintain attention and continue monitoring."
    st.info(recommendation)
    st.markdown('</div>', unsafe_allow_html=True)


st.write("")
si1, si2, si3 = st.columns(3)
with si1:
    st.markdown('<div class="card"><div class="title">Safety score</div><div class="value">{}</div><div class="note">Combined prototype estimate</div></div>'.format(max(0, min(100, attention - fatigue // 3))), unsafe_allow_html=True)
with si2:
    st.markdown('<div class="card"><div class="title">Risk level</div><div style="margin-top:14px"><span class="risk-chip">{}</span></div><div class="note">Based on current fatigue index</div></div>'.format("HIGH" if fatigue >= 65 else "MEDIUM" if fatigue >= 35 else "LOW"), unsafe_allow_html=True)
with si3:
    st.markdown('<div class="card"><div class="title">Recommended action</div><div style="margin-top:14px;font-size:12px;color:#d7e4f3">{}</div></div>'.format("Take a break" if fatigue >= 65 else "Stay attentive"), unsafe_allow_html=True)


st.write("")
a, b = st.columns([1.2, 1], gap="large")

with a:
    st.markdown('<div class="card"><div class="head"><div><div class="title">Fatigue trend</div><div class="caption">Recent simulated readings</div></div></div>', unsafe_allow_html=True)
    history = list(st.session_state.fatigue_history)
    max_value = max(max(history), 1)
    bars = ""
    for value in history[-24:]:
        height = max(4, int((value / max_value) * 150))
        bars += f'<div title="{value}%" style="height:{height}px;flex:1;background:linear-gradient(180deg,#51d7ff,#536dfe);border-radius:4px 4px 0 0;margin:0 2px;"></div>'
    st.markdown(f'<div style="height:175px;display:flex;align-items:end;padding:12px;background:#0a1320;border:1px solid #22364e;border-radius:12px;">{bars}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with b:
    st.markdown('<div class="card"><div class="head"><div><div class="title">Activity log</div><div class="caption">Recent system events</div></div></div>', unsafe_allow_html=True)
    for event_time, event_name, event_type in list(st.session_state.events)[:6]:
        st.markdown(f'<div class="event"><small>{event_time} · {event_type}</small><p>{event_name}</p></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

if page == "Analytics":
    st.subheader("Session analytics")
    st.metric("Average fatigue", f"{sum(st.session_state.fatigue_history) / len(st.session_state.fatigue_history):.1f}%")
    st.metric("Peak fatigue", f"{max(st.session_state.fatigue_history)}%")
    st.metric("Total alerts", st.session_state.alerts)
    st.download_button(
        "Export session log",
        data="\n".join(f"{t} | {typ} | {name}" for t, name, typ in st.session_state.events),
        file_name="driver_session_log.txt",
        mime="text/plain",
    )

if page == "Settings":
    st.subheader("Prototype settings")
    st.checkbox("Enable sound alert simulation", value=True)
    st.checkbox("Enable dashboard animations", value=True)
    st.checkbox("Enable automatic emergency escalation", value=False)
    st.slider("Fatigue alert threshold", 40, 90, 65)
    st.slider("Attention warning threshold", 40, 95, 70)
    st.info("These settings currently control the prototype interface. Connect them to a trained vision model for production behavior.")
    st.checkbox("Store session events", value=True)
    st.info("These controls are UI prototypes. They do not change a real detection model.")

st.markdown('<div style="text-align:center;color:#415873;font-size:9px;padding:25px">DRIVESENTINEL AI · DRIVER FATIGUE INTELLIGENCE · PROTOTYPE</div>', unsafe_allow_html=True)