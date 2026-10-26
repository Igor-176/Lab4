import sys, random
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QPainter, QColor, QBrush, QPolygon

class DrawWidget(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi('draw.ui', self)
        self.figures = []
        self.setFocusPolicy(Qt.StrongFocus)

    def mousePressEvent(self, event):
        pos = event.pos()
        size = random.randint(20, 80)
        color = QColor(random.randint(0,255), random.randint(0,255), random.randint(0,255))
        if event.button() == Qt.LeftButton:
            self.figures.append(('circle', pos, size, color))
        elif event.button() == Qt.RightButton:
            self.figures.append(('square', pos, size, color))
        self.update()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Space:
            pos = self.mapFromGlobal(self.cursor().pos())
            size = random.randint(20, 80)
            color = QColor(random.randint(0,255), random.randint(0,255), random.randint(0,255))
            self.figures.append(('triangle', pos, size, color))
            self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        for typ, pos, size, color in self.figures:
            painter.setBrush(QBrush(color))
            painter.setPen(Qt.NoPen)
            if typ == 'circle':
                painter.drawEllipse(pos, size//2, size//2)
            elif typ == 'square':
                painter.drawRect(pos.x()-size//2, pos.y()-size//2, size, size)
            elif typ == 'triangle':
                poly = QPolygon([
                    QPoint(pos.x(), pos.y()-size//2),
                    QPoint(pos.x()-size//2, pos.y()+size//2),
                    QPoint(pos.x()+size//2, pos.y()+size//2)
                ])
                painter.drawPolygon(poly)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = DrawWidget()
    w.show()
    sys.exit(app.exec_())