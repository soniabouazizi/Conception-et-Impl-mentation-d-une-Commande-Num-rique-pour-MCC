import RPi.GPIO as GPIO
import time

# Définir les broches
GPIO_A = 17       # Broche encodeur
ENA = 18          # PWM
PULSES = 24
Ratio = 218
SAMPLE_TIME = 10

pulse_count = 0
const = 60 / (SAMPLE_TIME * PULSES)

def count_pulse(channel):
    global pulse_count
    pulse_count += 1

# Configuration des GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(GPIO_A, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.add_event_detect(GPIO_A, GPIO.RISING, callback=count_pulse)


GPIO.setup(ENA, GPIO.OUT)

# Initialiser le PWM
pwm= GPIO.PWM(ENA, 1000)  # 1 kHz

pwm.start(0)
time.sleep(0.1)
pwm.ChangeDutyCycle(10)


try:
    while True:
        pulse_count = 0
        time.sleep(SAMPLE_TIME)

        Motor_rpm = pulse_count * const
        Gear_rpm = Motor_rpm / Ratio

        print(f"Vitesse du moteur : {Motor_rpm:.2f} RPM")
        print(f"Vitesse du réducteur : {Gear_rpm:.2f} RPM")

except KeyboardInterrupt:
    print("Arrêt du programme")

finally:
    pwm.stop()
    GPIO.cleanup()