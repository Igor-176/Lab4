import sys, sqlite3, hashlib, os, shutil, datetime
from PyQt5 import uic
from PyQt5.QtWidgets import (QApplication, QDialog, QMainWindow, QMessageBox,
                             QTableWidgetItem, QFileDialog)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt

DB = 'library.db'
IMAGES_DIR = 'images'
os.makedirs(IMAGES_DIR, exist_ok=True)

def hash_password(pwd: str) -> str:
    return hashlib.sha256(pwd.encode()).hexdigest()

def init_db():
    con = sqlite3.connect(DB)
    cur = con.cursor()
    cur.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            login TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            year INTEGER,
            genre TEXT,
            image_path TEXT
        );
    """)
    con.commit(); con.close()

# ---------- Авторизация ----------
class LoginDialog(QDialog):
    def __init__(self):
        super().__init__()
        uic.loadUi('login.ui', self)
        self.btnLogin.clicked.connect(self.login)
        self.btnRegister.clicked.connect(self.register)

    def login(self):
        login = self.lineLogin.text().strip()
        pwd = self.linePassword.text()
        if not login or not pwd:
            QMessageBox.warning(self, 'Ошибка', 'Заполните все поля')
            return
        con = sqlite3.connect(DB)
        cur = con.cursor()
        cur.execute("SELECT password_hash FROM users WHERE login=?", (login,))
        row = cur.fetchone()
        con.close()
        if row and row[0] == hash_password(pwd):
            self.accept()
        else:
            QMessageBox.warning(self, 'Ошибка', 'Неверный логин или пароль')

    def register(self):
        dlg = RegisterDialog(self)
        if dlg.exec_() == QDialog.Accepted:
            QMessageBox.information(self, 'Успех', 'Регистрация завершена')

class RegisterDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi('register.ui', self)
        self.buttonBox.accepted.connect(self.do_register)

    def do_register(self):
        login = self.lineLogin.text().strip()
        pwd1 = self.linePassword.text()
        pwd2 = self.linePassword2.text()
        if not login or not pwd1:
            QMessageBox.warning(self, 'Ошибка', 'Заполните все поля')
            return
        if pwd1 != pwd2:
            QMessageBox.warning(self, 'Ошибка', 'Пароли не совпадают')
            return
        con = sqlite3.connect(DB)
        try:
            con.execute("INSERT INTO users(login, password_hash) VALUES (?,?)",
                        (login, hash_password(pwd1)))
            con.commit()
            self.accept()
        except sqlite3.IntegrityError:
            QMessageBox.warning(self, 'Ошибка', 'Логин уже занят')
        finally:
            con.close()

# ---------- Редактирование книги ----------
class BookEditDialog(QDialog):
    def __init__(self, parent=None, book=None):
        super().__init__(parent)
        uic.loadUi('book_edit.ui', self)
        self.book = book
        self.image_path = None
        self.btnChooseImage.clicked.connect(self.choose_image)
        
        if book:
            self.lineTitle.setText(book[1])
            self.lineAuthor.setText(book[2])
            self.spinYear.setValue(book[3] or 0)
            self.lineGenre.setText(book[4] or '')
            self.image_path = book[5]
            self.update_image()

    def choose_image(self):
        path, _ = QFileDialog.getOpenFileName(self, 'Выбрать картинку', '',
                                              'Images (*.png *.jpg *.jpeg *.bmp)')
        if path:
            fname = os.path.basename(path)
            dst = os.path.join(IMAGES_DIR, fname)
            shutil.copy(path, dst)
            self.image_path = dst
            self.update_image()

    def update_image(self):
        if self.image_path and os.path.exists(self.image_path):
            pix = QPixmap(self.image_path).scaled(120, 120, Qt.KeepAspectRatio)
            self.labelImage.setPixmap(pix)
        else:
            self.labelImage.setText('Нет изображения')

    def accept(self):
        title = self.lineTitle.text().strip()
        author = self.lineAuthor.text().strip()
        if not title or not author:
            QMessageBox.warning(self, 'Ошибка', 'Название и автор обязательны')
            return
        year = self.spinYear.value()
        if year > datetime.datetime.now().year:
            QMessageBox.warning(self, 'Ошибка', 'Год не может быть в будущем')
            return
        self.result_data = (title, author, year, self.lineGenre.text().strip(), self.image_path)
        super().accept()

# ---------- Главное окно ----------
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('main.ui', self)
        self.btnAdd.clicked.connect(self.add_book)
        self.btnEdit.clicked.connect(self.edit_book)
        self.btnDelete.clicked.connect(self.delete_book)
        self.searchAuthor.textChanged.connect(self.load_table)
        self.searchTitle.textChanged.connect(self.load_table)
        self.load_table()

    def load_table(self):
        author_filter = self.searchAuthor.text().strip()
        title_filter = self.searchTitle.text().strip()
        query = "SELECT id, title, author, year, genre, image_path FROM books WHERE 1=1"
        params = []
        if author_filter:
            query += " AND author LIKE ?"
            params.append(f'%{author_filter}%')
        if title_filter:
            query += " AND title LIKE ?"
            params.append(f'%{title_filter}%')
            
        con = sqlite3.connect(DB)
        cur = con.cursor()
        cur.execute(query, params)
        rows = cur.fetchall()
        con.close()
        
        self.tableWidget.setRowCount(len(rows))
        self.tableWidget.setColumnCount(5)
        self.tableWidget.setHorizontalHeaderLabels(['Название', 'Автор', 'Год', 'Жанр', 'Изображение'])
        self.ids = []
        
        for r, row in enumerate(rows):
            self.ids.append(row[0])
            self.tableWidget.setItem(r, 0, QTableWidgetItem(row[1]))
            self.tableWidget.setItem(r, 1, QTableWidgetItem(row[2]))
            self.tableWidget.setItem(r, 2, QTableWidgetItem(str(row[3]) if row[3] else ''))
            self.tableWidget.setItem(r, 3, QTableWidgetItem(row[4] or ''))
            
            img_item = QTableWidgetItem()
            if row[5] and os.path.exists(row[5]):
                pix = QPixmap(row[5]).scaled(60, 60, Qt.KeepAspectRatio)
                img_item.setData(Qt.DecorationRole, pix)
            else:
                img_item.setText('Нет')
            self.tableWidget.setItem(r, 4, img_item)
            
        self.tableWidget.resizeColumnsToContents()
        self.tableWidget.resizeRowsToContents()

    def get_selected_id(self):
        row = self.tableWidget.currentRow()
        if row < 0:
            QMessageBox.warning(self, 'Ошибка', 'Выберите книгу')
            return None
        return self.ids[row]

    def add_book(self):
        dlg = BookEditDialog(self)
        if dlg.exec_() == QDialog.Accepted:
            title, author, year, genre, image = dlg.result_data
            con = sqlite3.connect(DB)
            con.execute("INSERT INTO books(title, author, year, genre, image_path) VALUES (?,?,?,?,?)",
                        (title, author, year, genre, image))
            con.commit(); con.close()
            self.load_table()

    def edit_book(self):
        bid = self.get_selected_id()
        if bid is None: return
        con = sqlite3.connect(DB)
        cur = con.cursor()
        cur.execute("SELECT id, title, author, year, genre, image_path FROM books WHERE id=?", (bid,))
        book = cur.fetchone()
        con.close()
        
        dlg = BookEditDialog(self, book)
        if dlg.exec_() == QDialog.Accepted:
            title, author, year, genre, image = dlg.result_data
            con = sqlite3.connect(DB)
            con.execute("UPDATE books SET title=?, author=?, year=?, genre=?, image_path=? WHERE id=?",
                        (title, author, year, genre, image, bid))
            con.commit(); con.close()
            self.load_table()

    def delete_book(self):
        bid = self.get_selected_id()
        if bid is None: return
        if QMessageBox.question(self, 'Подтверждение', 'Удалить книгу?') == QMessageBox.Yes:
            con = sqlite3.connect(DB)
            con.execute("DELETE FROM books WHERE id=?", (bid,))
            con.commit(); con.close()
            self.load_table()

if __name__ == '__main__':
    init_db()
    app = QApplication(sys.argv)
    
    # Сначала запускаем окно логина
    login_dlg = LoginDialog()
    if login_dlg.exec_() == QDialog.Accepted:
        win = MainWindow()
        win.show()
        sys.exit(app.exec_())
    else:
        sys.exit(0)