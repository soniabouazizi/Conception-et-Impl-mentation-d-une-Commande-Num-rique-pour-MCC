import RPi.GPIO as GPIO
import time
import matplotlib.pyplot as plt

GPIO_A = 17
PULSES = 24
RATIO = 218
SAMPLE_TIME = 0.1 # Échantillonnage rapide : toutes les 0.2 secondes

pulse_count = 0
const = 60 / (SAMPLE_TIME * PULSES)

motor_speeds = []
gear_speeds = []
times = []

def count_pulse(channel):
    global pulse_count
    pulse_count += 1

# Configuration GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(GPIO_A, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.add_event_detect(GPIO_A, GPIO.RISING, callback=count_pulse)

# Configuration du graphe
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))  # Plus grand graphique
fig.tight_layout(pad=4)

start_time = time.time()

try:
    while True:
        pulse_count = 0
        time.sleep(SAMPLE_TIME)

        Motor_rpm = pulse_count * const
        Gear_rpm = Motor_rpm / RATIO
        current_time = time.time() - start_time

        motor_speeds.append(Motor_rpm)
        gear_speeds.append(Gear_rpm)
        times.append(current_time)

        ax1.clear()
        ax2.clear()

        # Tracer la vitesse moteur
        ax1.plot(times, motor_speeds, label="Moteur", color='royalblue', linewidth=2)
        ax1.set_title("Vitesse du Moteur (RPM)", fontsize=14)
        ax1.set_xlabel("Temps (s)", fontsize=12)
        ax1.set_ylabel("Vitesse (RPM)", fontsize=12)
        ax1.grid(True, which='both', linestyle='--', linewidth=0.5)
        ax1.legend()
        ax1.set_ylim(min(motor_speeds) - 5, max(motor_speeds) + 5)  # Zoom automatique autour des valeurs

        # Tracer la vitesse réducteur
        ax2.plot(times, gear_speeds, label="Réducteur", color='seagreen', linewidth=2)
        ax2.set_title("Vitesse du Réducteur (RPM)", fontsize=14)
        ax2.set_xlabel("Temps (s)", fontsize=12)
        ax2.set_ylabel("Vitesse (RPM)", fontsize=12)
        ax2.grid(True, which='both', linestyle='--', linewidth=0.5)
        ax2.legend()
        ax2.set_ylim(min(gear_speeds) - 0.1, max(gear_speeds) + 0.1)  # Zoom automatique

        plt.pause(0.01)

except KeyboardInterrupt:
    print("Arrêt du programme.")

finally:
    GPIO.cleanup()