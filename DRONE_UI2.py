import os
import sys
import math
import threading
import datetime
from datetime import datetime, timedelta
from pathlib import Path
from collections import deque

import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

import smtplib
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from twilio.rest import Client
import pywhatkit

# Optional Windows Beep
try:
    import winsound
except:
    winsound = None

# ================= ENV VARIABLES =================
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASS = os.getenv("SMTP_PASS")

TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_FROM = os.getenv("TWILIO_FROM")
TWILIO_TO = os.getenv("TWILIO_TO")

# ================= YOLO PATH SETUP =================
FILE = Path(__file__).resolve()
ROOT = FILE.parents[0]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))
ROOT = Path(os.path.relpath(ROOT, Path.cwd()))

from utils.plots import *
from models.common import DetectMultiBackend
from utils.dataloaders import IMG_FORMATS, VID_FORMATS, LoadImages, LoadScreenshots, LoadStreams
from utils.general import (Profile, cv2, check_file,
                           non_max_suppression, scale_boxes, check_imshow)
from utils.plots import Annotator, colors
from utils.torch_utils import select_device

alarm_list = deque([])


class GUI:
    whatsapp_started = 0
    whatstime = datetime.now()
    user_email = ""
    grp_id = ""

    # ================= SOUND =================
    def snd(self):
        if winsound:
            winsound.Beep(2000, 1000)
        else:
            print("Beep not supported on this OS")

    # ================= EMAIL =================
    def mail(self, image, to_email):
        if not SMTP_USER or not SMTP_PASS:
            print("SMTP credentials not set")
            return

        smtp_server = 'smtp.gmail.com'
        smtp_port = 587

        message = MIMEMultipart()
        message['From'] = SMTP_USER
        message['To'] = to_email
        message['Subject'] = 'DRONE SPOTTED'

        body = "Drone detected by AI Drone Detection System."
        message.attach(MIMEText(body, 'plain'))

        try:
            with open(image, 'rb') as attachment:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment.read())
                encoders.encode_base64(part)
                part.add_header(
                    'Content-Disposition',
                    f'attachment; filename={os.path.basename(image)}',
                )
                message.attach(part)
        except FileNotFoundError:
            print("Attachment not found")

        try:
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(SMTP_USER, SMTP_PASS)
                server.send_message(message)
            print("Email sent successfully")
        except Exception as e:
            print("Email failed:", e)

    # ================= SMS =================
    def smssend(self):
        if not TWILIO_ACCOUNT_SID or not TWILIO_AUTH_TOKEN:
            print("Twilio credentials not set")
            return

        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        client.messages.create(
            body="Drone detected by AI system",
            from_=TWILIO_FROM,
            to=TWILIO_TO
        )
        print("SMS sent successfully")

    # ================= WHATSAPP =================
    def Whatsapp(self, image, grp_id):
        now = datetime.now()
        send_time = now + timedelta(minutes=1)

        pywhatkit.sendwhats_image(
            grp_id,
            image,
            "Drone Spotted at " + now.strftime('%H:%M:%S'),
            send_time.hour,
            send_time.minute
        )
        print("WhatsApp sent successfully")

    # ================= MAIN DETECTION =================
    def DRONEDET(self,
                 weights="drone2.pt",
                 source=0,
                 imgsz=(512, 512),
                 conf_thres=0.40,
                 iou_thres=0.45,
                 device=0):

        source = str(source)
        self.user_email = self.text_field1.get() or "example@gmail.com"
        self.grp_id = self.text_field2.get() or "GrNyQnFxBpzB8pJb2hbOQ3"

        device = select_device(device)
        model = DetectMultiBackend(weights, device=device)
        stride, names, pt = model.stride, model.names, model.pt

        webcam = source.isnumeric()
        if webcam:
            dataset = LoadStreams(source, img_size=imgsz, stride=stride, auto=pt)
        else:
            dataset = LoadImages(source, img_size=imgsz, stride=stride, auto=pt)

        model.warmup(imgsz=(1, 3, *imgsz))

        cv2.namedWindow("DRONE DETECTION", cv2.WINDOW_NORMAL)

        for path, im, im0s, vid_cap, s in dataset:
            im = torch.from_numpy(im).to(model.device)
            im = im.float() / 255.0
            if len(im.shape) == 3:
                im = im[None]

            pred = model(im)
            pred = non_max_suppression(pred, conf_thres, iou_thres)

            for i, det in enumerate(pred):
                im0 = im0s.copy()
                annotator = Annotator(im0)

                if len(det):
                    det[:, :4] = scale_boxes(im.shape[2:], det[:, :4], im0.shape).round()

                    for *xyxy, conf, cls in reversed(det):
                        c = int(cls)
                        label = f'{names[c]} {conf:.2f}'
                        annotator.box_label(xyxy, label, color=colors(c, True))

                        if names[c] == "drone":
                            alarm_list.append(1)

                            if len(alarm_list) >= 30:
                                cv2.imwrite("DetDrone.jpg", im0)

                                threading.Thread(target=self.snd).start()
                                threading.Thread(target=self.mail,
                                                 args=("DetDrone.jpg", self.user_email)).start()

                                if self.whatsapp_started == 0:
                                    threading.Thread(target=self.Whatsapp,
                                                     args=("DetDrone.jpg", self.grp_id)).start()
                                    self.whatsapp_started = 1
                                    self.whatstime = datetime.now()

                                alarm_list.clear()

                im0 = annotator.result()
                cv2.imshow("DRONE DETECTION", im0)

                if cv2.waitKey(1) == ord('q'):
                    return

    # ================= GUI =================
    def run(self):
        app = tk.Tk()
        app.geometry("1920x1080")
        app.title("DRONE DETECTION SYSTEM WITH WHATSAPP")

        img = Image.open("bg.png")
        self.imgtk = ImageTk.PhotoImage(img)
        panel = tk.Label(app, image=self.imgtk)
        panel.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(app, text="DRONE DETECTION ALERT SYSTEM",
                 font=("Arial Black", 30, "bold")).place(relx=0.5, rely=0.05, anchor="n")

        tk.Label(app, text="ENTER EMAIL ID FOR ALERT",
                 font=("Arial Black", 18, "bold")).place(relx=0.75, rely=0.4, anchor="n")

        self.text_field1 = tk.Entry(app, font=("Arial", 18))
        self.text_field1.place(relx=0.75, rely=0.45, width=300, height=35, anchor="n")

        tk.Label(app, text="ENTER WHATSAPP GP ID",
                 font=("Arial Black", 18, "bold")).place(relx=0.75, rely=0.55, anchor="n")

        self.text_field2 = tk.Entry(app, font=("Arial", 18))
        self.text_field2.place(relx=0.75, rely=0.6, width=300, height=35, anchor="n")

        ttk.Button(app, text="ENABLE CAMERA FEED",
                   command=lambda: self.DRONEDET()).place(relx=0.5, rely=0.85,
                                                         anchor="center", width=300, height=60)

        ttk.Button(app, text="QUIT",
                   command=app.destroy).place(relx=0.2, rely=0.85,
                                              anchor="center", width=200, height=60)

        app.mainloop()


if __name__ == "__main__":
    gui = GUI()
    gui.run()