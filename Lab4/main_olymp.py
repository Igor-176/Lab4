import sys, re, csv, os
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidgetItem
from PyQt5.QtGui import QColor

class OlympWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('olymp.ui', self)
        self.data = []
        self.load_csv('results.csv')
        self.fill_combos()
        
        # Подключение сигналов
        self.comboSchool.currentIndexChanged.connect(self.apply_filter)
        self.comboClass.currentIndexChanged.connect(self.apply_filter)
        
        self.apply_filter()

    def load_csv(self, path):
        if not os.path.exists(path):
            print(f"Файл {path} не найден!")
            return
        with open(path, encoding='utf-8') as f:
            reader = csv.reader(f)
            try:
                next(reader) # пропускаем заголовок
            except StopIteration:
                return
            for row in reader:
                if len(row) < 8: continue
                name, login = row[1], row[2]
                score_str = row[7].strip()
                score = int(score_str) if score_str.isdigit() else 0
                m = re.search(r'sh-kaluga16-(\d+)-(\d+)-', login)
                if not m: continue
                self.data.append({
                    'login': login, 'name': name, 'score': score,
                    'school': m.group(1), 'class': m.group(2)
                })

    def fill_combos(self):
        schools = sorted({d['school'] for d in self.data})
        classes = sorted({d['class'] for d in self.data})
        self.comboSchool.addItem('Все школы')
        self.comboSchool.addItems(schools)
        self.comboClass.addItem('Все классы')
        self.comboClass.addItems(classes)

    def apply_filter(self):
        school = self.comboSchool.currentText()
        cls = self.comboClass.currentText()
        filtered = [d for d in self.data
                    if (school == 'Все школы' or d['school'] == school)
                    and (cls == 'Все классы' or d['class'] == cls)]
        
        filtered.sort(key=lambda d: d['score'], reverse=True)
        
        # Подсчет мест
        places = {}
        place = 1
        i = 0
        while i < len(filtered):
            score = filtered[i]['score']
            cnt = 0
            while i < len(filtered) and filtered[i]['score'] == score:
                places[i] = place
                i += 1
                cnt += 1
            place += cnt

        self.tableWidget.setRowCount(len(filtered))
        self.tableWidget.setColumnCount(3)
        self.tableWidget.setHorizontalHeaderLabels(['Логин', 'ФИО', 'Балл'])
        
        colors = {1: QColor(255, 215, 0), 2: QColor(192, 192, 192), 3: QColor(205, 127, 50)}
        
        for row, d in enumerate(filtered):
            self.tableWidget.setItem(row, 0, QTableWidgetItem(d['login']))
            self.tableWidget.setItem(row, 1, QTableWidgetItem(d['name']))
            self.tableWidget.setItem(row, 2, QTableWidgetItem(str(d['score'])))
            
            p = places.get(row)
            if p in colors:
                for col in range(3):
                    self.tableWidget.item(row, col).setBackground(colors[p])
                    
        self.tableWidget.resizeColumnsToContents()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = OlympWindow()
    w.show()
    sys.exit(app.exec_())