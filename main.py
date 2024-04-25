import sys
from PyQt5.QtCore import Qt
# from PySide6.QtGui import QFont
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QVBoxLayout,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QWidget,
    QLabel,
    QFileDialog,
    QMessageBox,
    QButtonGroup,
    QRadioButton,
    QTabWidget,
    QTableWidget,
    QTableWidgetItem,
    QSizePolicy,
    QSpinBox,
    QGroupBox,
    QCheckBox,
    QGridLayout
)

from avgtMain import checkForErrorsAvgTmp, calcAvgTmp
from convStatMain import convertFiles
from surfaceMain import calcDF


class Avgt(QWidget):
    def __init__(self):
        super(Avgt, self).__init__()
        self.linePath = QLineEdit()
        self.linePath.setPlaceholderText("Путь к файлу")

        self.group = QButtonGroup()
        self.bEast = QRadioButton("В. Д.")
        self.bEast.setChecked(True)
        self.bWest = QRadioButton("З. Д.")
        self.group.addButton(self.bEast, 1)
        self.group.addButton(self.bWest, 2)

        hboxEW = QHBoxLayout()
        hboxEW.addWidget(self.bEast)
        hboxEW.addWidget(self.bWest)

        self.lineX = QLineEdit()
        self.lineX.setPlaceholderText("Координата X")

        self.lineY = QLineEdit()
        self.lineY.setPlaceholderText("Координата Y")

        self.bPath = QPushButton("Открыть")
        self.bPath.clicked.connect(self.setFilePathToLinePath)

        self.bStart = QPushButton("Начать")
        self.bStart.clicked.connect(self.startAvgTemp)

        self.tempsTable = QTableWidget(1, 13)
        self.tempsTable.setItem(0, 0, QTableWidgetItem('Ср. темп., C'))
        self.tempsTable.setHorizontalHeaderLabels(
            ['Давление, гПа', '1000', '925', '850', '800', '500', '400', '300', '250', '200', '150', '100', '70'])

        # self.label = QLabel(self.lblStr)
        # self.label.setFont(QFont("Times", 16))
        self.vbox = QVBoxLayout()
        self.hbox = QHBoxLayout()
        self.hbox.addWidget(self.linePath)
        self.hbox.addWidget(self.bPath)
        self.vbox.addLayout(self.hbox)
        self.vbox.addLayout(hboxEW)
        self.vbox.addWidget(self.lineX)
        self.vbox.addWidget(self.lineY)
        self.vbox.addWidget(self.bStart)
        self.vbox.addWidget(self.tempsTable)
        # self.vbox.addWidget(self.label)

        self.vbox.setAlignment(self.bStart, Qt.AlignmentFlag.AlignCenter)

        self.setLayout(self.vbox)

    def setFilePathToLinePath(self):
        name, _ = QFileDialog.getOpenFileName(self, "Выберите файл", "C:/", "Текстовый файл (*.txt)")
        if name:
            self.linePath.setText(name)

    def startAvgTemp(self):
        x, y, err = checkForErrorsAvgTmp(self.linePath.text(), self.lineX.text(), self.lineY.text(),
                                         self.group.checkedId())

        if len(err) > 0:
            message = QMessageBox()
            message.setWindowTitle("Ошибка")
            message.setText("\n".join(i for i in err))
            message.exec()
        else:
            avgT = calcAvgTmp(x, y)
            for i in range(len(avgT)):
                self.tempsTable.setItem(0, i + 1, QTableWidgetItem(str(avgT[i])))


