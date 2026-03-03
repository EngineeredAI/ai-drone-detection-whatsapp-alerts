# 🛰 AI Drone Detection & Alert System

An AI-powered real-time drone detection system built using deep learning
and automated alert pipelines.

This system detects drones from:

-   🎥 Live camera feed (Webcam / RTSP / IP Camera)\
-   📹 Video files\
-   📷 Image input

When a drone is detected, the system:

-   🔔 Triggers audio alert\
-   📩 Sends Email notification (with image attachment)\
-   📲 Sends SMS alert (Twilio)\
-   📸 Sends WhatsApp group alert with geolocation

------------------------------------------------------------------------

## 🚀 Core Technology Stack

### 🧠 Object Detection Engine

Built on YOLOv5 (Ultralytics) Uses Python 3.8.x

-   Custom-trained drone detection model (`drone2.pt`)
-   Optimized inference pipeline
-   Non-Max Suppression
-   Confidence threshold control
-   Real-time multi-frame validation logic

------------------------------------------------------------------------

### 📲 Alert & Communication Layer

  Service                     Purpose
  --------------------------- -----------------------------
  PyWhatKit                   Sends WhatsApp image alerts
  Twilio                      Sends SMS alerts
  SMTP (Gmail App Password)   Sends Email alerts

------------------------------------------------------------------------

## 🧠 Detection Workflow

1.  Video stream is captured (Webcam / RTSP / Video file).
2.  YOLOv5 performs real-time inference.
3.  Non-Max Suppression filters predictions.
4.  If "drone" class is detected:
    -   Detection flag is added to rolling buffer.
5.  If 60 consecutive frames confirm detection:
    -   Snapshot is saved.
    -   Alert system is triggered.
    -   Cooldown timer prevents spamming.

------------------------------------------------------------------------

## 📲 WhatsApp Alert Workflow

1.  Snapshot saved as `DetDrone.jpg`.
2.  Geolocation computed using forward geodesic calculation.
3.  Image scheduled and sent to WhatsApp group via PyWhatKit.
4.  Timestamp and coordinates included in message.

------------------------------------------------------------------------

## 📡 Alert Architecture Flow

Video Stream ↓ YOLOv5 Inference ↓ Non-Max Suppression ↓ Drone Class
Check ↓ Frame Validation Buffer ↓ Confirmed Detection ↓ Email \| SMS \|
WhatsApp Alert

------------------------------------------------------------------------

## ⚙ Installation

``` bash

**1. Python Installation**
Download and install Python 3.8

**2. Download the repo**
git clone https://github.com/EngineerAI/ai-drone-detection-whatsapp-alerts.git

**3. Change Directory**
cd ai-drone-detection-whatsapp-alerts

**4. Install the dependencies**
pip install -r requirements.txt

**FOR GPU users**

5. Install torch with version "torchvision-0.9.1+cu111-cp38-cp38-win_amd64.whl"
6. Install pytorch with version "torch-1.8.1+cu111-cp38-cp38-win_amd64.whl"

**FOR CPU USERS**

7. **Normal Install using pip**
pip instal torch==1.8.0
pip install torchvision=0.9.1

```

------------------------------------------------------------------------

## 🔐 Environment Setup

Create `.env` file using `.env.example` template.

Never commit real credentials.

------------------------------------------------------------------------

## 📜 License

MIT License

------------------------------------------------------------------------

## 👨‍💻 Developer

AI Systems Developer specializing in:

-   Computer Vision
-   Surveillance AI
-   Edge Deployment
-   Real-time Detection Systems
-   Automated Alert Architectures

Contact for customized software at gdc139913@gmail.com
