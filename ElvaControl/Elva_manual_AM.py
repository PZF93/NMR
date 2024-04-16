import Elva_serial as EV
import time
import RPi.GPIO as GPIO

PIN_trig = 19
mw = EV.ELVA(port='/dev/ttyUSB0')

GPIO.setmode(GPIO.BCM)
GPIO.setup(PIN_trig,GPIO.OUT,initial=GPIO.HIGH)

mw.setPower(0)
mw.setFrequency(188.0)
mw.switchOn()
mw.dacOn()
mw.setDAC(3000)

try:
    while True:
        exp_opt = (input('Change DAC[d] or frequency[f]: '))
        if exp_opt =='d':
            DNP_dac = float(input("Input DAC value (1-4095, default 3000): "))
            mw.setDAC(DNP_dac)
        elif exp_opt == 'f':
            DNP_frq = float(input("Input uw frequecy in GHz: "))
            mw.setFrequency(DNP_frq)
        input("Press any button to the next option")
except KeyboardInterrupt:
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
