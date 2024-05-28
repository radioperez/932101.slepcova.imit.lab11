import sys
import random
import numpy as np
from numpy.random import default_rng
import scipy.stats
from PyQt6.QtCore import QSize, Qt
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QPushButton,
    QSpinBox,
    QLabel,
    QLineEdit,
    QVBoxLayout,
    QHBoxLayout,
    QFormLayout,
)
import pyqtgraph as QtGraph

class Graph(QtGraph.PlotWidget):
    def __init__(self):
        super().__init__()
        self.setBackground("w")

class MainWindow(QMainWindow):
    n_events = 1
    startable: bool = False
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Сбор статистики вероятностей')

        settings = QVBoxLayout()
        # probabilities
        self.probabilities = QFormLayout()
        self.probabilities.addRow("а:", QLineEdit())
        self.probabilities.addRow("sigma:", QLineEdit())
        settings.addLayout(self.probabilities)

        # mean and variance
        self.mean_label = QLabel("Выборочное среднее: ")
        settings.addWidget(self.mean_label)
        self.var_label = QLabel("Выборочная дисперсия: ")
        settings.addWidget(self.var_label)

        # chi squared
        self.chi_label = QLabel("Критерий хи-квадрат: ")
        settings.addWidget(self.chi_label)

        # n of trials
        self.n_trials = QSpinBox(minimum=10, maximum=100_000, singleStep=10)
        settings.addWidget(self.n_trials)

        # start button
        start_button = QPushButton("СТАРТ")
        start_button.clicked.connect(self.start)
        settings.addWidget(start_button)

        # graph
        self.graph = Graph()

        layout = QHBoxLayout()
        layout.addLayout(settings)
        layout.addWidget(self.graph)
        root = QWidget()
        root.setLayout(layout)
        self.setCentralWidget(root)

    def start(self):
        try:
            a = float(self.probabilities.itemAt(0, QFormLayout.ItemRole.FieldRole).widget().text())
        except ValueError:
            a = 0
        
        try:
            sigma = float(self.probabilities.itemAt(1, QFormLayout.ItemRole.FieldRole).widget().text())
        except ValueError:
            sigma = 1
        
        N_TRIALS = self.n_trials.value()
        
        # generate numbers and collect statistics
        OBSERVED = default_rng().normal(a, sigma, size=N_TRIALS)

        EMP_STAT, _ = np.histogram(OBSERVED, bins=10)
        EMP_FREQ = [stat/N_TRIALS for stat in EMP_STAT]

        x = np.linspace(min(OBSERVED), max(OBSERVED), 10)
        THEO_FREQ = scipy.stats.norm.pdf(x, a, sigma)

        self.calc(OBSERVED, a, sigma)
        self.chisq(EMP_FREQ, THEO_FREQ)
        self.draw(x, EMP_FREQ)

    def calc(self, DATA, a, sigma):
        EMP_MEAN = np.mean(DATA)
        MEAN_ERROR = np.abs((a - EMP_MEAN) / 2)
        self.mean_label.setText(f"Выборочное среднее: {EMP_MEAN:.2f}, погрешность {MEAN_ERROR:.2f}")

        EMP_VARIANCE = np.var(DATA)
        VAR_ERROR = np.abs((sigma - EMP_VARIANCE) / 2)
        self.var_label.setText(f"Выборочная дисперсия: {EMP_VARIANCE:.2f}, погрешность {VAR_ERROR:.2f}")
    
    def chisq(self, DATA, THEORY):
        alpha = 0.05
        CHI = sum(abs(observed - expected) for observed, expected in zip(DATA, THEORY))
        CHI_CRITICAL = scipy.stats.chi2.ppf(alpha, df = len(DATA)-1)

        self.chi_label.setText(f"Критерий хи-квадрат: {CHI:.4f} {">" if CHI > CHI_CRITICAL else "<="} {CHI_CRITICAL:.4f}")

    def draw(self, x, y):
        self.graph.clear()
        hist = QtGraph.BarGraphItem(x = x, height = y, width = 0.9, brush='b')
        self.graph.addItem(hist)
        for index, _ in enumerate(x):
            text = QtGraph.TextItem(f'{y[index]:.4f}', color='black')
            text.setPos(x[index],y[index]+0.05)
            self.graph.addItem(text)
    def ping(self):
        print("PING")

random.seed()
app = QApplication(sys.argv)
main = MainWindow()
main.show()
app.exec()
