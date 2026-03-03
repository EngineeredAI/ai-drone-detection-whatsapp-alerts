        if any("1" in item for item in lane):
            cv2.rectangle(self.im, (200, 10),(440,60), color=(0, 255, 0), thickness=cv2.FILLED)
            cv2.putText(self.im, "LANE CHANGED", (200, 35),
                        0,
                        1,
                        (0, 0, 255),
                        thickness=2,
                        lineType=cv2.LINE_AA)
            threading.Thread(target=alert_snd).start()
        elif any("2" in item for item in lane):
            cv2.rectangle(self.im, (200, 10), (440, 60), color=(0, 255, 0), thickness=cv2.FILLED)
            cv2.putText(self.im, "LANE CHANGED", (200, 35),
                        0,
                        1,
                        (0, 0, 255),
                        thickness=2,
                        lineType=cv2.LINE_AA)
            threading.Thread(target=alert_snd).start()

        # Add one xyxy box to image with label
        if self.pil or not is_ascii(label):
            self.draw.rectangle(box, width=self.lw, outline=color)  # box
            if label:
                w, h = self.font.getsize(label)  # text width, height (WARNING: deprecated) in 9.2.0
                # _, _, w, h = self.font.getbbox(label)  # text width, height (New)
                outside = box[1] - h >= 0  # label fits outside box
                self.draw.rectangle(
                    (box[0], box[1] - h if outside else box[1], box[0] + w + 1,
                     box[1] + 1 if outside else box[1] + h + 1),
                    fill=color,
                )
                # self.draw.text((box[0], box[1]), label, fill=txt_color, font=self.font, anchor='ls')  # for PIL>8.0
                self.draw.text((box[0], box[1] - h if outside else box[1]), label, fill=txt_color, font=self.font)
        else:  # cv2
            p1, p2 = (int(box[0]), int(box[1])), (int(box[2]), int(box[3]))
            mpx,mpy=((p1[0]+p2[0])//2),((p1[1]+p2[1])//2)
            if label:
                tf = max(self.lw - 1, 1)  # font thickness
                w, h = cv2.getTextSize(label, 0, fontScale=self.lw / 3, thickness=tf)[0]  # text width, height
                outside = p1[1] - h >= 3
                if (mpx <= 190):
                    lane.append("0")
                    zone="LT"
                    labels.append(zone)
                elif (mpx>190 and mpx<450):
                    if(mpy>(743.07692 - 1.38461*mpx) and mpy>(1.38461*mpx - 143.07692)):
                        zone="MID"
                        lane.append("1")
                        labels.append(zone)
                    elif (mpy<(743.07692 - 1.38461*mpx) and mpy>(1.38461*mpx - 143.07692)):
                        lane.append("0")
                        zone = "LT"
                        labels.append(zone)
                    else:
                        lane.append("0")
                        zone = "RT"
                        labels.append(zone)
                elif (mpx >= 450):
                    lane.append("0")
                    zone="RT"
                    labels.append(zone)
                cv2.putText(self.im,label, (p1[0], p1[1] - 2 if outside else p1[1] + h + 2),0,self.lw / 3,txt_color,thickness=tf,lineType=cv2.LINE_AA)
                maxlen=20
                maxlanelen = 20
                if (len(lane) >= maxlanelen):
                    lane.clear()
                if len(labels) == maxlen:
                    l1=labels[0][-1]
                    l2=labels[0]
                    if ((l2=="LT" and l1=="0") and (l2=="MID" and l1=="0")):
                        lane.append("1")
                    elif ((labels[0]=="RT" and labels[maxlen-1]=="MID")):
                        lane.append("2")
                    labels.clear()