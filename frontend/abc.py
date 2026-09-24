import streamlit as st
import random
import time
from datetime import datetime
from collections import deque

st.set_page_config(page_title="DriveSentinel AI", page_icon="DS", layout="wide")


try:
    import av
    import cv2
    import numpy as np
    from streamlit_webrtc import webrtc_streamer, WebRtcMode
    CAMERA_READY = True
except Exception:
    CAMERA_READY = False
    


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
* {font-family: Arial, Helvetica, sans-serif;}
.stApp {background:#f5f7fa;color:#202124;}
[data-testid="stSidebar"] {background:#ffffff;border-right:1px solid #d9dee7;}
[data-testid="stSidebar"] * {color:#263238;}

.brand {padding-bottom:20px;border-bottom:1px solid #e1e5ea;margin-bottom:20px;}
.brand b {font-size:22px;font-weight:700;letter-spacing:0;}
.brand b span {color:#1769aa;}
.brand small {display:block;color:#6b7280;font-size:9px;letter-spacing:1.5px;margin-top:6px;}
.eyebrow {color:#1769aa;font-size:10px;font-weight:700;letter-spacing:1.5px;}
.sub {color:#667085;font-size:12px;margin-bottom:24px;}
.card,.kpi {background:#ffffff;border:1px solid #dfe3e8;border-radius:10px;padding:18px;box-shadow:0 1px 3px rgba(0,0,0,.04);}
.kpi {min-height:108px;}
.label {font-size:9px;letter-spacing:1px;color:#667085;font-weight:700;}
.value {font-size:28px;font-weight:700;margin-top:12px;color:#1f2937;}
.note {font-size:10px;color:#7a8491;margin-top:5px;}
.head {display:flex;justify-content:space-between;align-items:center;margin-bottom:15px;}
.title {font-size:14px;font-weight:600;color:#1f2937;}
.caption {font-size:10px;color:#7a8491;margin-top:4px;}
.pill {border:1px solid #b9d5ee;background:#eef6fd;color:#1769aa;border-radius:14px;padding:6px 10px;font-size:9px;font-weight:700;}
.status {padding:16px;border-radius:9px;margin-bottom:18px;background:#f4f8fc;border:1px solid #c9dff2;}
.status strong {display:block;color:#1769aa;font-size:24px;margin-top:6px;}
.metric-line {display:flex;justify-content:space-between;padding:10px 0;border-bottom:1px solid #e6e9ed;font-size:11px;}
.metric-line span:first-child {color:#667085;font-size:10px;}
.metric-line span:last-child {color:#273444;font-weight:600;}
.event {padding:9px 0;border-bottom:1px solid #e6e9ed;}
.event small {color:#7a8491;font-size:9px;}
.event p {margin:4px 0 0;color:#344054;font-size:11px;}
div.stButton>button {background:#ffffff;border:1px solid #b8c2cc;border-radius:7px;color:#243447;font-size:11px;}
div.stButton>button:hover {border-color:#1769aa;color:#1769aa;}
.camera-note {padding:14px;border:1px dashed #aeb8c2;border-radius:9px;color:#667085;font-size:12px;text-align:center;background:#fafbfc;}
.risk-chip {display:inline-block;padding:5px 9px;border-radius:14px;background:#fff7e6;color:#9a6700;border:1px solid #e8c878;font-size:9px;font-weight:700;}
.feature-box {background:#ffffff;border:1px solid #dfe3e8;border-radius:9px;padding:14px;min-height:88px;}
.feature-box b {font-size:21px;color:#1f2937;}
.feature-box span {display:block;color:#7a8491;font-size:10px;margin-top:5px;}
.alert-box {background:#fff1f2;border:1px solid #e5a4aa;color:#a33a43;border-radius:9px;padding:14px;font-size:12px;}
</style>
""", unsafe_allow_html=True)


with st.sidebar:
    st.markdown('<div class="brand"><b>◈ DRIVESENTINEL<span>AI</span></b><small>DRIVER FATIGUE MONITORING</small></div>', unsafe_allow_html=True)
    page = st.radio("Workspace", ["Dashboard", "Live Camera", "Analytics", "Settings"], label_visibility="collapsed")
    st.markdown("---")
    st.markdown("#### Session profile")
    driver = st.text_input("Driver name", "Alex Morgan")
    vehicle = st.text_input("Vehicle ID", "DS-2048")
    sensitivity = st.select_slider("Detection sensitivity", ["Low", "Balanced", "High"], value="Balanced")
    st.session_state.monitoring = st.toggle("Monitoring active", value=st.session_state.monitoring)
    st.markdown("---")
    st.caption("Vision engine: Ready" if CAMERA_READY else "Vision engine: Install camera packages")
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
st.markdown('<div class="sub">Live camera monitoring, fatigue indicators, alerts and session information.</div>', unsafe_allow_html=True)

q1, q2, q3, q4 = st.columns(4)
quick = [("BLINK RATE", f"{blink}/min", "Eye activity"), ("YAWNS", str(yawns), "Detected events"), ("CONFIDENCE", f"{min(attention + 1, 99)}%", "Vision estimate"), ("SESSION", "ACTIVE" if st.session_state.monitoring else "PAUSED", "Monitoring state")]
for col, (name, value, desc) in zip([q1, q2, q3, q4], quick):
    with col:
        st.markdown(f'<div class="feature-box"><div class="label">{name}</div><b>{value}</b><span>{desc}</span></div>', unsafe_allow_html=True)

if st.button("Refresh sensor simulation"):
    st.rerun()

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
        if CAMERA_READY:
            rtc_config = {"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]}

            class VideoProcessor:
                def recv(self, frame):
                    image = frame.to_ndarray(format="bgr24")
                    h, w = image.shape[:2]

                    # Simple camera overlay
                    cv2.rectangle(image, (15, 15), (w - 15, h - 15), (255, 255, 255), 1)
                    cv2.putText(image, "Driver Camera", (28, 45),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 255, 255), 2)
                    cv2.putText(image, "Monitoring", (28, h - 25),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

                    return av.VideoFrame.from_ndarray(image, format="bgr24")

            try:
                webrtc_streamer(
                    key="driver-camera",
                    mode=WebRtcMode.SENDRECV,
                    rtc_configuration=rtc_config,
                    video_processor_factory=VideoProcessor,
                    media_stream_constraints={"video": True, "audio": False},
                    async_processing=True,
                )
            except Exception as camera_error:
                st.warning("Live camera could not start. The rest of the dashboard is still available.")
                st.code(str(camera_error), language="text")
                st.info("Try refreshing the browser and allowing camera permission.")
        else:
            st.markdown('<div class="camera-note">Live camera packages are not installed. Use the installation commands below, then restart the app.</div>', unsafe_allow_html=True)
            st.code("pip install streamlit-webrtc opencv-python av numpy", language="powershell")

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
        st.error("Simulated emergency alert triggered.")

    if st.session_state.emergency:
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
        bars += f'<div title="{value}%" style="height:{height}px;flex:1;background:#1769aa;border-radius:4px 4px 0 0;margin:0 2px;"></div>'
    st.markdown(f'<div style="height:175px;display:flex;align-items:end;padding:12px;background:#f8fafc;border:1px solid #dfe3e8;border-radius:12px;">{bars}</div>', unsafe_allow_html=True)
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

st.markdown('<div style="text-align:center;color:#415873;font-size:9px;padding:25px">DRIVESENTINEL AI · DRIVER FATIGUE MONITORING · PROTOTYPE</div>', unsafe_allow_html=True)