class Surface(QWidget):
    def __init__(self):
        super(Surface, self).__init__()
        self.lineLevel = QLineEdit()
        self.lineLevel.setPlaceholderText("Путь к файлу")
        # self.lineLevel.setText("C:/Users/User/PycharmProjects/xlNew/venv/124.txt")
        bOpenLevel = QPushButton("Открыть")
        bOpenLevel.clicked.connect(self.openFileLevel)
        hboxLineLevel = QHBoxLayout()
        hboxLineLevel.addWidget(self.lineLevel)
        hboxLineLevel.addWidget(bOpenLevel)
        self.level = QSpinBox()
        self.level.setMinimum(1)
        self.level.setMaximum(12)
        self.levelLabel = QLabel("Высота")
        hboxLevel = QHBoxLayout()
        hboxLevel.addWidget(self.levelLabel)
        hboxLevel.addWidget(self.level)

        groupIntervals = QGroupBox("Интервалы")
        vboxIntervals = QVBoxLayout(groupIntervals)

        self.checkLayouts = QCheckBox("Слой целиком")
        self.checkLayouts.stateChanged[int].connect(self.checkLayoutsState)

        self.gridLayout = QGridLayout()

        labels = ["  0 - 30", "30 - 60", "60 - 90"]
        for i in range(3):
            self.gridLayout.addWidget(QLabel(labels[i]), i, 0)

        placeholderTexts = ('Мин. Т', 'Макс. Т', 'Шаг')

        for i in range(3):
            text = placeholderTexts[i]
            for j in range(3):
                editWidget = QLineEdit()
                editWidget.setPlaceholderText(text)
                self.gridLayout.addWidget(editWidget, j, i+1)

        vboxIntervals.addWidget(self.checkLayouts)
        vboxIntervals.addLayout(self.gridLayout)

        bSurface = QPushButton("Начать")
        bSurface.clicked.connect(self.startIntervals)

        hBoxRound = QHBoxLayout()
        labelRound = QLabel("Округление до знаков:")
        self.spinRound = QSpinBox()
        self.spinRound.setMinimum(0)
        self.spinRound.setValue(1)
        self.spinRound.valueChanged.connect(self.updateRoundNumber)
        hBoxRound.addWidget(labelRound)
        hBoxRound.addWidget(self.spinRound)

        vboxSurface = QVBoxLayout()
        vboxSurface.addLayout(hboxLineLevel)
        vboxSurface.addLayout(hboxLevel)
        vboxSurface.addWidget(groupIntervals)
        vboxSurface.addWidget(bSurface)
        vboxSurface.addSpacing(16)
        vboxSurface.addLayout(hBoxRound)
        vboxSurface.setAlignment(bSurface, Qt.AlignmentFlag.AlignCenter)

        self.tabBar = QTabWidget()
        labels = ["Интервалы", "Количество", "Процент", "Ср. значение", "Суммы", "Мин", "Макс"]
        self.names = ["Тропический пояс", "Умеренный пояс", "Полярный пояс", "Слой целиком"]
        for i in range(3):
            tbl = QTableWidget(1, 7)
            tbl.setHorizontalHeaderLabels(labels)
            self.tabBar.addTab(tbl, self.names[i])

        vboxSurface.addWidget(self.tabBar)

        self.setLayout(vboxSurface)

    def checkLayoutsState(self):
        checked = self.checkLayouts.isChecked()

        self.gridLayout.itemAtPosition(0, 0).widget().setText(checked and "  0 - 90" or "  0 - 30")

        for i in range(4):
            for j in range(1, 3):
                self.gridLayout.itemAtPosition(j, i).widget().setEnabled(not checked)

        self.tabBar.setTabText(0, checked and self.names[3] or self.names[0])
        for i in range(1, 3):
            self.tabBar.setTabEnabled(i, not checked)

    def openFileLevel(self):
        name, _ = QFileDialog.getOpenFileName(self, "Выберите файл", "C:/", "Текстовый файл (*.txt)")
        if name:
            self.lineLevel.setText(name)

    def updateRoundNumber(self):
        self.dataToTable()

    def dataToTable(self):
        roundNumber = self.spinRound.value()

        for k, v in self.data.items():
            widget = self.tabBar.widget(k)
            bins = v['bins']
            widget.setRowCount(len(bins))
            for i in range(len(bins) - 1):
                s = f'{bins[i]} - {bins[i + 1]}'
                widget.setItem(0 + i, 0, QTableWidgetItem(s))
            widget.setItem(len(bins) - 1, 0, QTableWidgetItem("Итого"))
            counts = v['counts']
            for i in range(len(counts)):
                widget.setItem(0 + i, 1, QTableWidgetItem(str(round(counts[i], roundNumber))))
            widget.setItem(0 + len(counts), 1, QTableWidgetItem(str(round(v['countsSUM'], roundNumber))))
            percents = v['percents']
            for i in range(len(percents)):
                widget.setItem(0 + i, 2, QTableWidgetItem(str(percents[i])))
            widget.setItem(0 + len(percents), 2, QTableWidgetItem(str(v['percentsSUM'])))
            mean = v['mean']
            sum = v['sum']
            min = v['min']
            max = v['max']
            for i in range(len(mean)):
                widget.setItem(0 + i, 3, QTableWidgetItem(str(mean[i])))
                widget.setItem(0 + i, 4, QTableWidgetItem(str(sum[i])))
                widget.setItem(0 + i, 5, QTableWidgetItem(str(min[i])))
                widget.setItem(0 + i, 6, QTableWidgetItem(str(max[i])))

    def startIntervals(self):
        # Эта функция пока не оптимизирована
        intervals = []
        rng = self.checkLayouts.isChecked() and 1 or 3
        for i in range(0, rng):
            for j in range(1, 4):
                try:
                    value = float(self.gridLayout.itemAtPosition(i, j).widget().text())
                    intervals.append(value)
                except:
                    message = QMessageBox()
                    message.setText("Введено не числовое значение")
                    message.exec()
                    return

        self.data = calcDF(self.lineLevel.text(), intervals, self.level.value(), self.checkLayouts.isChecked())

        self.dataToTable()

        # roundNumber = self.spinRound.value()
        #
        # for k, v in data.items():
        #     widget = self.tabBar.widget(k)
        #     bins = v['bins']
        #     widget.setRowCount(len(bins))
        #     for i in range(len(bins) - 1):
        #         s = f'{bins[i]} - {bins[i+1]}'
        #         widget.setItem(0 + i, 0, QTableWidgetItem(s))
        #     widget.setItem(len(bins) - 1, 0, QTableWidgetItem("Итого"))
        #     counts = v['counts']
        #     for i in range(len(counts)):
        #         widget.setItem(0 + i, 1, QTableWidgetItem(str(round(counts[i], roundNumber))))
        #     widget.setItem(0 + len(counts), 1, QTableWidgetItem(str(round(v['countsSUM'], roundNumber))))
        #     percents = v['percents']
        #     for i in range(len(percents)):
        #         widget.setItem(0 + i, 2, QTableWidgetItem(str(percents[i])))
        #     widget.setItem(0 + len(percents), 2, QTableWidgetItem(str(v['percentsSUM'])))
        #     mean = v['mean']
        #     sum = v['sum']
        #     min = v['min']
        #     max = v['max']
        #     for i in range(len(mean)):
        #         widget.setItem(0 + i, 3, QTableWidgetItem(str(mean[i])))
        #         widget.setItem(0 + i, 4, QTableWidgetItem(str(sum[i])))
        #         widget.setItem(0 + i, 5, QTableWidgetItem(str(min[i])))
        #         widget.setItem(0 + i, 6, QTableWidgetItem(str(max[i])))



