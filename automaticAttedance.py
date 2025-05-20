import tkinter as tk
from tkinter import *
import os, cv2
import shutil
import csv
import numpy as np
from PIL import ImageTk, Image
import pandas as pd
import datetime
import time
import tkinter.ttk as tkk
import tkinter.font as font

haarcasecade_path = "haarcascade_frontalface_default.xml"
trainimagelabel_path = "./TrainingImageLabel/Trainner.yml"
trainimage_path = "TrainingImage"
studentdetail_path = "StudentDetails/studentdetails.csv"
attendance_path = "Attendance"

def subjectChoose(text_to_speech):
    def FillAttendance():
        sub = tx.get()
        now = time.time()
        future = now + 20
        if sub == "":
            text_to_speech("Please enter the subject name!!!")
            return

        try:
            recognizer = cv2.face.LBPHFaceRecognizer_create()
            try:
                recognizer.read(trainimagelabel_path)
            except:
                e = "Model not found, please train model"
                Notifica.configure(text=e, bg="black", fg="yellow", width=33, font=("times", 15, "bold"))
                Notifica.place(x=20, y=250)
                text_to_speech(e)
                return

            facecasCade = cv2.CascadeClassifier(haarcasecade_path)
            df = pd.read_csv(studentdetail_path)
            
            cam = cv2.VideoCapture(0)
            if not cam.isOpened():
                print("Cannot open camera")
                return
            font = cv2.FONT_HERSHEY_SIMPLEX
            col_names = ["Enrollment", "Name"]
            attendance = pd.DataFrame(columns=col_names)

            live_face_frames = {}
            required_live_frames = 40
            last_invalid_speech_time = 0
            speech_cooldown = 5

            date = datetime.datetime.fromtimestamp(now).strftime("%Y-%m-%d")
            timeStamp = datetime.datetime.fromtimestamp(now).strftime("%H:%M:%S")

            while True:
                rem, im = cam.read()
                if not rem or im is None:
                    print("Failed to grab frame from camera")
                    break

                gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
                faces = facecasCade.detectMultiScale(gray, 1.2, 5)

                for (x, y, w, h) in faces:
                    if len(faces) == 1:
                        (x, y, w, h) = faces[0]
                        Id, error = recognizer.predict(gray[y:y+h, x:x+w])
                        face_crop = gray[y:y+h, x:x+w]
                        motion_score = cv2.Laplacian(face_crop, cv2.CV_64F).var()

                        if motion_score > 5 and error < 50:
                            live_face_frames[Id] = live_face_frames.get(Id, 0) + 1
                            if live_face_frames[Id] >= required_live_frames:
                                aa = df.loc[df["Enrollment"] == Id]["Name"].values[0]

                                # Check for duplicate attendance
                                path = os.path.join(attendance_path, sub)
                                if os.path.exists(path):
                                    for file in os.listdir(path):
                                        if file.endswith(".csv") and date in file:
                                            data = pd.read_csv(os.path.join(path, file))
                                            if Id in data["Enrollment"].values:
                                                continue  # Already marked, skip
                                attendance.loc[len(attendance)] = [Id, aa]
                                # cv2.rectangle(im, (x, y), (x + w, y + h), (0, 260, 0), 4)
                                # cv2.putText(im, f"{Id}-{aa}", (x + h, y), font, 1, (255, 255, 0), 4)
                                cv2.rectangle(im, (x, y), (x + w, y + h), (0, 255, 0), 4)
                                cv2.putText(im, f"{Id}-{aa}", (x, y - 10), font, 1, (255, 255, 0), 2)

                                # Show the frame with rectangle and text for 3 seconds
                                for _ in range(60):  # 60 frames ~ 2 seconds if running at ~30 FPS
                                    ret, frame = cam.read()
                                    if not ret:
                                        break
                                    frame = cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 4)
                                    frame = cv2.putText(frame, f"{Id}-{aa}", (x, y - 10), font, 1, (255, 255, 0), 2)
                                    cv2.imshow("Filling Attendance...", frame)
                                    if cv2.waitKey(30) & 0xFF == 27:
                                        break

                                cam.release()
                                cv2.destroyAllWindows()
                                break
                        else:
                            cv2.rectangle(im, (x, y), (x + w, y + h), (0, 0, 255), 4)
                            cv2.putText(im, "Unknown", (x, y - 10), font, 1, (0, 0, 255), 2)
                    elif len(faces) >= 2:
                        text_to_speech("Multiple faces detected. Only one allowed.")
                        cam.release()
                        cv2.destroyAllWindows()
                        break

                        # current_time = time.time()
                        # if current_time - last_invalid_speech_time > speech_cooldown:
                        #     text_to_speech("Multiple faces detected. Only one allowed.")
                        #     last_invalid_speech_time = current_time
                
                
                
                
                if time.time() > future:
                    break
                attendance = attendance.drop_duplicates(["Enrollment"], keep="first")
                cv2.imshow("Filling Attendance...", im)
                if cv2.waitKey(30) & 0xFF == 27:
                    break

            cam.release()
            cv2.destroyAllWindows()

            if attendance.empty:
                m = "No valid faces detected!"
                Notifica.configure(text=m, bg="black", fg="red", width=33, font=("times", 15, "bold"))
                Notifica.place(x=20, y=250)
                text_to_speech(m)
                return

            ts = time.time()
            date = datetime.datetime.fromtimestamp(ts).strftime("%Y-%m-%d")
            timeStamp = datetime.datetime.fromtimestamp(ts).strftime("%H:%M:%S")
            Hour, Minute, Second = timeStamp.split(":")

            import glob

            path = os.path.join(attendance_path, sub)
            if not os.path.exists(path):
                os.makedirs(path)

            # Look for today's attendance file for this subject
            pattern = os.path.join(path, f"{sub}_{date}_*.csv")
            existing_files = glob.glob(pattern)

            attendance = attendance.drop_duplicates(["Enrollment"], keep="first")

            if existing_files:
                fileName = existing_files[0]
                existing_data = pd.read_csv(fileName)

    # Check if all students are already marked
                all_already_marked = attendance["Enrollment"].isin(existing_data["Enrollment"]).all()

                if all_already_marked:
                    m = "Attendance already taken"
                    Notifica.configure(text=m, bg="black", fg="yellow", width=33, font=("times", 15, "bold"))
                    Notifica.place(x=20, y=250)
                    text_to_speech(m)
                    return
                else:
        # Add only students not yet marked
                    new_data = attendance[~attendance["Enrollment"].isin(existing_data["Enrollment"])]
                    updated_data = pd.concat([existing_data, new_data], ignore_index=True)
                    updated_data.drop_duplicates(subset=["Enrollment"], keep="first", inplace=True)
                    updated_data.to_csv(fileName, index=False)

                    m = "Attendance updated successfully for " + sub
            else:
                fileName = os.path.join(path, f"{sub}_{date}_{Hour}-{Minute}-{Second}.csv")
                attendance.to_csv(fileName, index=False)

                m = "Attendance filled successfully for " + sub

            Notifica.configure(text=m, bg="black", fg="yellow", width=33, font=("times", 15, "bold"))
            Notifica.place(x=20, y=250)
            text_to_speech(m)
            ##################################
            import tkinter
            root = tkinter.Tk()
            root.title("Attendance of " + sub)
            root.configure(background="black")
            with open(fileName, newline="") as file:
                reader = csv.reader(file)
                r = 0
                for col in reader:
                    c = 0
                    for row in col:
                        label = tkinter.Label(root, width=10, height=1, fg="yellow", font=("times", 15, " bold "), bg="black", text=row, relief=tkinter.RIDGE)
                        label.grid(row=r, column=c)
                        c += 1
                    r += 1
            root.mainloop()

        except Exception as e:
            print(e)
            # text_to_speech(f"Something Went Wrong: {e}")
            cv2.destroyAllWindows()

    subject = Tk()
    subject.title("Subject...")
    subject.geometry("580x320")
    subject.resizable(0, 0)
    subject.configure(background="black")

    titl = tk.Label(subject, bg="black", relief=RIDGE, bd=10, font=("arial", 30))
    titl.pack(fill=X)
    titl = tk.Label(subject, text="Enter the Subject Name", bg="black", fg="green", font=("arial", 25))
    titl.place(x=160, y=12)

    Notifica = tk.Label(subject, text="Attendance filled Successfully", bg="yellow", fg="black", width=33, height=2, font=("times", 15, "bold"))

    def Attf():
        sub = tx.get()
        if sub == "":
            text_to_speech("Please enter the subject name!!!")
        else:
            folder_path = os.path.join("Attendance", sub)
            if os.path.exists(folder_path):
                os.startfile(folder_path)
            else:
                t = "No attendance for this subject"
                text_to_speech(t)
                Notifica.configure(text=t, bg="black", fg="yellow", width=33, font=("times", 15, "bold"))
                Notifica.place(x=20, y=250)

    attf = tk.Button(subject, text="Check Sheets", command=Attf, bd=7, font=("times new roman", 15), bg="black", fg="yellow", height=2, width=10, relief=RIDGE)
    attf.place(x=360, y=170)

    sub = tk.Label(subject, text="Enter Subject", width=10, height=2, bg="black", fg="yellow", bd=5, relief=RIDGE, font=("times new roman", 15))
    sub.place(x=50, y=100)

    tx = tk.Entry(subject, width=15, bd=5, bg="black", fg="yellow", relief=RIDGE, font=("times", 30, "bold"))
    tx.place(x=190, y=100)

    fill_a = tk.Button(subject, text="Fill Attendance", command=FillAttendance, bd=7, font=("times new roman", 15), bg="black", fg="yellow", height=2, width=12, relief=RIDGE)
    fill_a.place(x=195, y=170)

    subject.mainloop()