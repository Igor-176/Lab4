import sys, random
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QWidget

class RunawayButton(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi('runaway.ui', self)
        self.setMouseTracking(True)
        self.btnRunaway.clicked.connect(lambda: print('Поймана!'))

    def mouseMoveEvent(self, event):
        cursor = event.pos()
        btn_center = self.btnRunaway.geometry().center()
        dx = cursor.x() - btn_center.x()
        dy = cursor.y() - btn_center.y()
        
        # Если курсор ближе 80 пикселей к центру кнопки
        if dx*dx + dy*dy < 80*80:
            w = self.width() - self.btnRunaway.width()
            h = self.height() - self.btnRunaway.height()
            if w > 0 and h > 0:
                self.btnRunaway.move(random.randint(0, w), random.randint(0, h))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = RunawayButton()
    w.show()
    sys.exit(app.exec_())