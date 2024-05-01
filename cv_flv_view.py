import cv2
import time

# Path to your FLV file
video_path = '.flv'
time.sleep(3)

# Open the video file
cap = cv2.VideoCapture(video_path)

# Check if the video file was opened successfully
if not cap.isOpened():
    print("Error opening video file")
else:
    # Read and display the video frames
    while True:
        ret, frame = cap.read()
        if not ret:
            break # Exit the loop if no more frames are available

        # Display the frame
        cv2.imshow('Frame', frame)

        # Wait for 1 millisecond before moving on to the next frame
        # You can adjust this value to control the playback speed
        if cv2.waitKey(20) & 0xFF == ord('q'):
            break # Exit the loop if 'q' is pressed

    # Release the video capture object and close the display window
    cap.release()
    cv2.destroyAllWindows()
