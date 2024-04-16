import Elva_serial as EV
import signal
import sys
import RPi.GPIO as GPIO
from datetime import datetime
import numpy as np
import time

DNP_frq = 187.8
frq_list = np.linspace(187.5,188.5,41)
mw_idx = -1
#mw_pwr = 140
pin_switch = 17
pins = [14, 1]
pin_trig = 19
mw = EV.ELVA(port='/dev/ttyUSB0')

old_print = print
def timestamped_print(*args, **kwargs):
    old_print('['+datetime.now().strftime('%Y-%m-%d %H:%M:%S')+']  ', *args, **kwargs)
print = timestamped_print


def signal_handler(sig, frame):
    reset_close()

def order_detect(channel):
    global mw_idx
    I2=GPIO.input(pins[0])
    I3=GPIO.input(pins[1])
    if I2==1 and I3==1:
        print('microwave OFF')
        print('Setting DNP build-up frequency ... ')
        mw_status = mw.setFrequency(DNP_frq)
        if mw_status:
            GPIO.output(pin_trig,0)
            time.sleep(0.01)
            GPIO.output(pin_trig,1)
            print('microwave ON')
    elif I2==1 and I3==0:
        print('microwave OFF')
        print('Setting spin diffusion frequency ...')
        mw_status = mw.setFrequency(frq_list[mw_idx])
        if mw_status:
            GPIO.output(pin_trig,0)
            time.sleep(0.01)
            GPIO.output(pin_trig,1)
            print('microwave ON')
    elif I2==0 and I3==1:
        mw_idx = mw_idx + 1
        print('Spin diffusion frequency is changed to {} GHz'.format(frq_list[mw_idx]))
    elif I2==0 and I3==0:
        reset_close()

def mw_init():
    mw.setPower(0)
    mw.setFrequency(188.00000)
    mw.switchOn()
    mw.dacOn()
    mw.setDAC(3000)
    time.sleep(0.2)
    
def reset_close():
    print('resetting and disconnecting ...')
    mw.setFrequency(188.00000)
    time.sleep(0.5)
    mw.dacOff()
    time.sleep(0.5)
    mw.setPower(0)
    time.sleep(1)
    mw.switchOff()
    time.sleep(1)
    mw.ser.close()
    GPIO.cleanup()
    print('Microwave sources are reset and disconnected')
    sys.exit(0)


if __name__ == '__main__':
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(pins,GPIO.IN,pull_up_down=GPIO.PUD_UP)
    GPIO.setup(pin_switch,GPIO.IN,pull_up_down=GPIO.PUD_UP)
    GPIO.setup(pin_trig,GPIO.OUT,initial=GPIO.HIGH)
    mw_init()

    GPIO.add_event_detect(pin_switch,GPIO.FALLING,callback=order_detect)
    
    signal.signal(signal.SIGINT,signal_handler)
    signal.pause()
