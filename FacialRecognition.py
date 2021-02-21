import asyncio
from bleak import BleakClient
import face_recognition
import cv2
import numpy as np
global process_this_frame 
process_this_frame = True
video_capture = cv2.VideoCapture(0)

obama_image = face_recognition.load_image_file("obama.jpg")
obama_face_encoding = face_recognition.face_encodings(obama_image)[0]

biden_image = face_recognition.load_image_file("biden.jpg")
biden_face_encoding = face_recognition.face_encodings(biden_image)[0]

max_image = face_recognition.load_image_file("max.jpg")
max_face_encoding = face_recognition.face_encodings(max_image)[0]

known_face_encodings = [
    obama_face_encoding,
    biden_face_encoding,
    max_face_encoding
]
known_face_names = [
    "Barack Obama",
    "Joe Biden",
    "Max"
]

# Initialize some variables
face_locations = []
face_encodings = []
face_names = []


address = '88:25:83:F0:2A:8D'
CHARACTERISTIC_UUID = '0000FFE1-0000-1000-8000-00805F9B34FB'
global read 
global video_controller
video_controller = 1
read = 'a'

def notification_handler( sender, data):
    global read
    data = data.decode('utf-8')
    print(data)
    if(data == 'b'):
        read = 'b'
    if(data == 'c'):
        read = 'c'

       

async def run(address):
    global read
    global process_this_frame
    client = BleakClient(address)
    try:
        await client.connect()

        while(read == 'a'):
            await client.start_notify(CHARACTERISTIC_UUID, notification_handler)
            await asyncio.sleep(1)
            await client.stop_notify(CHARACTERISTIC_UUID)

        print('starting video')                    
        global video_controller
        while (video_controller != 0):
            ret, frame = video_capture.read()
            if (ret):
                print('starting video2') 
                small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
                rgb_small_frame = small_frame[:, :, ::-1]

                if process_this_frame:
                # Find all the faces and face encodings in the current frame of video
                    face_locations = face_recognition.face_locations(rgb_small_frame)
                    face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

                    face_names = []
                    for face_encoding in face_encodings:
                        # See if the face is a match for the known face(s)
                        matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
                        name = "Unknown"

                        # # If a match was found in known_face_encodings, just use the first one.
                        # if True in matches:
                        #     first_match_index = matches.index(True)
                        #     name = known_face_names[first_match_index]

                        # Or instead, use the known face with the smallest distance to the new face
                        face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
                        best_match_index = np.argmin(face_distances)
                        if matches[best_match_index]:
                            name = known_face_names[best_match_index]

                        face_names.append(name)

                process_this_frame = not process_this_frame

                # Display the results
                for (top, right, bottom, left), name in zip(face_locations, face_names):
                    # Scale back up face locations since the frame we detected in was scaled to 1/4 size
                    top *= 4
                    right *= 4
                    bottom *= 4
                    left *= 4

                    # Draw a box around the face
                    cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

                    # Draw a label with a name below the face
                    cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
                    font = cv2.FONT_HERSHEY_DUPLEX
                    cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

                # Display the resulting image
                cv2.imshow('Video', frame)
                for (top, right, bottom, left), name in zip(face_locations, face_names):
                    if name == "Unknown":
                        print('find unknown!!')
                        cv2.waitKey(8000)
                        video_controller = 0;
                    
                        
                # Hit 'q' on the keyboard to quit!
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
        #face_recog()
        #capture unknown then send signal
    # Release handle to the webcam
        video_capture.release()
        cv2.destroyAllWindows() 
        await client.write_gatt_char(CHARACTERISTIC_UUID, b'a')  

        while(read == 'b'):
            await client.start_notify(CHARACTERISTIC_UUID, notification_handler)
            await asyncio.sleep(1)
            await client.stop_notify(CHARACTERISTIC_UUID)
        
        if(read == 'c'):
            print('we are going to reboot this computer')    
            import os
            os.system('shutdown /p /f')
            
              

    except Exception as e:
        print(e)
    finally:
        await client.disconnect()

loop = asyncio.get_event_loop()
loop.run_until_complete(run(address))