class Converter(QWidget):
    def __init__(self):
        super(Converter, self).__init__()
        self.lineConvert = QLineEdit()
        self.lineConvert.setPlaceholderText("Укажите путь к папке")

        bOpenConvert = QPushButton("Открыть")
        bOpenConvert.clicked.connect(self.openConvertDirectory)

        bStartConvert = QPushButton("Начать")
        bStartConvert.clicked.connect(self.startConvert)

        self.checkForStat = QCheckBox("Добавить файлы статистики")

        labelConvert = QLabel("Конвертация")
        self.labelConvertInfo = QLabel("Укажите папку с файлами для конвертации\nи нажмите кнопку \"Начать\"")

        hboxConvert = QHBoxLayout()
        hboxConvert.addWidget(self.lineConvert)
        hboxConvert.addWidget(bOpenConvert)
        hboxConvert1 = QHBoxLayout()
        hboxConvert1.addWidget(labelConvert)
        hboxConvert1.addWidget(bStartConvert)
        hboxConvert1.addWidget(self.checkForStat)
        vboxConvert = QVBoxLayout()
        vboxConvert.addLayout(hboxConvert)
        vboxConvert.addLayout(hboxConvert1)
        vboxConvert.addSpacing(16)
        vboxConvert.addWidget(self.labelConvertInfo)

        vboxConvert.setAlignment(Qt.AlignmentFlag.AlignTop)
        hboxConvert1.setAlignment(Qt.AlignmentFlag.AlignLeft)

        self.setLayout(vboxConvert)

    def openConvertDirectory(self):
        directory = QFileDialog.getExistingDirectory(self, "Укажите папку с файлами для конвертации", "C:\\")
        if directory:
            self.lineConvert.setText(directory)

    def startConvert(self):
        message = QMessageBox()
        message.setWindowTitle("Конвертация")
        if not convertFiles(self.lineConvert.text(), self.checkForStat.isChecked()):
            message.setText("Путь к папке указан не верно")
        else:
            message.setText("Конвертация файлов выполнена")
        message.exec()


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        tabBar = QTabWidget()

        self.setWindowTitle("Температура")
        self.setGeometry(320, 320, 500, 500)

        avgTempsWidget = Avgt()

        # self.lineLevel = QLineEdit()
        # self.lineLevel.setPlaceholderText("Путь к файлу")
        # bOpenLevel = QPushButton("Открыть")
        # hboxLineLevel = QHBoxLayout()
        # hboxLineLevel.addWidget(self.lineLevel)
        # hboxLineLevel.addWidget(bOpenLevel)
        # self.level = QSpinBox()
        # self.level.setMinimum(1)
        # self.level.setMaximum(12)
        # self.levelLabel = QLabel("Высота")
        # hboxLevel = QHBoxLayout()
        # hboxLevel.addWidget(self.levelLabel)
        # hboxLevel.addWidget(self.level)
        #
        # groupIntervals = QGroupBox("Интервалы")
        # vboxIntervals = QVBoxLayout(groupIntervals)
        #
        # self.checkLayouts = QCheckBox("Слой целиком")
        # self.checkLayouts.stateChanged[int].connect(self.checkLayoutsState)
        #
        # hbox030 = QHBoxLayout()
        # self.label030 = QLabel("  0-30")
        # self.min030 = QLineEdit()
        # self.min030.setPlaceholderText("Мин. Т")
        # self.max030 = QLineEdit()
        # self.max030.setPlaceholderText("Макс. Т")
        # self.step030 = QLineEdit()
        # self.step030.setPlaceholderText("Шаг")
        # hbox030.addWidget(self.label030)
        # hbox030.addWidget(self.min030)
        # hbox030.addWidget(self.max030)
        # hbox030.addWidget(self.step030)
        #
        # self.hbox3060 = QHBoxLayout()
        # self.label3060 = QLabel("30-60")
        # self.min3060 = QLineEdit()
        # self.min3060.setPlaceholderText("Мин. Т")
        # self.max3060 = QLineEdit()
        # self.max3060.setPlaceholderText("Макс. Т")
        # self.step3060 = QLineEdit()
        # self.step3060.setPlaceholderText("Шаг")
        # self.hbox3060.addWidget(self.label3060)
        # self.hbox3060.addWidget(self.min3060)
        # self.hbox3060.addWidget(self.max3060)
        # self.hbox3060.addWidget(self.step3060)
        #
        # self.hbox6090 = QHBoxLayout()
        # self.label6090 = QLabel("60-90")
        # self.min6090 = QLineEdit()
        # self.min6090.setPlaceholderText("Мин. Т")
        # self.max6090 = QLineEdit()
        # self.max6090.setPlaceholderText("Макс. Т")
        # self.step6090 = QLineEdit()
        # self.step6090.setPlaceholderText("Шаг")
        # self.hbox6090.addWidget(self.label6090)
        # self.hbox6090.addWidget(self.min6090)
        # self.hbox6090.addWidget(self.max6090)
        # self.hbox6090.addWidget(self.step6090)
        #
        # vboxIntervals.addWidget(self.checkLayouts)
        # vboxIntervals.addLayout(hbox030)
        # vboxIntervals.addLayout(self.hbox3060)
        # vboxIntervals.addLayout(self.hbox6090)
        #
        # bSurface = QPushButton("Начать")
        # bSurface.clicked.connect(self.startIntervals())
        #
        # vboxSurface = QVBoxLayout()
        # vboxSurface.addLayout(hboxLineLevel)
        # vboxSurface.addLayout(hboxLevel)
        # vboxSurface.addWidget(groupIntervals)
        # vboxSurface.addWidget(bSurface)
        # vboxSurface.setAlignment(bSurface, Qt.AlignmentFlag.AlignCenter)
        #
        surfaceWidget = Surface()
        # surfaceWidget.setLayout(vboxSurface)

        convertWidget = Converter()

        tabBar.addTab(avgTempsWidget, "Средние температуры")
        tabBar.addTab(surfaceWidget, "По слоям")
        tabBar.addTab(convertWidget, "Конвертация")

        self.setCentralWidget(tabBar)

    # def checkLayoutsState(self):
    #     checked = self.checkLayouts.isChecked()
    #
    #     self.label030.setText(checked and "  0-90" or "  0-30")
    #
    #     for i in range(1, 4):
    #         self.hbox3060.itemAt(i).widget().setEnabled(not checked)
    #
    #     for i in range(1, 4):
    #         self.hbox6090.itemAt(i).widget().setEnabled(not checked)

    # def openFileLevel(self):
    #     name, _ = QFileDialog.getOpenFileName(self, "Выберите файл", "C:/", "Текстовый файл (*.txt)")
    #     if name:
    #         self.lineLevel.setText(name)
    #
    # def startIntervals(self):
    #     intervals = []
    #     intervals.append(self.min030.text())
    #     intervals.append(self.max030.text())
    #     intervals.append(self.step030.text())
    #     intervals.append(self.min3060.text())
    #     intervals.append(self.max3060.text())
    #     intervals.append(self.step3060.text())
    #     intervals.append(self.min6090.text())
    #     intervals.append(self.max6090.text())
    #     intervals.append(self.step6090.text())
    #     for i in range(len(intervals)):
    #         intervals[i] = float(intervals(i))
    #
    #     data = calcDF(self.lineLevel.text(), intervals)


def my_excepthook(type, value, tback):
    QMessageBox.critical(
        window, "CRITICAL ERROR", str(value),
        QMessageBox.Cancel
    )

    sys.__excepthook__(type, value, tback)


sys.excepthook = my_excepthook


app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec()