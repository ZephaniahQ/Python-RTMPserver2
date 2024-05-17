from flask import Flask, Response, render_template
import cv2
import time
import webbrowser

app = Flask(__name__)

video_path_rtmp = '.flv'
url = "http://127.0.0.1:80"
urlRTSP = "rtsp://192.168.10.11:1935/h264_ulaw.sdp"


cap_rtmp = cv2.VideoCapture(video_path_rtmp)
cap_rtsp = cv2.VideoCapture(urlRTSP)

def generate_frames_rtmp():
    while True:
        ret, frame = cap_rtmp.read()
        if not ret:
            break

        # Convert the frame to JPEG format
        ret, jpeg = cv2.imencode('.jpg', frame)
        frame = jpeg.tobytes()

        #time.sleep(.01)
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        
def generate_frames_rtsp():
    while True:
        ret, frame = cap_rtsp.read()
        if not ret:
            break # Exit the loop if no more frames are available

        # Convert the frame to JPEG format
        ret, jpeg = cv2.imencode('.jpg', frame)
        frame = jpeg.tobytes()

        # Yield the frame as part of the response
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')



webbrowser.open_new(url)

@app.route('/video_rtmp')
def video_rtmp():
    return Response(generate_frames_rtmp(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/video_rtsp')
def video_rtsp():
    return Response(generate_frames_rtsp(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/')
def index():
    return render_template('index.html')
if __name__ == '__main__':
    app.run(port=80)
