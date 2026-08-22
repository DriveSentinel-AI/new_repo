# #import the necessary libraries
# import numpy as np
# import dlib
# import cv2
# from math import hypot


# cap = cv2.VideoCapture(0)

# detector = dlib.get_frontal_face_detector()
# predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")

# def mid(p1 ,p2):
#     return int((p1.x + p2.x)/2), int((p1.y + p2.y)/2)

# def eye_aspect_ratio(eye_landmark, face_roi_landmark):
#     left_point = (face_roi_landmark.part(eye_landmark[0]).x, face_roi_landmark.part(eye_landmark[0]).y)
#     right_point = (face_roi_landmark.part(eye_landmark[3]).x, face_roi_landmark.part(eye_landmark[3]).y)
#     center_top = mid(face_roi_landmark.part(eye_landmark[1]), face_roi_landmark.part(eye_landmark[2]))
#     center_bottom = mid(face_roi_landmark.part(eye_landmark[5]), face_roi_landmark.part(eye_landmark[4]))

#     hor_line_length = hypot((left_point[0] - right_point[0]), (left_point[1] - right_point[1]))
#     ver_line_length = hypot((center_top[0] - center_bottom[0]), (center_top[1] - center_bottom[1]))

#     ratio = hor_line_length / ver_line_length
#     return ratio

# def mouth_aspect_ratio(lips_landmark, face_roi_landmark):
#     left_point = (face_roi_landmark.part(lips_landmark[0]).x, face_roi_landmark.part(lips_landmark[0]).y)
#     right_point = (face_roi_landmark.part(lips_landmark[2]).x, face_roi_landmark.part(lips_landmark[2]).y)
#     center_top = (face_roi_landmark.part(lips_landmark[1]).x, face_roi_landmark.part(lips_landmark[1]).y)
#     center_bottom = (face_roi_landmark.part(lips_landmark[3]).x, face_roi_landmark.part(lips_landmark[3]).y)

#     hor_line_length = hypot((left_point[0] - right_point[0]), (left_point[1] - right_point[1]))
#     ver_line_length = hypot((center_top[0] - center_bottom[0]), (center_top[1] - center_bottom[1]))
#     if hor_line_length == 0:
#         return ver_line_length
#     ratio = ver_line_length / hor_line_length
#     return ratio

# count = 0
# font = cv2.FONT_HERSHEY_TRIPLEX
# while True:
#     _, img = cap.read()
#     img = cv2.flip(img,1)
#     gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

#     faces = detector(gray)
#     for face_roi in faces:

#         landmark_list = predictor(gray, face_roi)

#         left_eye_ratio = eye_aspect_ratio([36, 37, 38, 39, 40, 41], landmark_list)
#         right_eye_ratio = eye_aspect_ratio([42, 43, 44, 45, 46, 47], landmark_list)
#         eye_open_ratio = (left_eye_ratio + right_eye_ratio) / 2
#         cv2.putText(img, str(eye_open_ratio), (0, 13), font, 0.5, (100, 100, 100))
#         ###print(left_eye_ratio,right_eye_ratio,eye_open_ratio)

#         inner_lip_ratio = mouth_aspect_ratio([60,62,64,66], landmark_list)
#         outter_lip_ratio = mouth_aspect_ratio([48,51,54,57], landmark_list)
#         mouth_open_ratio = (inner_lip_ratio + outter_lip_ratio) / 2
#         ###print(inner_lip_ratio,outter_lip_ratio,mouth_open_ratio)
#         if mouth_open_ratio > 0.380 and eye_open_ratio > 4.0 or eye_open_ratio > 4.30:
#             count +=1
#         else:
#             count = 0
#         x,y = face_roi.left(), face_roi.top()
#         x1,y1 = face_roi.right(), face_roi.bottom()
#         if count > 10:
#             cv2.rectangle(img, (x,y), (x1,y1), (0, 0, 255), 2)
#             cv2.putText(img, "SLEEPY", (x, y-5),font, 0.7, (0, 0, 255), 2)
#         else:
#             cv2.rectangle(img, (x,y), (x1,y1), (0, 255, 0), 2)
#             cv2.putText(img, "AWAKE", (x, y-5),font, 0.7, (0, 255, 0), 2)

#     cv2.imshow("img", img)

#     key = cv2.waitKey(1)
#     if key == 27:
#         break

# cap.release()
# cv2.destroyAllWindows()

from flask import Flask, render_template, Response, jsonify
import cv2
import mediapipe as mp
from math import hypot
from playsound3 import playsound
import threading
import time


app = Flask(__name__)


# =========================================================
# MediaPipe Setup
# =========================================================

mp_face_mesh = mp.solutions.face_mesh
mp_drawing = mp.solutions.drawing_utils

face_mesh = mp_face_mesh.FaceMesh(
    max_num_faces=1,
    refine_landmarks=True,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)


# =========================================================
# Camera
# =========================================================

cap = cv2.VideoCapture(0)

font = cv2.FONT_HERSHEY_SIMPLEX

count = 0

alarm_playing = False

sleepy_status = False

alert_count = 0

eye_value = 0.0

mouth_value = 0.0


# =========================================================
# Eye Landmarks
# =========================================================

LEFT_EYE = [
    33,
    160,
    158,
    133,
    153,
    144
]

RIGHT_EYE = [
    362,
    385,
    387,
    263,
    373,
    380
]


# =========================================================
# Distance
# =========================================================

def distance(p1, p2):

    return hypot(
        p1.x - p2.x,
        p1.y - p2.y
    )


# =========================================================
# Eye Aspect Ratio
# =========================================================

