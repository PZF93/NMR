import serial
import time
from datetime import datetime

old_print = print

def timestamped_print(*args, **kwargs):
    old_print('['+datetime.now().strftime('%Y-%m-%d %H:%M:%S')+']  ', *args, **kwargs)

print = timestamped_print


class ELVA(object):
    def __init__(self, port='/dev/ttyUSB0', baudrate=115200, timeout=0.1, mode=188):
        self.ser = serial.Serial(port=port,baudrate=baudrate,timeout=timeout)
        self.mode = mode
        self.frequency = 0
        self.power = 0
        self.isOn = False

    def readline(self):
        out = ''
        while True:
            out += self.ser.read(1).decode()
            if out != '':
                while out[-1] != '#':
                    out += self.ser.read(1).decode()
                return out
            else:
                return ''

    def write(self,cmd):
        self.ser.write(cmd.encode())
       
    def close(self):
        if self.mode == 188:
            self.setFrequency(188.00000)
        time.sleep(0.1)
        self.setPower(0)
        time.sleep(1)
        self.switchOff()
        time.sleep(0.1)
        self.ser.close()

    def dafOn(self):
        time.sleep(0.5)
        self.write('@DAF!on#')
        time.sleep(0.5)
        ans = self.readline()
        print(ans)

    def dafOff(self):
        time.sleep(0.5)
        self.write('@DAF!off#')
        time.sleep(0.5)
        ans = self.readline()
        print(ans)

    def dacOn(self):
        attempt = 1
        time.sleep(0.5)
        self.write('@DAC!on#')
        time.sleep(0.5)
        ans = self.readline()
        while ans[-3:-1] != 'on':
            if attempt <= 10:
                print('Enabling DAC mode...')
                self.write('@DAC!on#')
                time.sleep(0.5)
                ans = self.readline()
                attempt += 1
            else:
                print('Fail to enable DAC mode')
                return 0
        print('DAC mode is on')
        return 1

    def setDAC(self, AAA):
        if self.mode == 188:
            if AAA >= 0 and AAA <= 4095:
                attempt = 0
                AAA = int(AAA)
                while attempt < 10:
                    attempt += 1
                    try:
                        time.sleep(0.5)
                        self.write("@DAC!{:d}#".format(AAA))
                        time.sleep(0.5)
                        ans = self.readline()
                        if float(ans[5:-1]) == AAA:
                            self.DAC_value = AAA
                            break
                        else:
                            print('DAC value not set: '+ ans)
                    except:
                        print('Error setting DAC value.')
                if attempt == 10:
                    print('DAC: %d not set in 10 attempts!' % AAA)
                    return 0
                else:
                    print('DAC is set to %d' % AAA)
                    return 1
            else:
                print('DAC is between 0 and 4095')
                return 0



    def dacOff(self):
        attempt = 1
        time.sleep(0.5)
        self.write('@DAC!off#')
        time.sleep(0.5)
        ans = self.readline()
        while ans[-4:-1] != 'off':
            if attempt <= 10:
                print('disabling DAC mode...')
                self.write('@DAC!off#')
                time.sleep(0.5)
                ans = self.readline()
                attempt += 1
            else:
                print('Fail to disable DAC mode')
                return 0
        print('DAC mode is off')
        return 1

    def switchOn(self):
        attempt = 1
        time.sleep(0.1)
        self.write('@U27!on#')
        time.sleep(0.1)
        ans = self.readline()
        while ans[-3:-1] != 'on':
            if attempt <= 20:
                print('Switching on Microwave')
                self.write('@U27!on#')
                time.sleep(0.1)
                ans = self.readline()
                attempt += 1
            else:
                print('Fail to switch on Microwave')
                return 0
        print('Microwave on')
        return 1

    def switchOff(self):
        attempt = 1
        time.sleep(0.1)
        self.write('@U27!off#')
        time.sleep(0.1)
        ans = self.readline()
        while ans[-4:-1] != 'off':
            if attempt <= 20:
                print('Switching off Microwave')
                self.write('@U27!off#')
                time.sleep(0.1)
                ans = self.readline()
                attempt += 1
            else:
                print('Fail to switch off Microwave')
                return 0
        print('Microwave off')
        return 1

    def setFrequency(self, frequency_input):
        if self.mode == 188:
            frequency = frequency_input * 1000
            frequency = round(frequency,2)
            if frequency > 187499.99 and frequency < 188500.01:
                attempt = 0
                while attempt < 10:
                    attempt += 1
                    try:
                        time.sleep(0.1)
                        self.write('@FRQ!{:.2f}#'.format(frequency))
                        time.sleep(0.1)
                        ans = self.readline()
                        if float(ans[5:-1]) == frequency:
                            self.frequency = frequency
                            for idx in range(0,3):
                                time.sleep(0.1)
                                self.write('@FRC?#')
                                time.sleep(0.1)
                                temp_ans1 = self.readline()
                                time.sleep(0.1)
                                self.write('@FRQ?#')
                                time.sleep(0.1)
                                temp_ans2 = self.readline()
                                if temp_ans1 != '' and temp_ans2 != '':
                                    print(temp_ans1 + ' ' + temp_ans2)
                                    break
                            break
                        else:
                            print('Frequency not set to: %f GHz' % frequency_input )
                    except:
                        print('Error setting Frequency')
            else:
                print('Input frequency is between 187.5 GHz and 188.5 GHz')
                return 0
            if attempt == 10:            
                print('Frequency: %.5f GHz not set in 10 attempts!' % frequency_input)
                return 0
            else:
                print('Frequency is set to %.5f' % frequency_input)
                return 1

    def getFrequency(self):
        attempt = 0
        while attempt < 10:
            attempt += 1
            time.sleep(0.1)
            self.write("@FRC?#")
            time.sleep(0.1)
            ans = self.readline()
            if float(ans[5:-1]) > 100:
                break
        if attempt == 10:
            print('Fail to get frequency')
            return 0
        else:    
            print('Frequency is ' + ans[5:8] + '.' +ans[8:11] + ans[-3:-1] + 'GHz')
            return ans[5:-1]

    def setPower(self, power):
        if self.mode == 188:
            if power >= 0 and power <= 150:
                attempt = 0
                power = int(power)
                while attempt < 10:
                    attempt += 1
                    try:
                        time.sleep(0.1)
                        self.write("@PWR!{:03d}#".format(power))
                        time.sleep(0.1)
                        ans = self.readline()
                        if float(ans[5:-1]) == power:
                            self.power = power
                            break
                        else:
                            print('Power not set: '+ ans)
                    except:
                        print('Error setting power.')
                if attempt == 10:
                    print('Power: %d mw not set in 10 attempts!' % power)
                    return 0
                else:
                    print('Power is set to %d mw' % power)
                    return 1
            else:
                print('Power is between 0 and 150 mw')
                return 0


    def getPower(self):
        attempt = 0
        while attempt < 10:
            attempt += 1
            time.sleep(0.1)
            self.write("@PWR?#")
            time.sleep(0.1)
            ans = self.readline()
            if float(ans[5:-1]) > -1:
                break
        if attempt == 10:
            print('Fail to get frequency')
            return 0
        else:    
            print('Power is ' + ans[5:-1] + 'mw')
            return ans[5:-1]

