import sys, sqlite3, datetime
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow, QDialog, QMessageBox, QTableWidgetItem

DB = 'films_db.sqlite'

class FilmEditDialog(QDialog):
    def __init__(self, parent=None, film=None):
        super().__init__(parent)
        uic.loadUi('film_edit.ui', self)
        self.film = film
        self.load_genres()
        
        if film:
            self.lineTitle.setText(film[1])
            self.spinYear.setValue(film[2] or 0)
            idx = self.comboGenre.findData(film[3])
            if idx >= 0: self.comboGenre.setCurrentIndex(idx)
            self.spinDuration.setValue(film[4] or 0)

    def load_genres(self):
        con = sqlite3.connect(DB)
        cur = con.cursor()
        cur.execute("SELECT id, title FROM genres")
        for gid, title in cur.fetchall():
            self.comboGenre.addItem(title, gid)
        con.close()

    def accept(self):
        title = self.lineTitle.text().strip()
        if not title:
            QMessageBox.warning(self, 'Ошибка', 'Название не может быть пустым')
            return
        year = self.spinYear.value()
        if year > datetime.datetime.now().year:
            QMessageBox.warning(self, 'Ошибка', 'Год не может быть в будущем')
            return
        duration = self.spinDuration.value()
        if duration <= 0:
            QMessageBox.warning(self, 'Ошибка', 'Длительность должна быть положительной')
            return
            
        self.result_data = (title, year, self.comboGenre.currentData(), duration)
        super().accept()

class FilmsWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('films.ui', self)
        self.btnAdd.clicked.connect(self.add_film)
        self.btnEdit.clicked.connect(self.edit_film)
        self.btnDelete.clicked.connect(self.delete_film)
        self.load_table()

    def load_table(self):
        con = sqlite3.connect(DB)
        cur = con.cursor()
        cur.execute("""
            SELECT f.id, f.title, f.year, g.title AS genre, f.duration
            FROM films f LEFT JOIN genres g ON f.genre = g.id
        """)
        rows = cur.fetchall()
        headers = [d[0] for d in cur.description]
        con.close()
        
        self.tableWidget.setColumnCount(len(headers))
        self.tableWidget.setHorizontalHeaderLabels(headers)
        self.tableWidget.setRowCount(len(rows))
        self.ids = []
        
        for r, row in enumerate(rows):
            self.ids.append(row[0])
            for c, val in enumerate(row):
                self.tableWidget.setItem(r, c, QTableWidgetItem(str(val) if val is not None else ""))
        self.tableWidget.resizeColumnsToContents()

    def get_selected_id(self):
        row = self.tableWidget.currentRow()
        if row < 0:
            QMessageBox.warning(self, 'Ошибка', 'Выберите строку')
            return None
        return self.ids[row]

    def add_film(self):
        dlg = FilmEditDialog(self)
        if dlg.exec_() == QDialog.Accepted:
            title, year, genre, duration = dlg.result_data
            con = sqlite3.connect(DB)
            con.execute("INSERT INTO films(title, year, genre, duration) VALUES (?,?,?,?)",
                        (title, year, genre, duration))
            con.commit(); con.close()
            self.load_table()

    def edit_film(self):
        fid = self.get_selected_id()
        if fid is None: return
        con = sqlite3.connect(DB)
        cur = con.cursor()
        cur.execute("SELECT id, title, year, genre, duration FROM films WHERE id=?", (fid,))
        film = cur.fetchone()
        con.close()
        
        dlg = FilmEditDialog(self, film)
        if dlg.exec_() == QDialog.Accepted:
            title, year, genre, duration = dlg.result_data
            con = sqlite3.connect(DB)
            con.execute("UPDATE films SET title=?, year=?, genre=?, duration=? WHERE id=?",
                        (title, year, genre, duration, fid))
            con.commit(); con.close()
            self.load_table()

    def delete_film(self):
        fid = self.get_selected_id()
        if fid is None: return
        if QMessageBox.question(self, 'Подтверждение', 'Удалить фильм?') == QMessageBox.Yes:
            con = sqlite3.connect(DB)
            con.execute("DELETE FROM films WHERE id=?", (fid,))
            con.commit(); con.close()
            self.load_table()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = FilmsWindow()
    w.show()
    sys.exit(app.exec_())