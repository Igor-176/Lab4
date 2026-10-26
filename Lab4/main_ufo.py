import sys, os
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt

class UfoGame(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi('ufo.ui', self)
        
        if os.path.exists('ufo.png'):
            pix = QPixmap('ufo.png')
        else:
            pix = QPixmap(60, 60)
            pix.fill(Qt.green) # Зеленый квадрат, если нет картинки
            
        self.ufoLabel.setPixmap(pix.scaled(60, 60, Qt.KeepAspectRatio))
        self.ufoLabel.resize(60, 60)
        
        self.step = 20
        self.ufoLabel.move(self.width()//2, self.height()//2)

    def keyPressEvent(self, event):
        x, y = self.ufoLabel.x(), self.ufoLabel.y()
        w, h = self.width(), self.height()
        uw, uh = self.ufoLabel.width(), self.ufoLabel.height()
        
        if event.key() == Qt.Key_Left:
            x -= self.step
            if x + uw < 0: x = w
        elif event.key() == Qt.Key_Right:
            x += self.step
            if x > w: x = -uw
        elif event.key() == Qt.Key_Up:
            y -= self.step
            if y + uh < 0: y = h
        elif event.key() == Qt.Key_Down:
            y += self.step
            if y > h: y = -uh
            
        self.ufoLabel.move(x, y)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = UfoGame()
    w.show()
    sys.exit(app.exec_())