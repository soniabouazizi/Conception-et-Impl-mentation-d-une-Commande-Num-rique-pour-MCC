import RPi.GPIO as GPIO
import time

GPIO_A = 17
PULSES = 24
Ratio = 218
SAMPLE_TIME = 10

pulse_count = 0

const = 60/(SAMPLE_TIME*PULSES)

def count_pulse(channel):
    global pulse_count
    pulse_count += 1

# Configuration de GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(GPIO_A, GPIO.IN, pull_up_down=GPIO.PUD_UP)

GPIO.add_event_detect(GPIO_A, GPIO.RISING, callback=count_pulse)

try:
    while True:
        pulse_count = 0
        time.sleep(SAMPLE_TIME)
        
        # Calcul de la vitesse en RPM
        Motor_rpm = pulse_count*const
        Gear_rpm = Motor_rpm / Ratio

        print(f"Vitesse du moteur : {Motor_rpm: .2f} RPM")
        print(f"Vitesse du réducteur : {Gear_rpm: .2f} RPM")
except KeyboardInterrupt:
    print("arret du programme")
finally:
    GPIO.cleanup()    