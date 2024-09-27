import socket
import face_recognition
import os
import sys
import cv2
import numpy as np
import math
import smtplib
import imghdr
from email.message import EmailMessage

# Set up the client socket connection
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(('192.168.43.229', 12345))  # Replace with Raspberry Pi IP address

def face_confidence(face_distance, face_match_threshold=0.6):
    range = (1.0 - face_match_threshold)
    linear_val = (1.0 - face_distance) / (range * 2.0)
    if face_distance > face_match_threshold:
        return str(round(linear_val * 100, 2)) + '%'
    else:
        value = (linear_val + ((1.0 - linear_val) * math.pow((linear_val - 0.5) * 2, 0.2))) * 100
        return str(round(value, 2)) + '%'

class FaceRecognition:
    face_location = []
    face_encoding = []
    face_names = []   # this three from database
    known_face_encodings = []
    known_face_names = []
    process_current_frame = True

    def __init__(self):
        self.encode_faces()
    
    def encode_faces(self):
        for image in os.listdir('faces'):
            face_image = face_recognition.load_image_file(f'faces/{image}')
            face_encoding = face_recognition.face_encodings(face_image)[0]

            self.known_face_encodings.append(face_encoding)
            self.known_face_names.append(image)
        print(self.known_face_names)
        
    def run_recognition(self):
        video_capture = cv2.VideoCapture(0)

        if not video_capture.isOpened():
            sys.exit('Video source not found. Check permissions.')

        while True:
            print("waiting for bell input")
            # Receive data from the server
            data = client_socket.recv(1024)
            if data == b'a':
                print('bell is rang')
                video_capture = cv2.VideoCapture(0)
                if not video_capture.isOpened():
                    sys.exit('Video source not found. Check permissions.')

                detected = False
                while not detected:
                    ret, frame = video_capture.read()
                    if not ret:
                        print("Error: Failed to capture frame from video source")
                        continue

                    # Perform frame processing
                    small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
                    self.face_location = face_recognition.face_locations(small_frame)
                    self.face_encoding = face_recognition.face_encodings(small_frame, self.face_location)
                    self.face_names = []

                    for face_encoding in self.face_encoding:
                        matches = face_recognition.compare_faces(self.known_face_encodings, face_encoding)
                        name = 'unknown'
                        confidence = 'unknown'

                        face_distances = face_recognition.face_distance(self.known_face_encodings, face_encoding)
                        best_match_index = np.argmin(face_distances)

                        if matches[best_match_index]:
                            name = self.known_face_names[best_match_index]
                            confidence = face_confidence(face_distances[best_match_index])
                        self.face_names.append(f'{name}, {confidence}')

                        if name == "unknown":
                            client_socket.sendall(b'0')
                            print('unknown person found')
                            pir_data = client_socket.recv(1024)
                            if (pir_data == b'q'):
                                return_value, image = video_capture.read()
                                cv2.imwrite('intruder.png', image)
                                Sender_Email = "getayawkalwork@gmail.com"
                                Reciever_Email = "getayawkalgirma36908@gmail.com"
                                Password = "lmkc rzbn vauh sqmh"  # type your password here
                                newMessage = EmailMessage()
                                newMessage['Subject'] = "Alert Theft inside your home"
                                newMessage['From'] = Sender_Email
                                newMessage['To'] = Reciever_Email
                                newMessage.set_content('Let me know what you think. Image attached!')
                                with open('intruder.png', 'rb') as f:
                                    image_data = f.read()
                                    image_type = imghdr.what(f.name)
                                    image_name = f.name
                                newMessage.add_attachment(image_data, maintype='image', subtype=image_type,
                                                          filename=image_name)
                                with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
                                    smtp.login(Sender_Email, Password)
                                    smtp.send_message(newMessage)
                            elif (pir_data == b'p'):
                                print("Members present inside home no need to send image ")
                        elif name in self.known_face_names:
                            client_socket.sendall(b'1')
                            print('known person detected')
                            detected = True
                            break

                    # Display annotations on the frame
                    for (top, right, bottom, left), name in zip(self.face_location, self.face_names):
                        top *= 4
                        right *= 4
                        bottom *= 4
                        left *= 4

                        cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
                        cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), -1)
                        cv2.putText(frame, name, (left + 6, bottom - 6), cv2.FONT_HERSHEY_COMPLEX, 0.8, (255, 255, 255), 1)

                    # Display the frame
                    cv2.imshow('Face Recognition', frame)

                    # Check for 'q' key press to exit
                    if cv2.waitKey(1) == ord('q'):
                        break

                video_capture.release()
                cv2.destroyAllWindows()

if __name__ == '__main__':
    fr = FaceRecognition()
    fr.run_recognition()
    client_socket.close()