def eye_aspect_ratio(landmarks, indices):

    p1 = landmarks[indices[0]]
    p2 = landmarks[indices[1]]
    p3 = landmarks[indices[2]]
    p4 = landmarks[indices[3]]
    p5 = landmarks[indices[4]]
    p6 = landmarks[indices[5]]

    horizontal = distance(p1, p4)

    vertical1 = distance(p2, p6)
    vertical2 = distance(p3, p5)

    if horizontal == 0:
        return 0

    ear = (vertical1 + vertical2) / (2.0 * horizontal)

    return ear


# =========================================================
# Mouth Aspect Ratio
# =========================================================

def mouth_aspect_ratio(landmarks):

    left = landmarks[78]
    right = landmarks[308]

    top = landmarks[13]
    bottom = landmarks[14]

    horizontal = distance(left, right)

    vertical = distance(top, bottom)

    if horizontal == 0:
        return 0

    return vertical / horizontal


# =========================================================
# Alarm
# =========================================================

def play_alarm():

    global alarm_playing

    try:

        playsound("alarm.mpeg")

    except Exception as e:

        print("Alarm error:", e)

    alarm_playing = False


# =========================================================
# Camera Processing
# =========================================================

def generate_frames():

    global count
    global alarm_playing
    global sleepy_status
    global alert_count
    global eye_value
    global mouth_value

    previous_sleepy = False

    while True:

        success, frame = cap.read()

        if not success:

            break

        frame = cv2.flip(frame, 1)

        rgb = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2RGB
        )

        results = face_mesh.process(rgb)

        sleepy_status = False

        if results.multi_face_landmarks:

            for face_landmarks in results.multi_face_landmarks:

                landmarks = face_landmarks.landmark

                # -----------------------------------------
                # Eye calculation
                # -----------------------------------------

                left_eye_ratio = eye_aspect_ratio(
                    landmarks,
                    LEFT_EYE
                )

                right_eye_ratio = eye_aspect_ratio(
                    landmarks,
                    RIGHT_EYE
                )

                eye_open_ratio = (
                    left_eye_ratio +
                    right_eye_ratio
                ) / 2

                eye_value = eye_open_ratio


                # -----------------------------------------
                # Mouth calculation
                # -----------------------------------------

                mouth_open_ratio = mouth_aspect_ratio(
                    landmarks
                )

                mouth_value = mouth_open_ratio


                # -----------------------------------------
                # Drowsiness detection
                # -----------------------------------------

                if eye_open_ratio < 0.20:

                    count += 1

                else:

                    count = 0


                # -----------------------------------------
                # Sleepy
                # -----------------------------------------

                if count > 10:

                    sleepy_status = True

                    # Count new sleepy event
                    if not previous_sleepy:

                        alert_count += 1

                    previous_sleepy = True


                    # Alarm
                    if not alarm_playing:

                        alarm_playing = True

                        threading.Thread(
                            target=play_alarm,
                            daemon=True
                        ).start()


                    # Red status
                    cv2.putText(
                        frame,
                        "SLEEPY",
                        (20, 50),
                        font,
                        1.2,
                        (0, 0, 255),
                        3
                    )

                    cv2.putText(
                        frame,
                        "WARNING!",
                        (20, 90),
                        font,
                        0.9,
                        (0, 0, 255),
                        3
                    )

                else:

                    previous_sleepy = False

                    cv2.putText(
                        frame,
                        "AWAKE",
                        (20, 50),
                        font,
                        1.2,
                        (0, 255, 0),
                        3
                    )


                # -----------------------------------------
                # Display values on camera
                # -----------------------------------------

                cv2.putText(
                    frame,
                    f"Eye: {eye_open_ratio:.2f}",
                    (20, 125),
                    font,
                    0.7,
                    (255, 255, 255),
                    2
                )

                cv2.putText(
                    frame,
                    f"Mouth: {mouth_open_ratio:.2f}",
                    (20, 155),
                    font,
                    0.7,
                    (255, 255, 255),
                    2
                )


                # -----------------------------------------
                # Face landmarks
                # -----------------------------------------

                mp_drawing.draw_landmarks(
                    frame,
                    face_landmarks,
                    mp_face_mesh.FACEMESH_TESSELATION,
                    landmark_drawing_spec=None,
                    connection_drawing_spec=mp_drawing.DrawingSpec(
                        color=(100, 100, 100),
                        thickness=1
                    )
                )


        else:

            cv2.putText(
                frame,
                "NO FACE DETECTED",
                (20, 50),
                font,
                0.9,
                (0, 255, 255),
                2
            )


        # -----------------------------------------
        # Encode frame
        # -----------------------------------------

        ret, buffer = cv2.imencode(
            ".jpg",
            frame
        )

        frame_bytes = buffer.tobytes()


        yield (
            b"--frame\r\n"
            b"Content-Type: image/jpeg\r\n\r\n" +
            frame_bytes +
            b"\r\n"
        )


# =========================================================
# Home Page
# =========================================================

@app.route("/")
def index():

    return render_template("index.html")


# =========================================================
# Video Feed
# =========================================================

@app.route("/video_feed")
def video_feed():

    return Response(
        generate_frames(),
        mimetype="multipart/x-mixed-replace; boundary=frame"
    )


# =========================================================
# Status API
# =========================================================

@app.route("/status")
def status():

    return jsonify({

        "sleepy": sleepy_status,

        "eye": round(eye_value, 2),

        "mouth": round(mouth_value, 2),

        "alerts": alert_count

    })


# =========================================================
# Start Flask
# =========================================================

if __name__ == "__main__":

    app.run(
        debug=False,
        host="127.0.0.1",
        port=5000,
        threaded=True
    )