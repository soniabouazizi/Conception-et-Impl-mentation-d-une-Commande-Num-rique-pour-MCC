import sys
import numpy as np
from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QLineEdit, QLabel,
    QVBoxLayout, QHBoxLayout, QGroupBox, QGridLayout
)
from PyQt5.QtCore import QTimer
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class RealTimePlot(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Commande Vitesse Moteur - Temps Réel")
        self.init_ui()
        self.timer = QTimer()
        self.timer.setInterval(50)  # en ms
        self.timer.timeout.connect(self.update_plot)

        self.t = []
        self.moteur_data = []
        self.reducteur_data = []
        self.start_time = 0
        self.elapsed_time = 0

    def init_ui(self):
        main_layout = QHBoxLayout()
        control_layout = QVBoxLayout()

        # Zone de réglages
        reg_box = QGroupBox("Paramètres")
        reg_layout = QGridLayout()
        self.kp = QLineEdit("0.000558")
        self.ki = QLineEdit("0.02198")
        self.kd = QLineEdit("0.0000018")
        self.consigne_input = QLineEdit("2300.0")
        self.pwm_input = QLineEdit("50.0")  # Entrée commande PWM

        reg_layout.addWidget(QLabel("Kp:"), 0, 0)
        reg_layout.addWidget(self.kp, 0, 1)
        reg_layout.addWidget(QLabel("Ki:"), 1, 0)
        reg_layout.addWidget(self.ki, 1, 1)
        reg_layout.addWidget(QLabel("Kd:"), 2, 0)
        reg_layout.addWidget(self.kd, 2, 1)
        reg_layout.addWidget(QLabel("Consigne (tr/min):"), 3, 0)
        reg_layout.addWidget(self.consigne_input, 3, 1)
        reg_layout.addWidget(QLabel("PWM (%) :"), 4, 0)
        reg_layout.addWidget(self.pwm_input, 4, 1)
        reg_box.setLayout(reg_layout)

        self.start_btn = QPushButton("Démarrer")
        self.stop_btn = QPushButton("Arrêter")
        self.quit_btn = QPushButton("Quitter")
        self.start_btn.clicked.connect(self.start_plot)
        self.stop_btn.clicked.connect(self.stop_plot)
        self.quit_btn.clicked.connect(self.close)

        control_layout.addWidget(reg_box)
        control_layout.addWidget(self.start_btn)
        control_layout.addWidget(self.stop_btn)
        control_layout.addWidget(self.quit_btn)

        # Graphiques
        graph_layout = QVBoxLayout()
        self.fig = Figure(figsize=(6, 4))
        self.canvas = FigureCanvas(self.fig)
        self.ax1 = self.fig.add_subplot(211)
        self.ax2 = self.fig.add_subplot(212)
        self.fig.tight_layout()
        graph_layout.addWidget(self.canvas)

        main_layout.addLayout(control_layout, 1)
        main_layout.addLayout(graph_layout, 3)
        self.setLayout(main_layout)

    def start_plot(self):
        self.t = []
        self.moteur_data = []
        self.reducteur_data = []
        self.elapsed_time = 0
        self.timer.start()

    def stop_plot(self):
        self.timer.stop()

    def update_plot(self):
        try:
            consigne = float(self.consigne_input.text())
            kp = float(self.kp.text())
            ki = float(self.ki.text())
            kd = float(self.kd.text())
            pwm_val = float(self.pwm_input.text())
            pwm_val = max(0, min(pwm_val, 100))  # Limite entre 0 et 100
        except ValueError:
            return

        dt = 0.05
        self.elapsed_time += dt
        t = self.elapsed_time

        erreur = consigne - consigne * (1 - np.exp(-2 * t))
        integral = sum([consigne - x for x in self.moteur_data]) * dt if self.moteur_data else 0
        derivative = 0 if len(self.moteur_data) < 2 else (self.moteur_data[-1] - self.moteur_data[-2]) / dt

        # Modèle influencé par PWM
        moteur = pwm_val * 50 * (1 - np.exp(-2 * t)) + kp * erreur + ki * integral + kd * derivative
        moteur += np.random.normal(0, 10)  # Ajout d’un peu de bruit
        reducteur = moteur / 200

        self.t.append(t)
        self.moteur_data.append(moteur)
        self.reducteur_data.append(reducteur)

        # Limite les points affichés
        max_points = 200
        if len(self.t) > max_points:
            self.t = self.t[-max_points:]
            self.moteur_data = self.moteur_data[-max_points:]
            self.reducteur_data = self.reducteur_data[-max_points:]

        # Tracé
        self.ax1.clear()
        self.ax2.clear()

        self.ax1.plot(self.t, self.moteur_data, label="Vitesse Moteur", color="red")
        self.ax1.plot(self.t, [consigne] * len(self.t), '--', label="Consigne", color="green")
        self.ax1.set_ylabel("Vitesse (tr/min)")
        self.ax1.set_title("Moteur")
        self.ax1.grid()
        self.ax1.legend()

        self.ax2.plot(self.t, self.reducteur_data, label="Réducteur", color="blue")
        self.ax2.plot(self.t, [consigne / 200] * len(self.t), '--', label="Consigne Réducteur", color="black")
        self.ax2.set_xlabel("Temps (s)")
        self.ax2.set_ylabel("Vitesse")
        self.ax2.set_title("Réducteur")
        self.ax2.grid()
        self.ax2.legend()

        self.canvas.draw()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    gui = RealTimePlot()
    gui.resize(1000, 600)
    gui.show()
    sys.exit(app.exec_())
