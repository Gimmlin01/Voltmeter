from __future__ import print_function

import hid
import time
from decimal import Decimal
# enumerate USB devices

for d in hid.enumerate():
    keys = list(d.keys())
    keys.sort()
    for key in keys:
        print("%s : %s" % (key, d[key]))
    print()


#byte 0 sign

#byte 1-4 digit

#byte 5
    
#byte 6
KOMMA = {
    0x31: 1000,  #2.000
    0x32: 100,  #20.00
    0x34: 10,  #200.0
    0x30: 1, #2000
}

#byte 7
# Weder Delta noch Norm => MIN/MAX weder AC noch DC %
# 0:NORM 1:HOLD 2:DELTA 3:AC 4:DC 5:Autorange 6:

#byte 8 BATT leer? 4

#byte 9
EXP={
    0x00: (1e0,""),
    0x10: (1e6,"M"),
    0x20: (1e3,"k"),
    0x40: (1e-3,"m"),
    0x80: (1e-6,"my"),
    0x02: (1,"%"),
    0x04: (1,""), #Diode
    0x08: (1,"") #durchgang
    }

#byte 10
MODE={
    0x80: "V",
    0x20: "Ohm",
    0x08: "Hz",
    0x02: "°C",
    0x01: "°F",
    0x04: "nF",
    0x40: "A",
    0x00: "hmm"
    }



def check_bit(int_type, offset):
    mask = 1 << offset
    return bool(int_type & mask)

def parse(msg):
    if len(msg)==14:
        if msg[0]==0x2b:
            sign=1
        elif msg[0]==0x2d:
            sign=-1
        else:
            raise UnicodeError("Sign not detected")
        ACDC=""
        if check_bit(msg[7],3):
            ACDC="AC"
        elif check_bit(msg[7],4):
            ACDC="DC"
        for a in msg:
            print(hex(a),end=", ")
        print("")
        print(bin(msg[7]))
        digits=[msg[1]&0x0f,msg[2]&0x0f,msg[3]&0x0f,msg[4]&0x0f]
        digit_value = 0
        for i, digit in zip(range(4), digits):
            digit_value += digit*(10**(3-i))
        display = digit_value / KOMMA[msg[6]]
        display_value = display * EXP[msg[9]][0]
        print(str(display)+ " " + EXP[msg[9]][1] + MODE[msg[10]] + " " + ACDC)
        print(display_value)
    else:
        raise UnicodeError("Message to short")



try:
    print("Opening the device")
    h = hid.device()
    h.open(6790,57352) # TUT61C VendorID/ProductID
    buf = [0x05,0x60, 0x09, 0x00, 0x60, 0x03]
    res = h.send_feature_report(buf)
    print(res)
    time.sleep(0.05)
    msginc=False
    msg=[]
    while True:
        d = bytes(h.read(2))
        if d:
            if d[0]==0xf1:
                msg.append(d[1])
                msginc=True
            else:
                if (msginc):
                    try:
                        parse(msg)
                    except UnicodeError as ex:
                        print(ex)
                msg=[]
                msginc=False
                
except IOError as ex:
    print(ex)
    print("You probably don't have the hard coded device. Update the hid.device line")
    print("in this script with one from the enumeration list output above and try again.")
finally:
    print("Closing the device")
    h.close()
    print("Done")
