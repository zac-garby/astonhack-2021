import cv2
import numpy as np
import sys
import time
import serial

ser = serial.Serial(port="/dev/cu.usbmodem1101",
                    baudrate = 115200,
                    parity=serial.PARITY_NONE,
                    stopbits=serial.STOPBITS_ONE,
                    bytesize=serial.EIGHTBITS,
                    timeout=1)

temp = None

flag_reg_min = (553, 171)
flag_reg_max = (562, 178)

def click(e, x, y, flags, param):
    global flag_reg_min, flag_reg_max
                
    if e == cv2.EVENT_LBUTTONDOWN:
        if flag_reg_min == None:
            flag_reg_min = (x, y)
        elif flag_reg_max == None:
            flag_reg_max = (x, y)
            print("flag region:", flag_reg_min, "to", flag_reg_max)
            print("now select the LCD display region")
            cv2.rectangle(temp, flag_reg_min, flag_reg_max, (0, 255, 0), 2, 8)
                
        cv2.circle(temp, (x, y), 20, (255, 0, 0), -1)

def calibrate(img):
    global temp, flag_reg_min, flag_reg_max
    
    temp = img.copy()
    
    cv2.namedWindow("calibration")
    cv2.setMouseCallback("calibration", click)
    
    print("select the following regions from top-left to bottom-right")
    print("select the flag region")
    
    while flag_reg_max == None:
        cv2.imshow("calibration", temp)
        if cv2.waitKey(20) & 0xFF == 27:
            break
        
    print(flag_reg_min, flag_reg_max)
    
    cv2.destroyAllWindows()

def qr(img):
    decoder = cv2.QRCodeDetector()

    data, bbox, rectified_img = decoder.detectAndDecode(img)
    if len(data) > 0:
        return data == "one"
    else:
        return None
    
def flag(img):
    roi = img[flag_reg_min[1]:flag_reg_max[1], flag_reg_min[0]:flag_reg_max[0]]
    rows, cols, _ = roi.shape
    r_tot = 0
    g_tot = 0
    
    for i in range(rows):
        for j in range(cols):
            [b, g, r] = roi[i, j]
            if r > g:
                r += 1
            elif g > r:
                g += 1
        
    return g > r

cam = cv2.VideoCapture(0)
_, frame = cam.read()
# cam.release()

if False:
    flag_reg_min = None
    flag_reg_max = None
    calibrate(frame)
else:
    while True:        
        #cam = cv2.VideoCapture(0)
        check, frame = cam.read()
        #cam.release()
    
        q = qr(frame)
        if q == None:
            continue
    
        ser.write(("1" if flag(frame) else "0").encode("utf-8"))
        ser.write(("1" if q else "0").encode("utf-8"))
        ser.write("\r\n".encode("utf-8"))
        ser.flush()
