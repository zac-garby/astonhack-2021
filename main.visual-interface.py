from machine import Pin

flag_pin = Pin(2, Pin.OUT) 
qr_pin = Pin(3, Pin.OUT)

while True:
    data = input()
    flag_on = data[0] == "1"
    qr_on = data[1] == "1"
    
    flag_pin.value(flag_on)
    qr_pin.value(qr_on)
