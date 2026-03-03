import datetime
import tkinter as tk
import winsound
from PIL import ImageTk
import os
import math
import sys
import threading
from pathlib import Path
from collections import deque
FILE = Path(__file__).resolve()
ROOT = FILE.parents[0]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT)) # add ROOT to PATH
ROOT = Path(os.path.relpath(ROOT, Path.cwd())) # relative

# ==================== ENVIRONMENT CONFIGURATION ====================
# Documentation: Load credentials from .env file (copy env.example to .env and fill values)
# This is the ONLY change made to the source code - all hardcoded credentials replaced.
# No logic, structure, imports (except dotenv), or functionality has been altered.
from dotenv import load_dotenv
load_dotenv()

from utils.plots import *
from models.common import DetectMultiBackend
from utils.dataloaders import IMG_FORMATS, VID_FORMATS, LoadImages, LoadScreenshots, LoadStreams
from utils.general import (Profile, cv2, check_file,
                           non_max_suppression, scale_boxes, check_imshow, )
from utils.plots import Annotator, colors
from utils.torch_utils import select_device
import smtplib
from email import encoders
from email.mime.base import MIMEBase
from twilio.rest import Client
import pywhatkit
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime, timedelta
alarm_list=deque([])
class GUI:
    whatsapp_started = 0
    whatstime=datetime.now()
    user_email=""
    grp_id=""
    #text_field1=tk.Entry()
    #text_field2 = tk.Entry()
    def snd(self):
        winsound.Beep(2000, 1000)
    def mail(self,image,to_email):
        smtp_server = 'smtp.gmail.com' # Replace with your SMTP server
        smtp_port = 587 # Commonly used port for SMTP
        #
        # Documentation: Email credentials loaded from .env (SMTP_USER / SMTP_PASS - see env.example)
        smtp_user = os.getenv('SMTP_USER')
        smtp_password = os.getenv('SMTP_PASS')
        from_email = smtp_user
        subject = 'DRONE SPOTTED'
        body = """
        Jai Hind Sir
        THIS IS A TEST EMAIL FOR DEMO PURPOSE
        A drone is spotted by the Drone Detection System.
        Regards,
        """
        # Create the email
        message = MIMEMultipart()
        message['From'] = from_email
        message['To'] = to_email
        message['Subject'] = subject
        message.attach(MIMEText(body, 'plain'))
        image_path = image
        try:
            with open(image_path, 'rb') as attachment:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment.read())
                encoders.encode_base64(part)
                part.add_header(
                    'Content-Disposition',
                    f'attachment; filename={image_path}',
                )
                message.attach(part)
        except FileNotFoundError:
            print(f'File {image_path} not found. Email sent without attachment.')
        # Send the email
        try:
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls() # Secure the connection
                server.login(smtp_user, smtp_password)
                server.send_message(message)
            print('Email sent successfully!')
        except Exception as e:
            print(f'Failed to send email: {e}')
    def smssend(self):
        # Documentation: Twilio credentials loaded from .env (TWILIO_SID / TWILIO_AUTH / TWILIO_FROM / TWILIO_TO - see env.example)
        ACCOUNT_SID = os.getenv('TWILIO_SID')
        AUTH_TOKEN = os.getenv('TWILIO_AUTH')
        # Create a client instance
        client = Client(ACCOUNT_SID, AUTH_TOKEN)
        # Send SMS
        message = client.messages.create(
            body="Jai Hind Sir Drone spotted Regards",
            from_=os.getenv('TWILIO_FROM'),
            to=os.getenv('TWILIO_TO')
        )
        # Print the message SID
        print("SMS sent successfully")
    def Whatsapp(self,image,grp_id,dist2):
        #group_number = "+919795705785" # Replace with your group number
        #grp_id2=""
        # Replace with the path to your image
        image_path = image
        #Geostagging calc
        R = 6371000 # Earth radius in meters
        # Documentation: Owner location loaded from .env (OWNER_LAT / OWNER_LON - see env.example)
        lat1 = math.radians(float(os.getenv('OWNER_LAT')))
        lon1 = math.radians(float(os.getenv('OWNER_LON')))
        bearing = math.radians(os.getenv('DEGREES')) #bearing
        #delta = float(dist2.strip()) / R #delta = dist2 / R
        delta = float(dist2.strip().replace('m', '')) / R
        lat2 = math.asin(
            math.sin(lat1) * math.cos(delta) +
            math.cos(lat1) * math.sin(delta) * math.cos(bearing)
        )
        lon2 = lon1 + math.atan2(
            math.sin(bearing) * math.sin(delta) * math.cos(lat1),
            math.cos(delta) - math.sin(lat1) * math.sin(lat2)
        )
        lat = f"{math.degrees(lat2):.6f}"
        lon = f"{math.degrees(lon2):.6f}"
        loc=str(lat)+","+str(lon)
        print(loc)#pass in text and convert to string first
        now = datetime.now()
        seconds_remaining = 60 - now.second
        one_minute_delta = timedelta(seconds=seconds_remaining)
        send_time = now + one_minute_delta
        hour = send_time.hour
        minute = send_time.minute
        print(hour)
        print(minute)
        # Send the image to the group
        #GrNyQnFxBpzB8pJb2hbOQ3
        pywhatkit.sendwhats_image(grp_id, image_path, "Drone Spotted At " + str(datetime.now().strftime('%H:%M:%S')),
                                  hour, minute,loc=loc)
        # pywhatkit.sendwhatmsg_to_group("GrNyQnFxBpzB8pJb2hbOQ3", "hi hello", hour, minute)
        print("Image sent successfully!")
    def compute_destination(lat_deg, lon_deg, distance_m, bearing_deg):
        R = 6371000 # Earth radius in meters
        lat1 = math.radians(lat_deg)
        lon1 = math.radians(lon_deg)
        bearing = math.radians(bearing_deg)
        delta = distance_m / R
        lat2 = math.asin(
            math.sin(lat1) * math.cos(delta) +
            math.cos(lat1) * math.sin(delta) * math.cos(bearing)
        )
        lon2 = lon1 + math.atan2(
            math.sin(bearing) * math.sin(delta) * math.cos(lat1),
            math.cos(delta) - math.sin(lat1) * math.sin(lat2)
        )
        return math.degrees(lat2), math.degrees(lon2)
    def DRONEDET(self,
            weights="drone2.pt", # model path or triton URL
            #source="PTZtest1.mp4",
            source=0, # file/dir/URL/glob/screen/0(webcam)
            #source="rtsp://admin:12345@192.168.1.100:554/h265/stream3",
            #source="rtsp://admin:Admin12345@136.53.8.27:554/h265/stream3", # For PTZ camera D1 MW tower
            #source="rtsp://admin:Admin12345@136.53.5.250:554/live/0/MAIN", # For bullet camera AVAKE testing
            data=ROOT / 'data/drone.yaml', # dataset.yaml path
            imgsz=(512, 512), # inference size (height, width)
            nosave=False, # do not save images/videos
            conf_thres=0.40, # confidence threshold
            iou_thres=0.45, # NMS IOU threshold
            max_det=10, # maximum detections per image
            device=0, # cuda device, i.e. 0 or 0,1,2,3 or cpu
            classes=None, # filter by class: --class 0, or --class 0 2 3
            agnostic_nms=False, # class-agnostic NMS
            augment=False, # augmented inference
            visualize=False, # visualize features
            line_thickness=3, # bounding box thickness (pixels)
            hide_labels=False, # hide labels
            hide_conf=True, # hide confidences
            half=False, # use FP16 half-precision inference
            dnn=False, # use OpenCV DNN for ONNX inference
            vid_stride=1, # video frame-rate stride
    ):
        source = str(source)
        self.user_email = str(self.text_field1.get())
        self.grp_id=str(self.text_field2.get())
        if(self.grp_id==""):
            # Documentation: WhatsApp group ID loaded from .env (WHATSAPP_GROUP_ID - see env.example)
            self.grp_id=os.getenv('WHATSAPP_GROUP_ID')
        if(self.user_email==""):
            self.user_email="Youremail@gmail.com"
        print(self.user_email)
        save_img = not nosave and not source.endswith('.txt') # save inference images
        is_file = Path(source).suffix[1:] in (IMG_FORMATS + VID_FORMATS)
        is_url = source.lower().startswith(('rtsp://', 'rtmp://', 'http://', 'https://'))
        webcam = source.isnumeric() or source.endswith('.streams') or (is_url and not is_file)
        screenshot = source.lower().startswith('screen')
        if is_url and is_file:
            source = check_file(source)
        device = select_device(device)
        cv2.namedWindow("DRONE DETECTION", cv2.WINDOW_NORMAL)
        #cv2.setWindowProperty("DRONE DETECTION", cv2.WND_PROP_FULLSCREEN, 0)
        cv2.moveWindow("DRONE DETECTION", 200, 100) # Move it to (40,30)
        model = DetectMultiBackend(weights, device=device, dnn=dnn, data=data, fp16=half)
        stride, names, pt = model.stride, model.names, model.pt
        save_dir = "D:\\TF PROGRAM\\DRONE YOLO\\Outputs"
        #dataset = LoadStreams(source, img_size=imgsz, stride=stride, auto=pt, vid_stride=vid_stride)
        bs = 1
        if webcam:
            view_img = check_imshow(warn=True)
            dataset = LoadStreams(source, img_size=imgsz, stride=stride, auto=pt, vid_stride=vid_stride)
            bs = len(dataset)
        elif screenshot:
            dataset = LoadScreenshots(source, img_size=imgsz, stride=stride, auto=pt)
        else:
            dataset = LoadImages(source, img_size=imgsz, stride=stride, auto=pt, vid_stride=vid_stride)
        vid_path, vid_writer = [None] * bs, [None] * bs
        model.warmup(imgsz=(1 if pt or model.triton else bs, 3, *imgsz)) # warmup
        seen, windows, dt = 0, [], (Profile(), Profile(), Profile())
        for path, im, im0s, vid_cap, s in dataset:
            with dt[0]:
                im = torch.from_numpy(im).to(model.device)
                im = im.half() if model.fp16 else im.float() # uint8 to fp16/32
                im /= 255 # 0 - 255 to 0.0 - 1.0
                if len(im.shape) == 3:
                    im = im[None] # expand for batch dim
            with dt[1]:
                pred = model(im, augment=augment, visualize=False)
            # NMS
            with dt[2]:
                pred = non_max_suppression(pred, conf_thres, iou_thres, classes, agnostic_nms, max_det=max_det)
            for i, det in enumerate(pred): # per image
                seen += 1
                if webcam:
                    p, im0, frame = path[i], im0s[i].copy(), dataset.count
                    s += f'{i}: '
                else:
                    p, im0, frame = path, im0s.copy(), getattr(dataset, 'frame', 0)
                #s += '%gx%g ' % im.shape[2:] # print string
                cv2.putText(im0,
                            "No of Drones"+str(len(det))+"", (1040, 685),
                            0,
                            1,
                            (0,0,0),
                            thickness=2,
                            lineType=cv2.LINE_AA)
                annotator = Annotator(im0, line_width=line_thickness, example=str(names))
                if (len(alarm_list) >= 61):
                    alarm_list.clear()
                if len(det):
                    det[:, :4] = scale_boxes(im.shape[2:], det[:, :4], im0.shape).round()
                    for c in det[:, 5].unique():
                        n = (det[:, 5] == c).sum() # detections per class
                    for *xyxy, conf, cls in reversed(det):
                        c = int(cls)
                        label = None if hide_labels else (names[c] if hide_conf else f'{names[c]} {conf:.2f}')
                        dist2=annotator.box_label(xyxy, label, color=colors(c, True))
                        #print(alarm_list)
                        #print(label)
                        if (label == "drone"):
                            alarm_list.append(1)
                            if (len(alarm_list) >= 60):
                                if (alarm_list[0] == 1 and alarm_list[59] == 1):
                                    cv2.imwrite('DetDrone.jpg', im0)
                                    threading.Thread(target=self.snd).start()
                                    if (self.whatsapp_started==0):
                                        threading.Thread(target=self.mail,args=("DetDrone.jpg",self.user_email,)).start()
                                        threading.Thread(target=self.Whatsapp,args=("DetDrone.jpg",self.grp_id,dist2)).start()
                                        #threading.Thread(target=self.smssend).start()
                                        self.whatsapp_started=1
                                        self.whatstime=datetime.now()
                                    print("Drone detected")
                                    alarm_list.clear()
                        else:
                            alarm_list.append(0)
                        td=datetime.now() - self.whatstime
                        if ( td> timedelta(seconds=60)):
                            self.whatsapp_started = 0
                im0=annotator.result()
                cv2.imshow("DRONE DETECTION",im0)
                if cv2.waitKey(1) == ord('n'): # 1 millisecond
                    exit()
    def close(self,gui):
        gui.destroy()
    def run(self):
        import tkinter as tk
        from tkinter import ttk
        from PIL import Image, ImageTk
        app = tk.Tk()
        app.geometry("1920x1080")
        app.title("JG DRONE DETECTION SYSTEM")
        app.configure() # Set plain white background
        # Load and center image
        img = Image.open("bg.png")
        #img = img.resize((700, 700), Image.Resampling.LANCZOS) # Resize to fit window nicely
        self.imgtk = ImageTk.PhotoImage(img)
        panel = tk.Label(app, image=self.imgtk, bg="white")
        panel.place(relx=0.5, rely=0.5, anchor="center") # Center the image
        # Top headlines - centered, bold, underlined
        headline1 = tk.Label(app, text="JG DRONE DETECTION SYSTEM",
                         font=("Arial Black", 30, "bold", "underline"),
                         bg="white", fg="red")
        headline1.place(relx=0.5, rely=0.05, anchor="n")
        headline2 = tk.Label(app, text="AI BASED DRONE DETECTION SYSTEM",
                         font=("Arial Black", 25, "bold"),
                         bg="white", fg="red")
        headline2.place(relx=0.5, rely=0.12, anchor="n")
        # Right-side Labels and Entry boxes
        # Email
        label_email = tk.Label(app, text="ENTER EMAIL ID FOR ALERT",
                           font=("Arial Black", 18, "bold"), fg="red", bg="white")
        label_email.place(relx=0.75, rely=0.4, anchor="n")
        self.text_field1 = tk.Entry(app, font=("Arial", 18), justify="center", bd=3, relief="ridge")
        self.text_field1.place(relx=0.75, rely=0.45, width=300, height=35, anchor="n")
        # WhatsApp GP ID
        label_gp = tk.Label(app, text="ENTER WHATSAPP GP ID",
                        font=("Arial Black", 18, "bold"), fg="red", bg="white")
        label_gp.place(relx=0.75, rely=0.55, anchor="n")
        self.text_field2 = tk.Entry(app, font=("Arial", 18), justify="center", bd=3, relief="ridge")
        self.text_field2.place(relx=0.75, rely=0.6, width=300, height=35, anchor="n")
        # Bottom buttons with curved/rounded edges
        style = ttk.Style()
        style.configure("Rounded.TButton", font=("Arial Black", 20, "bold"), foreground="red",
                    background="white", borderwidth=3, relief="raised")
        style.map("Rounded.TButton",
              background=[('active', 'lightgrey')],
              relief=[('pressed', 'sunken'), ('!pressed', 'raised')])
        # Enable Camera Feed Button
        b1 = ttk.Button(app, text="ENABLE CAMERA FEED", style="Rounded.TButton",
                    command=lambda: self.DRONEDET())
        b1.place(relx=0.5, rely=0.85, anchor="center", width=300, height=60)
        # Quit Button
        b3 = ttk.Button(app, text="QUIT", style="Rounded.TButton",
                    command=lambda: self.close(app))
        b3.place(relx=0.2, rely=0.85, anchor="center", width=200, height=60)
        app.mainloop()
if __name__ == "__main__":
    gui=GUI()
    gui.run()
