import sys, os
import traceback
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QLineEdit, QMessageBox, QComboBox, QScrollArea,QFrame,
    QTableWidget, QTableWidgetItem, QFileDialog, QHeaderView, QListWidget, QInputDialog, QTabWidget, QDialog, QFormLayout,QDateEdit, QCheckBox
)
from PyQt6.QtGui import QPixmap, QFont
from PyQt6.QtCore import Qt, QDate

import psycopg2
from psycopg2.extras import RealDictCursor


def get_connection():
    return psycopg2.connect(
        dbname="a4kidscity",
        user="postgres",
        password=" ",
        host="127.0.1.45",
        port="5432"
    )


# ----------------- Параметры интерфейса -----------------
PRIMARY_COLOR = "#00BCD4"
SECONDARY_COLOR = "#FF9800"
ACCENT_COLOR = "#4CAF50"
CARD_BG_COLOR = "#FFF9C4"
BACKGROUND_COLOR = "#E1F5FE"
TEXT_COLOR = "#000000"

FONT_TITLE = QFont("Comic Sans MS", 16, QFont.Weight.Bold)
FONT_TEXT = QFont("Comic Sans MS", 12)


def load_accounts():
    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT login, password, ID_Parent as id_parent FROM Parents;")
            accs = {r["login"]: {"password": r["password"], "id": r["id_parent"] or r["id_parent"], "role": "user"} for r in cur.fetchall()}
    finally:
        conn.close()
    return accs

def save_account(login, password, first_name, last_name, middle_name, phone):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO Parents (last_name, first_name, middle_name, phone, login, password)
                VALUES (%s, %s, %s, %s, %s, %s);
            """, (last_name, first_name, middle_name, phone, login, password))
            conn.commit()
    finally:
        conn.close()

def load_locations():
    """
    Возвращаем список локаций как dict с ключами:
    id_location, name (алиас name_location), age_range, description, cost, image
    """
    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT ID_Location,
                       name_location,
                       age_range, 
                       description,
                       cost, 
                       image
                FROM Locations ORDER BY ID_Location;
            """)
            rows = cur.fetchall()
    finally:
        conn.close()
    return rows

def save_locations(locations):
    """
    Перезаписывает таблицу Locations (очистка + вставка).
    locations: list of dicts with keys name, description, age_range, cost, image
    """
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM Locations;")
            for loc in locations:
                cur.execute("""
                    INSERT INTO Locations (name_location, description, age_range, cost, image)
                    VALUES (%s, %s, %s, %s, %s);
                """, (loc.get("name_location"), loc.get("description"), loc.get("age_range"), loc.get("cost"), loc.get("image")))
            conn.commit()
    finally:
        conn.close()

def insert_location(name_location, description, age_range, cost, image):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO Locations (name_location, description, age_range, cost, image)
                VALUES (%s, %s, %s, %s, %s) RETURNING ID_Location;
            """, (name_location, description, age_range, cost, image))
            lid = cur.fetchone()[0]
            conn.commit()
            return lid
    finally:
        conn.close()

def update_location(id_location, name_location, description, age_range, cost, image):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE Locations SET name_location=%s, description=%s, age_range=%s, cost=%s, image=%s
                WHERE ID_Location=%s;
            """, (name_location, description, age_range, cost, image, id_location))
            conn.commit()
    finally:
        conn.close()

def delete_location(id_location):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM Locations WHERE ID_Location=%s;", (id_location,))
            conn.commit()
    finally:
        conn.close()

# Preferences
def load_preferences_for_location(id_location):
    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT ID_Preference, age_preference FROM Preferences WHERE ID_Location=%s;", (id_location,))
            return cur.fetchall()
    finally:
        conn.close()

def insert_preference(id_location, age_pref):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("INSERT INTO Preferences (ID_Location, age_preference) VALUES (%s, %s) RETURNING ID_Preference;", (id_location, age_pref))
            pid = cur.fetchone()[0]
            conn.commit()
            return pid
    finally:
        conn.close()

def delete_preference(id_pref):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM Preferences WHERE ID_Preference=%s;", (id_pref,))
            conn.commit()
    finally:
        conn.close()

# Tickets and Children
def save_ticket(user_login, child_name, child_age, id_location,data):
    conn = get_connection()
    cur = conn.cursor()
    # Родитель
    cur.execute("SELECT ID_Parent FROM Parents WHERE login=%s;", (user_login,))
    parent = cur.fetchone()
    if not parent:
        QMessageBox.warning(None, "Ошибка", "Пользователь не найден!")
        return
    id_parent = parent[0]
    # Ребенок
    cur.execute("SELECT ID_Child FROM Children WHERE name=%s AND ID_Parent=%s;", (child_name, id_parent))
    row = cur.fetchone()
    if row:
        id_child = row[0]
        
    else:
        cur.execute(
            "INSERT INTO Children (name, age, ID_Parent) VALUES (%s, %s, %s) RETURNING ID_Child;",
            (child_name, child_age, id_parent)
        )
        id_child = cur.fetchone()[0]
    # Билет
    cur.execute(
        "INSERT INTO Tickets (ID_Parent, ID_Child, ID_Location,data) VALUES (%s, %s, %s,%s);",
        (id_parent, id_child, id_location,data)
    )
    conn.commit()
    conn.close()

def load_tickets(current_user, current_role):
    """Загружает все билеты пользователя по логину"""
    try:
        conn = get_connection()
        cur = conn.cursor()

        base_query = """
        SELECT t.id_ticket, 
               c.name AS child_name, 
               c.age as child_age,
               l.name_location as name_location,
               l.cost,
               p.last_name ||  ' ' || p.first_name as parent_name,
               p.login as user_login
        FROM Tickets t
        JOIN Parents p ON t.id_parent = p.id_parent
        JOIN Children c ON t.id_child = c.id_child
        JOIN Locations l ON t.id_location = l.id_location
        WHERE p.login = %s;
        """
        if current_role == "admin":
            cur.execute("""
        SELECT t.id_ticket, 
               c.name AS child_name, 
               c.age as child_age,
               l.name_location as name_location,
               l.cost,
               p.last_name ||  ' ' || p.first_name as parent_name,
               p.login as user_login
        FROM Tickets t
        JOIN Parents p ON t.id_parent = p.id_parent
        JOIN Children c ON t.id_child = c.id_child
        JOIN Locations l ON t.id_location = l.id_location;
        """)
        else:
            cur.execute("""
        SELECT t.id_ticket, 
               c.name AS child_name, 
               c.age as child_age,
               l.name_location as name_location,
               l.cost,
               p.last_name ||  ' ' || p.first_name as parent_name,
               p.login as user_login
        FROM Tickets t
        JOIN Parents p ON t.id_parent = p.id_parent
        JOIN Children c ON t.id_child = c.id_child
        JOIN Locations l ON t.id_location = l.id_location
        WHERE p.login = %s;
        """, (current_user,))

        rows = cur.fetchall()
        conn.close()
        return [
            {
                "id_ticket": row[0],
                "child_name": row[1],
                "child_age": row[2],
                "name_location": row[3],
                "cost": row[4],
                "parent_name": row[5],
                "user_login": row[6]
            }
            for row in rows
        ]

    except Exception as e:
        print("Ошибка при загрузке билетов:", e)
        return []

def get_all_tickets():
    import psycopg2
    conn = psycopg2.connect(
        dbname="a4kidscity",
        user="postgres",
        password="password",
        host="127.0.1.45")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT t.id_ticket, 
               c.name AS child_name, 
               c.age as child_age,
               l.name_location as name_location,
               l.cost,
               p.last_name ||  ' ' || p.first_name as parent_name,
               p.login as user_login,
               t.data
        FROM Tickets t
        JOIN Parents p ON t.id_parent = p.id_parent
        JOIN Children c ON t.id_child = c.id_child
        JOIN Locations l ON t.id_location = l.id_location
        ORDER BY t.data desc;
    """)
    result = cursor.fetchall()
    conn.close()
    return result


def get_user_tickets(user_id):
    conn = psycopg2.connect(dbname="a4kidscity", user="postgres", password="password", host="127.0.1.45")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT t.id_ticket, 
               c.name AS child_name, 
               c.age as child_age,
               l.name_location as name_location,
               l.cost,
               p.last_name ||  ' ' || p.first_name as parent_name,
               p.login as user_login,
               t.data
        FROM Tickets t
        JOIN Parents p ON t.id_parent = p.id_parent
        JOIN Children c ON t.id_child = c.id_child
        JOIN Locations l ON t.id_location = l.id_location
        WHERE p.login = %s
        ORDER BY t.data desc;
    """, (user_id,))
    result = cursor.fetchall()
    conn.close()
    return result

def delete_ticket_by_id(ticket_id, user_login=None, is_admin=False):
    try:
        conn = get_connection()
        cur = conn.cursor()

        if is_admin:
            cur.execute("DELETE FROM Tickets WHERE id_ticket=%s", (ticket_id,))
        else:
            # Получаем id_parent по логину
            cur.execute("SELECT ID_Parent FROM Parents WHERE login=%s", (user_login,))
            row = cur.fetchone()
            if not row:
                conn.close()
                return False
            id_parent = row[0]
            cur.execute("DELETE FROM Tickets WHERE id_ticket=%s AND id_parent=%s", (ticket_id, id_parent))

        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print("Ошибка при удалении билета:", e)
        return False


# ----------------- Стили -----------------
def style_button(btn):
    btn.setStyleSheet(f"""
        QPushButton {{
            background-color: {PRIMARY_COLOR};
            color: white;
            border-radius: 12px;
            padding: 8px 20px;
            font-weight: bold;
            font-size: 12pt;
        }}
        QPushButton:hover {{
            background-color: {ACCENT_COLOR};
        }}
    """)


def style_card(widget):
    widget.setStyleSheet(f"""
        QWidget {{
            background-color: {CARD_BG_COLOR};
            border-radius: 12px;
            border: 2px solid {SECONDARY_COLOR};
            padding: 10px;
            color: {TEXT_COLOR};
        }}
    """)


def style_main_window(window):
    window.setStyleSheet(f"""
        QWidget {{
            background: qlineargradient(x1:0,y1:0,x2:0,y2:1, stop:0 {BACKGROUND_COLOR}, stop:1 lightgreen);
            font-family: Comic Sans MS;
            color: {TEXT_COLOR};
        }}
    """)


def style_input(input_field):
    input_field.setStyleSheet(f"""
        QLineEdit, QComboBox {{
            background-color: white;
            color: {TEXT_COLOR};
            border: 2px solid #00BCD4;
            border-radius: 8px;
            padding: 6px;
            font-size: 12pt;
            selection-background-color: #B2EBF2;
        }}
    """)


# ----------------- TicketWindow -----------------
class TicketWindow(QWidget):
    def __init__(self, current_user, current_role, parent=None):
        super().__init__()
        self.current_user = current_user
        self.current_role = current_role
        self.parent_window  = parent
        self.selected_locations = []
        self.children_widgets = []  # Список детей в виде словарей {'name':..., 'age':...}
        self.setWindowTitle("Оформление билета — A4 Kids City")
        self.resize(550, 650)
        self.__init__ui()

    def __init__ui(self):
        self.layout = QVBoxLayout()
        self.layout.setSpacing(10)

        logo = QLabel()
        pixmap = QPixmap("02083b0b-746a-430a-b7cf-0e950235229c.png")
        if not pixmap.isNull():
            pixmap = pixmap.scaled(220, 100, Qt.AspectRatioMode.KeepAspectRatio,
                                   Qt.TransformationMode.SmoothTransformation)
            logo.setPixmap(pixmap)
        else:
            logo.setText("A4 Kids City")
            logo.setFont(FONT_TITLE)
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(logo)

        self.setLayout(self.layout)
        self.setStyleSheet(f"background-color:{BACKGROUND_COLOR}; color:{TEXT_COLOR};")

        # Заголовок
        title = QLabel("Оформление билетов")
        title.setFont(FONT_TITLE)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(title)

        # Выбор даты бронирования 🆕
        self.layout.addWidget(QLabel("Выберите дату посещения:"))
        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDate(QDate.currentDate())  # сегодняшняя дата по умолчанию
        self.date_edit.setMinimumDate(QDate.currentDate())
        style_input(self.date_edit)
        self.layout.addWidget(self.date_edit)

        # Список локаций
        self.locations_combo = QComboBox()
        self.layout.addWidget(QLabel("Выберите локацию:"))
        style_input(self.locations_combo)
        self.layout.addWidget(self.locations_combo)
        self.refresh_locations()

        btn_add_location = QPushButton("Добавить локацию")
        style_button(btn_add_location)
        btn_add_location.clicked.connect(self.add_location)
        self.layout.addWidget(btn_add_location)

        # Виджет списка выбранных локаций
        self.locations_list_widget = QListWidget()
        self.layout.addWidget(QLabel("Выбранные локации:"))
        self.layout.addWidget(self.locations_list_widget)

        # Кнопка удаления локации
        btn_delete_location = QPushButton("Удалить выбранную локацию")
        style_button(btn_delete_location)
        btn_delete_location.clicked.connect(self.delete_selected_location)
        self.layout.addWidget(btn_delete_location)


        # Дети
        self.layout.addWidget(QLabel("Добавьте детей:"))
        self.children_list_widget = QListWidget()
        self.layout.addWidget(self.children_list_widget)

        btn_add_child = QPushButton("Добавить ребёнка")
        style_button(btn_add_child)
        btn_add_child.clicked.connect(self.add_child)
        self.layout.addWidget(btn_add_child)

        # Новая кнопка для редактирования ребенка
        btn_edit_child = QPushButton("Редактировать ребёнка")
        style_button(btn_edit_child)
        btn_edit_child.clicked.connect(self.edit_child)
        self.layout.addWidget(btn_edit_child)

        # Кнопка удаления ребенка
        btn_delete_child = QPushButton("Удалить выбранного ребенка")
        style_button(btn_delete_child)
        btn_delete_child.clicked.connect(self.delete_selected_child)
        self.layout.addWidget(btn_delete_child)

        # Кнопка оформления
        btn_submit = QPushButton("Оформить билеты")
        style_button(btn_submit)
        btn_submit.clicked.connect(self.create_tickets)
        self.layout.addWidget(btn_submit)

        # Кнопка выхода
        btn_exit = QPushButton("Выйти в главное меню")
        style_button(btn_exit)
        btn_exit.clicked.connect(self.close)
        self.layout.addWidget(btn_exit)

        self.setLayout(self.layout)
        self.refresh_locations()

    def refresh_locations(self):
        """Загрузка локаций из БД"""
        try:
            self.locations_combo.clear()
            self.locations = load_locations()
            if not self.locations:
                QMessageBox.warning(self, "Ошибка", "Нет доступных локаций")
                return
            for loc in self.locations:
                self.locations_combo.addItem(
                    f"{loc['name_location']} (Возраст: {loc.get('age_range','')}, Цена: {loc.get('cost','')})",
                    loc
                )
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить локации:\n{e}")

    def add_location(self):
        loc = self.locations_combo.currentData()
        if loc and loc not in self.selected_locations:
            self.selected_locations.append(loc)
            self.update_locations_widget()

    def update_locations_widget(self):
        self.locations_list_widget.clear()
        for loc in self.selected_locations:
            self.locations_list_widget.addItem(loc["name_location"])

    def delete_selected_location(self):
        selected_items = self.locations_list_widget.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Ошибка", "Выберите локацию для удаления")
            return
        for item in selected_items:
            loc_name = item.text()
            self.selected_locations = [loc for loc in self.selected_locations if loc["name_location"] != loc_name]
            self.locations_list_widget.takeItem(self.locations_list_widget.row(item))

    def add_child(self):
        name, ok1 = QInputDialog.getText(self, "Имя ребёнка", "Введите имя:")
        if not ok1 or not name.strip():
            return
        age, ok2 = QInputDialog.getInt(self, "Возраст ребёнка", "Введите возраст:", min=1, max=18)
        if not ok2:
            return
        self.children_widgets.append({"name": name.strip(), "age": age})
        self.children_list_widget.addItem(f"{name.strip()} (Возраст: {age})")

    def delete_selected_child(self):
        selected_items = self.children_list_widget.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Ошибка", "Выберите ребёнка для удаления")
            return
        for item in selected_items:
            row = self.children_list_widget.row(item)
            self.children_list_widget.takeItem(row)
            del self.children_widgets[row]

    def edit_child(self):
        selected_items = self.children_list_widget.selectedItems()
        if len(selected_items) > 1:
            QMessageBox.warning(self, "Ошибка", "Можно редактировать только одного ребенка одновременно.")
            return
        elif not selected_items:
            QMessageBox.warning(self, "Ошибка", "Выберите ребёнка для редактирования.")
            return

        selected_item = selected_items[0]
        idx = self.children_list_widget.row(selected_item)
        child = self.children_widgets[idx]

        # Диалоговое окно для редактирования
        new_name, ok1 = QInputDialog.getText(self, "Редактирование имени", "Введите новое имя:",
                                             text=child["name"])
        if not ok1 or not new_name.strip():
            return

        new_age, ok2 = QInputDialog.getInt(self, "Редактирование возраста", "Введите новый возраст:",
                                           value=int(child["age"]), min=1, max=18)
        if not ok2:
            return

        # Обновляем представление в списке
        self.children_widgets[idx]['name'] = new_name.strip()
        self.children_widgets[idx]['age'] = new_age
        self.children_list_widget.takeItem(idx)
        self.children_list_widget.insertItem(idx, f"{new_name.strip()} (Возраст: {new_age})")

        # Сохраняем изменения в базе данных
        self.save_child_edits(child["name"], new_name, new_age)

    def save_child_edits(self, old_name, new_name, new_age):
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("""
                            UPDATE Children
                            SET name=%s,
                                age=%s
                            WHERE name = %s
                              AND ID_Parent IN (SELECT ID_Parent
                                                FROM Parents
                                                WHERE login = %s);
                            """, (new_name, new_age, old_name, self.current_user))
                conn.commit()
                QMessageBox.information(self, "Успех", "Данные ребенка обновлены.")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить изменения:\n{e}")
        finally:
            conn.close()

    def create_tickets(self):
        if not self.selected_locations or not self.children_widgets:
            QMessageBox.warning(self, "Ошибка", "Добавьте хотя бы одну локацию и одного ребёнка!")
            return
        selected_date = self.date_edit.date().toString("yyyy-MM-dd")
        try:
            for loc in self.selected_locations:
                loc_id = loc["id_location"]
                for child in self.children_widgets:
                    print(f"Создается билет:"
                          f"пользователь={self.current_user},"
                          f"ребенок={child['name']},"
                          f"возраст={child['age']},"
                          f"локация={loc['name_location']},"
                          f" дата={selected_date}")
                    save_ticket(self.current_user, child["name"], child["age"], loc_id, selected_date)
            QMessageBox.information(self, "Успех", "Билеты успешно оформлены!")
            self.close()
            # Обновляем окно «Мои билеты» если оно открыто
            if self.parent_window:
                self.parent_window.show_my_tickets()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось оформить билеты:\n{e}")




# ----------------- RegistrationWindow -----------------
class RegistrationWindow(QWidget):
    def __init__(self, switch_to_login):
        super().__init__()
        self.switch_to_login = switch_to_login
        self.setWindowTitle("Регистрация — A4 Kids City")
        self.resize(400, 450)
        self.__init__ui()

    def __init__ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(15)

        logo = QLabel()
        pixmap = QPixmap("02083b0b-746a-430a-b7cf-0e950235229c.png")
        if not pixmap.isNull():
            pixmap = pixmap.scaled(220, 100, Qt.AspectRatioMode.KeepAspectRatio,
                                   Qt.TransformationMode.SmoothTransformation)
            logo.setPixmap(pixmap)
        else:
            logo.setText("A4 Kids City")
            logo.setFont(FONT_TITLE)
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(logo)

        title = QLabel("Создание нового аккаунта")
        title.setFont(FONT_TITLE)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Поля ФИО
        layout.addWidget(QLabel("Фамилия:"))
        self.last_name_input = QLineEdit()
        self.last_name_input.setPlaceholderText("Фамилия")
        style_input(self.last_name_input)
        layout.addWidget(self.last_name_input)

        layout.addWidget(QLabel("Имя:"))
        self.first_name_input = QLineEdit()
        self.first_name_input.setPlaceholderText("Имя")
        style_input(self.first_name_input)
        layout.addWidget(self.first_name_input)

        layout.addWidget(QLabel("Отчество:"))
        self.middle_name_input = QLineEdit()
        self.middle_name_input.setPlaceholderText("Отчество (если есть)")
        style_input(self.middle_name_input)
        layout.addWidget(self.middle_name_input)

        # Номер телефона
        layout.addWidget(QLabel("Номер телефона:"))
        self.phone_input = QLineEdit()
        self.phone_input.setPlaceholderText("Номер телефона (+7...)")
        style_input(self.phone_input)
        layout.addWidget(self.phone_input)

        layout.addWidget(QLabel("Придумайте логин:"))
        self.login_input = QLineEdit()
        self.login_input.setPlaceholderText("Введите логин")
        style_input(self.login_input)
        layout.addWidget(self.login_input)

        layout.addWidget(QLabel("Придумайте пароль:"))
        self.pass_input = QLineEdit()
        self.pass_input.setPlaceholderText("Введите пароль")
        self.pass_input.setEchoMode(QLineEdit.EchoMode.Password)
        style_input(self.pass_input)
        layout.addWidget(self.pass_input)

        # Кнопка "Показать пароль"
        self.show_password_btn = QPushButton("Показать пароль")
        self.show_password_btn.setFixedWidth(100)  # фиксируем ширину кнопки
        self.show_password_btn.clicked.connect(self.toggle_password_visibility)
        layout.addWidget(self.show_password_btn, alignment=Qt.AlignmentFlag.AlignRight)

        btn_register = QPushButton("Зарегистрироваться")
        style_button(btn_register)
        btn_register.clicked.connect(self.register)
        layout.addWidget(btn_register)

        btn_goto_login = QPushButton("Уже есть аккаунт? Войти")
        style_button(btn_goto_login)
        btn_goto_login.clicked.connect(self.switch_to_login_and_close)
        layout.addWidget(btn_goto_login)

        self.setLayout(layout)
        self.setStyleSheet(f"background-color:{BACKGROUND_COLOR}; color:{TEXT_COLOR};")

    def toggle_password_visibility(self):
        if self.pass_input.echoMode() == QLineEdit.EchoMode.Password:
            self.pass_input.setEchoMode(QLineEdit.EchoMode.Normal)  # показывать пароль
            self.show_password_btn.setText("Скрыть пароль")
        else:
            self.pass_input.setEchoMode(QLineEdit.EchoMode.Password)  # прятать пароль
            self.show_password_btn.setText("Показать пароль")

    def register(self):
        login = self.login_input.text().strip()
        password = self.pass_input.text().strip()
        first_name = self.first_name_input.text().strip()
        last_name = self.last_name_input.text().strip()
        middle_name = self.middle_name_input.text().strip()
        phone = self.phone_input.text().strip()

        if not login or not password or not first_name or not last_name:
            QMessageBox.warning(self, "Ошибка", "Заполните все обязательные поля!")
            return

        accounts = load_accounts()
        if login in accounts:
            QMessageBox.warning(self, "Ошибка", "Такой логин уже существует!")
            return

        save_account(login, password, first_name, last_name, middle_name, phone)
        QMessageBox.information(self, "Успех", "Аккаунт успешно создан!")
        self.hide()
        self.switch_to_login()

    def switch_to_login_and_close(self):
        self.close()
        self.switch_to_login()



# ----------------- LoginWindow -----------------
class LoginWindow(QWidget):
    def __init__(self, switch_to_main, switch_to_registration):
        super().__init__()
        self.switch_to_main = switch_to_main
        self.switch_to_registration = switch_to_registration
        self.setWindowTitle("Авторизация — A4 Kids City")
        self.resize(400, 450)
        self.__init__ui()

    def __init__ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(15)

        logo = QLabel()
        pixmap = QPixmap("02083b0b-746a-430a-b7cf-0e950235229c.png")
        if not pixmap.isNull():
            pixmap = pixmap.scaled(220, 100, Qt.AspectRatioMode.KeepAspectRatio,
                                   Qt.TransformationMode.SmoothTransformation)
            logo.setPixmap(pixmap)
        else:
            logo.setText("A4 Kids City")
            logo.setFont(FONT_TITLE)
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(logo)

        title = QLabel("Добро пожаловать в A4 Kids City")
        title.setFont(FONT_TITLE)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        layout.addWidget(QLabel("Логин:"))
        self.login_input = QLineEdit()
        self.login_input.setPlaceholderText("Введите логин")
        style_input(self.login_input)
        layout.addWidget(self.login_input)

        layout.addWidget(QLabel("Пароль:"))
        self.pass_input = QLineEdit()
        self.pass_input.setPlaceholderText("Введите пароль")
        self.pass_input.setEchoMode(QLineEdit.EchoMode.Password)
        style_input(self.pass_input)
        layout.addWidget(self.pass_input)

        # Небольшая горизонтальная линия для отделения кнопки от поля ввода
        separator_line = QFrame()
        separator_line.setFrameShape(QFrame.Shape.HLine)
        separator_line.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(separator_line)

        # Кнопка для отображения пароля
        self.show_password_btn = QPushButton("Показать пароль")
        self.show_password_btn.setFixedHeight(25)  # небольшая высота кнопки
        self.show_password_btn.clicked.connect(self.toggle_password_visibility)
        layout.addWidget(self.show_password_btn)

        btn_login = QPushButton("Войти")
        style_button(btn_login)
        btn_login.clicked.connect(self.login)
        layout.addWidget(btn_login)

        btn_register = QPushButton("Создать аккаунт")
        style_button(btn_register)
        btn_register.clicked.connect(self.switch_to_registration)
        layout.addWidget(btn_register)

        self.setLayout(layout)
        self.setStyleSheet(f"background-color:{BACKGROUND_COLOR}; color:{TEXT_COLOR};")

    def toggle_password_visibility(self):
        if self.pass_input.echoMode() == QLineEdit.EchoMode.Password:
            self.pass_input.setEchoMode(QLineEdit.EchoMode.Normal)  # Открыть пароль
            self.show_password_btn.setText("Скрыть пароль")
        else:
            self.pass_input.setEchoMode(QLineEdit.EchoMode.Password)  # Скрыть пароль
            self.show_password_btn.setText("Показать пароль")  # Звёздочки

    def login(self):
        login = self.login_input.text().strip()
        password = self.pass_input.text()

        if login == "admin" and password == "admin":
            self.admin_panel = AdminPanelWindow(self)
            self.admin_panel.show()
            self.close()
            return

        accounts = load_accounts()
        if login in accounts and accounts[login]["password"] == password:
            role = accounts[login].get("role", "user")
            QMessageBox.information(self, "Успех", "Вы вошли в систему")
            self.switch_to_main(login, role)
        else:
            QMessageBox.warning(self, "Ошибка", "Неверный логин или пароль")


# ----------------- TicketsViewerWindow -----------------
class TicketsViewerWindow(QWidget):
    def __init__(self, current_user, current_role):
        super().__init__()
        self.current_user = current_user
        self.current_role = current_role
        self.setWindowTitle("Мои билеты" if current_role != "admin" else "Все билеты")
        self.resize(700, 400)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.layout.setSpacing(10)

        self.table = QTableWidget()
        self.layout.addWidget(self.table)

        self.delete_button = QPushButton("Удалить выбранный билет")
        style_button(self.delete_button)
        self.delete_button.clicked.connect(self.delete_ticket)
        self.layout.addWidget(self.delete_button)

        self.setStyleSheet(f"background-color:{BACKGROUND_COLOR}; color:{TEXT_COLOR};")
        self.load_tickets()

    def load_tickets(self):
        if self.current_role == "admin":
            tickets = get_all_tickets()
        else:
            tickets = get_user_tickets(self.current_user)
        self.table.clear()
        if not tickets:
            self.table.setRowCount(0)
            self.table.setColumnCount(1)
            self.table.setHorizontalHeaderLabels(["Нет билетов"])
            return
        self.table.setRowCount(len(tickets))
        self.table.setColumnCount(len(tickets[0]))
        headers = ["ID", "Ребенок", "Возраст", "Локация", "Стоимость", "Родитель", "Логин", "Дата посещения"]
        self.table.setRowCount(len(tickets))
        self.table.setColumnCount(len(headers))
        self.table.setHorizontalHeaderLabels(headers)
        for row, ticket in enumerate(tickets):
            for col, val in enumerate(ticket):
                self.table.setItem(row, col, QTableWidgetItem(str(val)))

        self.table.resizeColumnsToContents()

    def delete_ticket(self):
        selected_row = self.table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "Ошибка", "Выберите билет для удаления")
            return
        ticket_id = self.table.item(selected_row, 0).text()
        confirm = QMessageBox.question(
            self,
            "Подтверждение",
            f"Удалить билет #{ticket_id}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if confirm != QMessageBox.StandardButton.Yes:
            return
        is_admin = (self.current_role == "admin")
        success = delete_ticket_by_id(ticket_id,  self.current_user, is_admin,)
        if success:
            QMessageBox.information(self, "Успех", "Билет удалён")
            self.load_tickets()
        else:
            QMessageBox.warning(self, "Ошибка", "Не удалось удалить билет")


# ----------------- EditLocationsWindow -----------------
class EditLocationsWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Редактирование локаций")
        self.resize(900, 450)
        self.locations = load_locations()
        self.__init__ui()

    def __init__ui(self):
        layout = QVBoxLayout()
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(
            ["Название", "Описание", "Возраст", "Стоимость", "Изображение", "Выбор файла"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.load_table_data()

        btn_add = QPushButton("Добавить локацию")
        btn_delete = QPushButton("Удалить выбранную")
        btn_save = QPushButton("Сохранить изменения")
        for btn in [btn_add, btn_delete, btn_save]: style_button(btn)

        btn_add.clicked.connect(self.add_row)
        btn_delete.clicked.connect(self.delete_selected)
        btn_save.clicked.connect(self.save_location)

        layout.addWidget(self.table)
        hbox = QHBoxLayout()
        hbox.addWidget(btn_add)
        hbox.addWidget(btn_delete)
        hbox.addWidget(btn_save)
        layout.addLayout(hbox)
        self.setLayout(layout)
        self.setStyleSheet(f"background-color:{BACKGROUND_COLOR}; color:{TEXT_COLOR};")


    def load_table_data(self):
        self.table.setRowCount(len(self.locations))
        for i, loc in enumerate(self.locations):
            for col, key in enumerate(["name_location", "description", "age_range", "cost", "image"]):
                self.table.setItem(i, col, QTableWidgetItem(str(loc.get(key, ""))))
            btn_browse = QPushButton("Выбрать файл")
            style_button(btn_browse)
            btn_browse.clicked.connect(lambda _, row=i: self.choose_file(row))
            self.table.setCellWidget(i, 5, btn_browse)

    def add_row(self):
        row = self.table.rowCount()
        self.table.insertRow(row)
        btn_browse = QPushButton("Выбрать файл")
        style_button(btn_browse)
        btn_browse.clicked.connect(lambda _, row=row: self.choose_file(row))
        self.table.setCellWidget(row, 5, btn_browse)

    def choose_file(self, row):
        file_path, _ = QFileDialog.getOpenFileName(self, "Выберите изображение", "",
                                                   "Изображения (*.png *.jpg *.jpeg *.bmp)")
        if file_path:
            self.table.setItem(row, 4, QTableWidgetItem(file_path))

    def delete_selected(self):
        row = self.table.currentRow()
        if row >= 0:
            self.table.removeRow(row)

    def save_location(self):
        locations = []
        for row in range(self.table.rowCount()):
            data = [self._get_text(row, i) for i in range(5)]
            if data[0].strip():
                locations.append({
                    "name_location": data[0],
                    "description": data[1],
                    "age_range": data[2],
                    "cost": data[3],
                    "image": data[4]
                })
        save_locations(locations)
        QMessageBox.information(self, "Сохранено", "Изменения успешно сохранены!")

    def _get_text(self, row, col):
        item = self.table.item(row, col)
        return item.text() if item else ""




# ----------------- MainWindow -----------------
class MainWindow(QWidget):
    def __init__(self, current_user, current_role, go_to_login):
        super().__init__()
        self.current_user = current_user
        self.current_role = current_role
        self.user_role = current_role
        self.go_to_login = go_to_login
        self.ticket_form_window=None
        self.ticket_viewer_window=None
        self.setWindowTitle("A4 Kids City")
        self.resize(850, 600)
        self.locations = load_locations()
        self.__init__ui(current_role)
        if self.user_role == "admin":
            self.admin_panel = AdminPanelWindow()
            self.setCentralWidget(self.admin_panel)
            self.setWindowTitle("Админ-панель — A4 Kids City")
            self.resize(1000, 600)
        else:
            # Тут будет обычный интерфейс для обычного пользователя
            self.setWindowTitle("A4 Kids City")
            # self.setup_user_ui()

    def __init__ui(self, current_role):
        self.layout = QVBoxLayout()

        filter_layout = QHBoxLayout()
        filter_label = QLabel("Фильтр по возрасту:")
        filter_label.setFont(FONT_TEXT)
        self.age_filter = QComboBox()
        style_input(self.age_filter)
        self.age_filter.addItems(["Все", "3+", "4+", "5+", "6+", "7+", "8+"])
        self.age_filter.currentIndexChanged.connect(self.update_location_display)
        filter_layout.addWidget(filter_label)
        filter_layout.addWidget(self.age_filter)
        filter_layout.addStretch()
        self.layout.addLayout(filter_layout)

        self.book_ticket_button = QPushButton("Оформить билет")
        style_button(self.book_ticket_button)
        self.book_ticket_button.clicked.connect(self.open_ticket_window)
        self.layout.addWidget(self.book_ticket_button)

        self.view_tickets_button = QPushButton("Мои билеты" if current_role != "admin" else "Все билеты")
        style_button(self.view_tickets_button)
        self.view_tickets_button.clicked.connect(self.show_my_tickets)
        self.layout.addWidget(self.view_tickets_button)

        self.scroll_area = QScrollArea()
        self.locations_widget = QWidget()
        self.locations_layout = QVBoxLayout()
        self.locations_widget.setLayout(self.locations_layout)
        self.scroll_area.setWidget(self.locations_widget)
        self.scroll_area.setWidgetResizable(True)
        self.layout.addWidget(self.scroll_area)


        if self.current_role == "admin":
            btn_admin = QPushButton("Админ-панель")
            style_button(btn_admin)
            btn_admin.clicked.connect(self.open_admin_panel)
            self.layout.addWidget(btn_admin)

        btn_logout = QPushButton("Выйти")
        style_button(btn_logout)
        btn_logout.clicked.connect(self.logout)
        self.layout.addWidget(btn_logout)

        self.setLayout(self.layout)
        self.update_location_display()
        style_main_window(self)

    def logout(self):
        self.close()
        self.go_to_login()

    def update_location_display(self):
        # Очистка предыдущих карточек
        for i in reversed(range(self.locations_layout.count())):
            widget = self.locations_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)

        filter_age = self.age_filter.currentText()
        for loc in self.locations:
            age = loc.get("age_range", "")
            if filter_age != "Все" and filter_age != age:
                continue

            card = QWidget()
            style_card(card)
            card_layout = QHBoxLayout()
            card_layout.setSpacing(15)
            card.setLayout(card_layout)

            # --- Картинка слева ---
            img_label = QLabel()
            img_label.setFixedSize(150, 120)
            if loc.get("image") and os.path.exists(loc["image"]):
                pix = QPixmap(loc["image"]).scaled(150, 120, Qt.AspectRatioMode.KeepAspectRatio,
                                                   Qt.TransformationMode.SmoothTransformation)
                img_label.setPixmap(pix)
                img_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            else:
                img_label.setText("(нет изображения)")
                img_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            card_layout.addWidget(img_label)

            # --- Описание справа ---
            desc_layout = QVBoxLayout()
            name_label = QLabel(f"<b style='font-size:14pt;color:#FF5722'>{loc.get('name_location', '')}</b>")
            desc_label = QLabel(f"<span style='font-size:12pt;color:#212121'>{loc.get('description', '')}</span>")
            age_label = QLabel(f"<span style='font-size:11pt;color:#00796B'>Возраст: {age}</span>")
            cost_label = QLabel(f"<span style='font-size:12pt;color:#000000'>Стоимость: {loc.get('cost', '')}</span>")

            for lbl in [name_label, desc_label, age_label, cost_label]:
                lbl.setWordWrap(True)
                lbl.setFont(FONT_TEXT)

            desc_layout.addWidget(name_label)
            desc_layout.addWidget(desc_label)
            desc_layout.addWidget(age_label)
            desc_layout.addWidget(cost_label)
            desc_layout.addStretch()

            card_layout.addLayout(desc_layout)
            self.locations_layout.addWidget(card)

        self.locations_layout.addStretch()

    def open_ticket_window(self):
        self.ticket_form_window = TicketWindow(self.current_user, self.current_role, parent=self)
        self.ticket_form_window.show()

    def open_tickets_viewer(self):
        if self.ticket_viewer_window is None:
            self.ticket_viewer_window = TicketsViewerWindow(self.current_user, self.current_role)
            self.ticket_viewer_window.show()
            self.ticket_viewer_window.raise_()
            self.ticket_viewer_window.activateWindow()

    def show_my_tickets(self):
        # Открываем или обновляем окно билетов
        if getattr(self, "tickets_window", None):
            self.ticket_viewer_window.load_tickets()
            self.ticket_viewer_window.show()
            self.ticket_viewer_window.raise_()
            self.ticket_viewer_window.activateWindow()
        else:
            self.ticket_viewer_window = TicketsViewerWindow(self.current_user, self.current_role)
            self.ticket_viewer_window.show()

    def open_admin_panel(self):
        self.admin_window = AdminPanelWindow( )
        self.admin_window.show()
    def open_edit_window(self):
        if self.current_role == "admin":
            self.edit_window = EditLocationsWindow()
            self.edit_window.show()

class AdminPanelWindow(QWidget):
    def __init__(self,login_window):
        super().__init__()
        self.login_window = login_window
        self.setWindowTitle("Админ-панель — A4 Kids City")
        self.resize(1000, 600)
        self.tabs = QTabWidget()
        layout = QVBoxLayout()
        layout.addWidget(self.tabs)
        self.setLayout(layout)

        # Вкладки
        self.init_parents_tab()
        self.init_children_tab()
        self.init_locations_tab()
        self.init_tickets_tab()
        self.init_preferences_tab()

        self.button_exit = QPushButton("Выход")
        style_button(self.button_exit)
        self.button_exit.clicked.connect(self.logout)
        layout.addWidget(self.button_exit)


    def logout(self):
        # Закрываем административную панель и возвращаемся к окну авторизации
        self.close()
        self.login_window.show()

    # ---------- РОДИТЕЛИ ----------
    def init_parents_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        self.parents_table = QTableWidget()
        layout.addWidget(self.parents_table)

        btn_refresh = QPushButton("Обновить")
        btn_add = QPushButton("Добавить родителя")
        btn_edit = QPushButton("Редактировать выбранного")
        btn_delete = QPushButton("Удалить выбранного")

        for b in (btn_refresh, btn_add, btn_edit, btn_delete):
            style_button(b)

        btn_refresh.clicked.connect(self.load_parents)
        btn_add.clicked.connect(self.add_parent)
        btn_edit.clicked.connect(self.edit_selected_parent)
        btn_delete.clicked.connect(self.delete_parent)

        hbox = QHBoxLayout()
        hbox.addWidget(btn_refresh)
        hbox.addWidget(btn_add)
        hbox.addWidget(btn_edit)
        hbox.addWidget(btn_delete)
        layout.addLayout(hbox)

        self.tabs.addTab(widget, "Родители")
        self.load_parents()

    def load_parents(self):
        conn = get_connection()
        with conn.cursor() as cur:
            cur.execute("""
                        SELECT id_parent, last_name, first_name, middle_name, phone, login, password
                        FROM parents
                        ORDER BY id_parent;
                        """)
            rows = cur.fetchall()
        conn.close()

        self.parents_table.setColumnCount(7)
        self.parents_table.setHorizontalHeaderLabels(
            ["ID", "Фамилия", "Имя", "Отчество", "Телефон", "Логин", "Пароль"]
        )
        self.parents_table.setRowCount(len(rows))

        for i, row in enumerate(rows):
            for j, val in enumerate(row):
                item = QTableWidgetItem(str(val) if val is not None else "")
                # Скрываем пароль звёздочками
                if j == 6:  # Индекс столбца пароля
                    item = QTableWidgetItem("*" * len(val))  # Заменяем символы на "*"
                if j == 0:  # ID только для чтения
                    item.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
                self.parents_table.setItem(i, j, item)

        self.parents_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

    def edit_selected_parent(self):
        row = self.parents_table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Ошибка", "Выберите родителя для редактирования!")
            return

        parent_id = int(self.parents_table.item(row, 0).text())

        # получаем оригинальные данные из базы данных
        conn = get_connection()
        with conn.cursor() as cur:
            cur.execute("""
                        SELECT id_parent, last_name, first_name, middle_name, phone, login, password
                        FROM parents
                        WHERE id_parent = %s;
                        """, (parent_id,))
            row = cur.fetchone()
        conn.close()

        if row is None:
            QMessageBox.warning(self, "Ошибка", "Родитель не найден!")
            return

        # получаем реальные данные
        parent_id, last_name, first_name, middle_name, phone, login, password = row

        dlg = QDialog(self)
        dlg.setWindowTitle(f"Редактирование родителя #{parent_id}")
        form = QFormLayout(dlg)

        field_last_name = QLineEdit(last_name)
        field_first_name = QLineEdit(first_name)
        field_middle_name = QLineEdit(middle_name)
        field_phone = QLineEdit(phone)
        field_login = QLineEdit(login)
        field_password = QLineEdit(password)  # передаём РЕАЛЬНЫЙ пароль из базы данных
        field_password.setEchoMode(QLineEdit.EchoMode.Normal)  # отображаем его в открытом виде

        form.addRow("Фамилия:", field_last_name)
        form.addRow("Имя:", field_first_name)
        form.addRow("Отчество:", field_middle_name)
        form.addRow("Телефон:", field_phone)
        form.addRow("Логин:", field_login)
        form.addRow("Пароль:", field_password)

        btn_save = QPushButton("Сохранить")
        btn_cancel = QPushButton("Отмена")
        style_button(btn_save)
        style_button(btn_cancel)

        hbox = QHBoxLayout()
        hbox.addWidget(btn_save)
        hbox.addWidget(btn_cancel)
        form.addRow(hbox)

        btn_cancel.clicked.connect(dlg.reject)
        btn_save.clicked.connect(lambda: self.save_parent_changes(
            dlg, parent_id, field_last_name, field_first_name, field_middle_name, field_phone, field_login,
            field_password
        ))

        dlg.exec()

    def save_parent_changes(self, dlg, parent_id, field_last_name, field_first_name, field_middle_name, field_phone,
                            field_login, field_password):
        last_name = field_last_name.text().strip()
        first_name = field_first_name.text().strip()
        middle_name = field_middle_name.text().strip()
        phone = field_phone.text().strip()
        login = field_login.text().strip()
        password = field_password.text().strip()

        if not last_name or not first_name or not login or not password:
            QMessageBox.warning(self, "Ошибка", "Фамилия, имя, логин и пароль обязательны!")
            return

        try:
            conn = get_connection()
            with conn.cursor() as cur:
                cur.execute("""
                        UPDATE parents
                        SET last_name   = %s,
                            first_name  = %s,
                            middle_name = %s,
                            phone       = %s,
                            login       = %s,
                            password    = %s
                        WHERE id_parent = %s;
                        """, (last_name, first_name, middle_name, phone, login, password, parent_id))
            conn.commit()
            conn.close()

            QMessageBox.information(self, "Успешно", "Изменения сохранены!")
            dlg.accept()
            self.load_parents()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить изменения:\n{e}")

    def add_parent(self):
        dlg = QDialog(self)
        dlg.setWindowTitle("Добавить родителя")
        form = QFormLayout(dlg)

        field_last_name = QLineEdit()
        field_first_name = QLineEdit()
        field_middle_name = QLineEdit()
        field_phone = QLineEdit()
        field_login = QLineEdit()
        field_password = QLineEdit()
        field_password.setEchoMode(QLineEdit.Password)

        form.addRow("Фамилия:", field_last_name)
        form.addRow("Имя:", field_first_name)
        form.addRow("Отчество:", field_middle_name)
        form.addRow("Телефон:", field_phone)
        form.addRow("Логин:", field_login)
        form.addRow("Пароль:", field_password)

        btn_save = QPushButton("Добавить")
        btn_cancel = QPushButton("Отмена")
        style_button(btn_save)
        style_button(btn_cancel)

        hbox = QHBoxLayout()
        hbox.addWidget(btn_save)
        hbox.addWidget(btn_cancel)
        form.addRow(hbox)

        btn_cancel.clicked.connect(dlg.reject)
        btn_save.clicked.connect(lambda: self.insert_new_parent(
            dlg, field_last_name, field_first_name, field_middle_name, field_phone, field_login, field_password
        ))

        dlg.exec()

    def insert_new_parent(self, dlg, field_last_name, field_first_name, field_middle_name, field_phone, field_login,
                          field_password):
        last_name = field_last_name.text().strip()
        first_name = field_first_name.text().strip()
        middle_name = field_middle_name.text().strip()
        phone = field_phone.text().strip()
        login = field_login.text().strip()
        password = field_password.text().strip()

        if not last_name or not first_name or not login or not password:
            QMessageBox.warning(dlg, "Ошибка", "Фамилия, имя, логин и пароль обязательны!")
            return

        try:
            conn = get_connection()
            with conn.cursor() as cur:
                cur.execute("""
                            INSERT INTO parents (last_name, first_name, middle_name, phone, login, password)
                            VALUES (%s, %s, %s, %s, %s, %s);
                            """, (last_name, first_name, middle_name, phone, login, password))
            conn.commit()
            conn.close()

            QMessageBox.information(dlg, "Успешно", "Родитель добавлен!")
            dlg.accept()
            self.load_parents()
        except Exception as e:
            QMessageBox.critical(dlg, "Ошибка", f"Не удалось добавить родителя:\n{e}")

    def delete_parent(self):
        """Удаление выбранного родителя"""
        row = self.parents_table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Ошибка", "Выберите родителя для удаления!")
            return

        parent_id = int(self.parents_table.item(row, 0).text())
        confirm = QMessageBox.question(
            self, "Подтверждение",
            f"Удалить родителя с ID {parent_id}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if confirm != QMessageBox.StandardButton.Yes:
            return

        try:
            conn = get_connection()
            with conn.cursor() as cur:
                cur.execute("DELETE FROM parents WHERE id_parent = %s;", (parent_id,))
            conn.commit()
            conn.close()
            QMessageBox.information(self, "Успешно", "Родитель удалён!")
            self.load_parents()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось удалить родителя:\n{e}")

    # ---------- ДЕТИ ----------

    def init_children_tab(self):
        """Инициализация вкладки детей"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        self.children_table = QTableWidget()
        layout.addWidget(self.children_table)

        # --- Кнопки и фильтр по родителям ---
        buttons_and_filters_layout = QHBoxLayout()

        # Фильтр по родителям
        self.parent_combo = QComboBox()
        style_input(self.parent_combo)
        self.parent_combo.currentTextChanged.connect(self.filter_children_by_parent)
        buttons_and_filters_layout.addWidget(self.parent_combo)

        # Кнопки
        btn_add = QPushButton("Добавить ребёнка")
        btn_refresh = QPushButton("Обновить")
        style_button(btn_add)
        style_button(btn_refresh)
        btn_add.clicked.connect(self.add_child_dialog)
        btn_refresh.clicked.connect(self.load_children)
        buttons_and_filters_layout.addWidget(btn_add)
        buttons_and_filters_layout.addWidget(btn_refresh)

        layout.addLayout(buttons_and_filters_layout)

        hbox = QHBoxLayout()
        hbox.addWidget(btn_add)
        hbox.addWidget(btn_refresh)
        layout.addLayout(hbox)

        self.children_table.cellDoubleClicked.connect(self.edit_child_dialog)

        self.tabs.addTab(widget, "Дети")
        self.load_parents_into_combo()
        self.load_children()

    def load_parents_into_combo(self):
        """Загрузка списка родителей в QComboBox"""
        conn = get_connection()
        with conn.cursor() as cur:
            cur.execute("SELECT id_parent, last_name || ' ' || first_name FROM parents ORDER BY last_name, first_name;")
            parents = cur.fetchall()
        conn.close()

        self.parent_combo.clear()
        self.parent_combo.addItem("Все родители", None)  # Элемент для сброса фильтра
        for pid, fullname in parents:
            self.parent_combo.addItem(fullname, pid)

    def filter_children_by_parent(self):
        """Фильтрация детей по выбранному родителю"""
        selected_parent_id = self.parent_combo.currentData()
        if selected_parent_id is None:
            self.load_children()  # Показывать всех детей
        else:
            self.filter_children(selected_parent_id)

    def filter_children(self, parent_id):
        """Показывает только детей заданного родителя"""
        conn = get_connection()
        with conn.cursor() as cur:
            cur.execute("""
                        SELECT c.id_child, c.name, COALESCE(c.age, 0), p.last_name || ' ' || p.first_name
                        FROM children c
                                 JOIN parents p ON c.id_parent = p.id_parent
                        WHERE c.id_parent = %s
                        ORDER BY c.id_child;
                        """, (parent_id,))
            rows = cur.fetchall()
        conn.close()

        self.children_table.setColumnCount(4)
        self.children_table.setHorizontalHeaderLabels(["ID", "Имя", "Возраст", "Родитель"])
        self.children_table.setRowCount(len(rows))

        for i, row in enumerate(rows):
            for j, value in enumerate(row):
                self.children_table.setItem(i, j, QTableWidgetItem(str(value)))

        self.children_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

    def load_children(self):
        """Загружает детей с родителем"""
        conn = get_connection()
        with conn.cursor() as cur:
            cur.execute("""
                        SELECT c.id_child, c.name, COALESCE(c.age, 0), p.last_name ||' '||  p.first_name
                        FROM children c
                                 LEFT JOIN parents p ON c.id_parent = p.id_parent
                        ORDER BY c.id_child;
                        """)
            rows = cur.fetchall()
        conn.close()

        self.children_table.setColumnCount(4)
        self.children_table.setHorizontalHeaderLabels(["ID", "Имя", "Возраст", "Родитель"])
        self.children_table.setRowCount(len(rows))

        for i, row in enumerate(rows):
            for j, val in enumerate(row):
                self.children_table.setItem(i, j, QTableWidgetItem(str(val)))

        self.children_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

    def edit_child_dialog(self, row, col):
        """Редактирование выбранного ребёнка"""
        child_id = int(self.children_table.item(row, 0).text())

        conn = get_connection()
        with conn.cursor() as cur:
            # Получаем данные ребёнка
            cur.execute("SELECT name, COALESCE(age,0), id_parent FROM children WHERE id_child = %s;", (child_id,))
            child = cur.fetchone()
            if not child:
                QMessageBox.warning(self, "Ошибка", f"Ребёнок с ID {child_id} не найден.")
                return
            name, age, parent_id = child

            # Загружаем всех родителей
            cur.execute("SELECT id_parent, last_name || ' '||  first_name FROM parents ORDER BY last_name, first_name;")
            parents = cur.fetchall()
        conn.close()

        # Создаём окно
        dlg = QDialog(self)
        dlg.setWindowTitle(f"Редактирование ребёнка #{child_id}")
        form = QFormLayout(dlg)

        field_name = QLineEdit(name)
        field_age = QLineEdit(str(age))
        combo_parent = QComboBox()
        for pid, full_name in parents:
            combo_parent.addItem(full_name, pid)
        idx_parent = next((i for i, (pid, _) in enumerate(parents) if pid == parent_id), 0)
        combo_parent.setCurrentIndex(idx_parent)

        form.addRow("Имя:", field_name)
        form.addRow("Возраст:", field_age)
        form.addRow("Родитель:", combo_parent)

        btn_save = QPushButton("Сохранить")
        btn_cancel = QPushButton("Отмена")
        style_button(btn_save)
        style_button(btn_cancel)

        hbox = QHBoxLayout()
        hbox.addWidget(btn_save)
        hbox.addWidget(btn_cancel)
        form.addRow(hbox)

        btn_cancel.clicked.connect(dlg.reject)
        btn_save.clicked.connect(lambda: self.save_children_changes(child_id, field_name, field_age, combo_parent, dlg))

        dlg.exec()

    def add_child_dialog(self):
        """Добавление нового ребёнка"""
        dlg = QDialog(self)
        dlg.setWindowTitle("Добавить ребёнка")
        form = QFormLayout(dlg)

        field_name = QLineEdit()
        field_age = QLineEdit()

        conn = get_connection()
        with conn.cursor() as cur:
            cur.execute("SELECT id_parent, last_name || ' '||  first_name FROM parents ORDER BY last_name, first_name;")
            parents = cur.fetchall()
        conn.close()

        combo_parent = QComboBox()
        for pid, full_name in parents:
            combo_parent.addItem(full_name, pid)

        form.addRow("Имя:", field_name)
        form.addRow("Возраст:", field_age)
        form.addRow("Родитель:", combo_parent)

        btn_save = QPushButton("Добавить")
        btn_cancel = QPushButton("Отмена")
        style_button(btn_save)
        style_button(btn_cancel)

        hbox = QHBoxLayout()
        hbox.addWidget(btn_save)
        hbox.addWidget(btn_cancel)
        form.addRow(hbox)

        btn_cancel.clicked.connect(dlg.reject)
        btn_save.clicked.connect(lambda: self.insert_child(field_name, field_age, combo_parent, dlg))

        dlg.exec()


    def save_children_changes(self, child_id, field_name, field_age, combo_parent, dlg):
        """Сохраняет изменения ребёнка"""
        try:
            name = field_name.text()
            age = int(field_age.text())
            parent_id = combo_parent.currentData()

            conn = get_connection()
            with conn.cursor() as cur:
                cur.execute("""
                        UPDATE children
                        SET name      = %s,
                            age       = %s,
                            id_parent = %s
                        WHERE id_child = %s;
                        """, (name, age, parent_id, child_id))
            conn.commit()
            conn.close()

            QMessageBox.information(self, "Успешно", "Изменения сохранены.")
            dlg.accept()
            self.load_children()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить изменения:\n{e}")


    def insert_child(self, field_name, field_age, combo_parent, dlg):
        """Добавляет нового ребёнка"""
        try:
            name = field_name.text()
            age = int(field_age.text())
            parent_id = combo_parent.currentData()

            conn = get_connection()
            with conn.cursor() as cur:
                cur.execute("""
                        INSERT INTO children (name, age, id_parent)
                        VALUES (%s, %s, %s);
                        """, (name, age, parent_id))
            conn.commit()
            conn.close()

            QMessageBox.information(self, "Успешно", "Ребёнок добавлен.")
            dlg.accept()
            self.load_children()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось добавить ребёнка:\n{e}")

    # ---------- ЛОКАЦИИ ----------
    def init_locations_tab(self):
        self.locations_tab = EditLocationsWindow()
        self.tabs.addTab(self.locations_tab, "Локации")

    # ---------- БИЛЕТЫ ---------
    def init_tickets_tab(self):
            widget = QWidget()
            layout = QVBoxLayout(widget)
            self.tickets_table = QTableWidget()
            layout.addWidget(self.tickets_table)
            # --- Кнопки управления билетами ---
            buttons_layout = QHBoxLayout()

            btn_edit = QPushButton("Редактировать билет")
            style_button(btn_edit)
            btn_edit.clicked.connect(self.edit_selected_ticket)
            buttons_layout.addWidget(btn_edit)

            btn_delete = QPushButton("Удалить билет")
            style_button(btn_delete)
            btn_delete.clicked.connect(self.delete_selected_ticket)
            buttons_layout.addWidget(btn_delete)

            layout.addLayout(buttons_layout)

            self.tabs.addTab(widget, "Билеты")

            layout = QVBoxLayout()
            layout.setSpacing(10)
            self.tickets_table.setLayout(layout)

            # --- Блок фильтра по дате ---
            filter_layout = QHBoxLayout()
            filter_label = QLabel("Показать билеты на дату:")
            self.filter_date = QDateEdit()
            self.filter_date.setCalendarPopup(True)
            self.filter_date.setDisplayFormat("yyyy-MM-dd")
            self.filter_date.setDate(QDate.currentDate())
            style_input(self.filter_date)

            btn_filter = QPushButton("Показать")
            style_button(btn_filter)
            btn_filter.clicked.connect(self.filter_tickets_by_date)

            btn_clear_filter = QPushButton("Сбросить фильтр")
            style_button(btn_clear_filter)
            btn_clear_filter.clicked.connect(self.clear_date_filter)

            filter_layout.addWidget(filter_label)
            filter_layout.addWidget(self.filter_date)
            filter_layout.addWidget(btn_filter)
            filter_layout.addWidget(btn_clear_filter)
            layout.addLayout(filter_layout)

            # --- Таблица билетов ---
            self.tickets_table = QTableWidget()
            layout.addWidget(self.tickets_table)

            # --- Кнопки управления ---
            btn_refresh = QPushButton("Обновить список")
            style_button(btn_refresh)
            btn_refresh.clicked.connect(self.load_tickets)
            layout.addWidget(btn_refresh)

            self.load_tickets()

    def filter_tickets_by_date(self):
        """Фильтрует билеты по выбранной дате"""
        selected_date = self.filter_date.date().toPyDate()

        conn = get_connection()
        with conn.cursor() as cur:
            cur.execute("""
                        SELECT t.id_ticket,
                               c.name AS child_name,
                               c.age,
                               l.name_location,
                               p.last_name ||' ' || p.first_name AS parent_name, t.data AS visit_date
                        FROM tickets t
                                 JOIN children c ON c.id_child = t.id_child
                                 JOIN locations l ON l.id_location = t.id_location
                                 JOIN parents p ON p.id_parent = t.id_parent
                        WHERE t.data = %s
                        ORDER BY t.id_ticket;
                        """, (selected_date,))
            rows = cur.fetchall()
        conn.close()

        self.fill_tickets_table(rows)

    def clear_date_filter(self):
        """Сбрасывает фильтр и показывает все билеты"""
        self.load_tickets()

    def load_tickets(self):
        """Загружает билеты с JOIN-ами (имена вместо id)"""
        conn = get_connection()
        with conn.cursor() as cur:
            cur.execute("""
                        SELECT t.id_ticket,
                               c.name             AS child_name,
                               COALESCE(c.age, 0) AS age,
                               l.name_location    AS location_name,
                               p.last_name ||' '||  p.first_name AS parent_name,
                               t.data as visit_date
                        FROM tickets t
                                 JOIN children c ON c.id_child = t.id_child
                                 JOIN locations l ON l.id_location = t.id_location
                                 JOIN parents p ON p.id_parent = t.id_parent
                        ORDER BY t.id_ticket;
                        """)
            rows = cur.fetchall()
        conn.close()

        self.fill_tickets_table(rows)

    def fill_tickets_table(self, rows):
        """Обновляет содержимое таблицы билетов"""
        self.tickets_table.clear()
        self.tickets_table.setRowCount(len(rows))
        self.tickets_table.setColumnCount(6)
        self.tickets_table.setHorizontalHeaderLabels([
            "ID", "Имя ребёнка", "Возраст", "Локация", "Родитель", "Дата посещения"
        ])

        for i, row in enumerate(rows):
            for j, val in enumerate(row):
                self.tickets_table.setItem(i, j, QTableWidgetItem(str(val)))

        self.tickets_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

    def edit_selected_ticket(self):
        """Открывает окно редактирования выбранного билета"""
        selected_row = self.tickets_table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "Ошибка", "Выберите билет для редактирования.")
            return

        ticket_id = self.tickets_table.item(selected_row, 0).text()

        # Получаем детальную информацию из БД
        conn = get_connection()
        with conn.cursor() as cur:
            cur.execute("""
                        SELECT t.id_ticket,
                               c.id_child,
                               c.name,
                               c.age,
                               p.id_parent,
                               p.first_name ||' '||  p.last_name AS parent_name, l.id_location,
                               l.name_location,
                               t.data
                        FROM tickets t
                                 JOIN children c ON c.id_child = t.id_child
                                 JOIN parents p ON p.id_parent = t.id_parent
                                 JOIN locations l ON l.id_location = t.id_location
                        WHERE t.id_ticket = %s;
                        """, (ticket_id,))
            ticket = cur.fetchone()
        conn.close()

        if not ticket:
            QMessageBox.warning(self, "Ошибка", "Билет не найден.")
            return

        # --- Создаём диалог ---
        dlg = QDialog(self)
        dlg.setWindowTitle(f"Редактирование билета #{ticket_id}")
        form = QFormLayout(dlg)

        # Имя ребёнка
        field_name = QLineEdit(ticket[2])
        form.addRow(QLabel("Имя ребёнка:"), field_name)

        # Возраст
        field_age = QLineEdit(str(ticket[3]))
        form.addRow(QLabel("Возраст:"), field_age)

        # Родитель
        combo_parent = QComboBox()
        conn = get_connection()
        with conn.cursor() as cur:
            cur.execute("SELECT id_parent, first_name || ' '||  last_name FROM parents ORDER BY last_name;")
            parents = cur.fetchall()
        conn.close()
        for pid, pname in parents:
            combo_parent.addItem(pname, pid)
            if pid == ticket[4]:
                combo_parent.setCurrentIndex(combo_parent.count() - 1)
        form.addRow(QLabel("Родитель:"), combo_parent)

        # Локация
        combo_location = QComboBox()
        conn = get_connection()
        with conn.cursor() as cur:
            cur.execute("SELECT id_location, name_location FROM locations ORDER BY name_location;")
            locations = cur.fetchall()
        conn.close()
        for lid, lname in locations:
            combo_location.addItem(lname, lid)
            if lid == ticket[6]:
                combo_location.setCurrentIndex(combo_location.count() - 1)
        form.addRow(QLabel("Локация:"), combo_location)

        # Дата
        date_edit = QDateEdit()
        date_edit.setCalendarPopup(True)
        date_edit.setDisplayFormat("yyyy-MM-dd")
        if ticket[8]:
            qdate = QDate.fromString(str(ticket[8]), "yyyy-MM-dd")
            if qdate.isValid():
                date_edit.setDate(qdate)
            else:
                date_edit.setDate(QDate.currentDate())
        else:
            date_edit.setDate(QDate.currentDate())
        form.addRow(QLabel("Дата посещения:"), date_edit)

        # Кнопки
        btn_save = QPushButton("Сохранить изменения")
        style_button(btn_save)
        btn_save.clicked.connect(lambda: self.save_ticket_changes(
            dlg,
            ticket_id,
            ticket[1],
            field_name.text(),
            field_age.text(),
            combo_parent.currentData(),
            combo_location.currentData(),
            date_edit.date().toPyDate()
        ))
        form.addWidget(btn_save)

        dlg.exec()

    def save_ticket_changes(self, dlg, ticket_id, child_id, name, age, parent_id, location_id, visit_date):
        """Сохраняет изменения в таблицы children и tickets"""
        try:
            conn = get_connection()
            with conn.cursor() as cur:
                # Обновляем ребёнка
                cur.execute("""
                            UPDATE children
                            SET name = %s,
                                age        = %s
                            WHERE id_child = %s;
                            """, (name, age, child_id))

                # Обновляем билет
                cur.execute("""
                            UPDATE tickets
                            SET id_parent   = %s,
                                id_location = %s,
                                data = %s
                            WHERE id_ticket = %s;
                            """, (parent_id, location_id, visit_date, ticket_id))

            conn.commit()
            conn.close()

            QMessageBox.information(self, "Успешно", "Изменения сохранены.")
            dlg.accept()
            self.load_tickets()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить изменения:\n{e}")

    def delete_selected_ticket(self):
        """Удаляет выбранный билет"""
        selected_row = self.tickets_table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "Ошибка", "Выберите билет для удаления.")
            return

        ticket_id = self.tickets_table.item(selected_row, 0).text()
        confirm = QMessageBox.question(
            self,
            "Подтверждение удаления",
            f"Удалить билет #{ticket_id}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if confirm != QMessageBox.StandardButton.Yes:
            return

        try:
            conn = get_connection()
            with conn.cursor() as cur:
                cur.execute("DELETE FROM tickets WHERE id_ticket = %s;", (ticket_id,))
            conn.commit()
            conn.close()

            QMessageBox.information(self, "Успех", f"Билет #{ticket_id} удалён.")
            self.load_tickets()

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось удалить билет:\n{e}")

    # ---------- ПРЕДПОЧТЕНИЯ ----------
    def init_preferences_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        self.pref_table = QTableWidget()
        self.pref_table.setColumnCount(3)
        self.pref_table.setHorizontalHeaderLabels(["ID", "Локация", "Возраст"])
        self.pref_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        btn_add = QPushButton("Добавить")
        btn_del = QPushButton("Удалить выбранное")
        btn_refresh = QPushButton("Обновить")
        for b in [btn_add, btn_del, btn_refresh]:
            style_button(b)

        btn_add.clicked.connect(self.add_preference)
        btn_del.clicked.connect(self.delete_preference)
        btn_refresh.clicked.connect(self.load_preferences)
        self.pref_table.cellDoubleClicked.connect(self.edit_preference_dialog)

        hbox = QHBoxLayout()
        hbox.addWidget(btn_add)
        hbox.addWidget(btn_del)
        hbox.addWidget(btn_refresh)

        layout.addWidget(self.pref_table)
        layout.addLayout(hbox)
        self.tabs.addTab(widget, "Предпочтения")
        self.load_preferences()

    def load_preferences(self):
        """Загружает таблицу предпочтений с JOIN'ами"""
        conn = get_connection()
        with conn.cursor() as cur:
            cur.execute("""
                        SELECT pr.id_preference,
                               l.name_location,
                               p.age_preference
                        FROM preferences pr
                                 JOIN locations l ON pr.id_location = l.id_location
                                 JOIN preferences p ON pr.id_preference = p.id_preference
                        ORDER BY pr.age_preference;
                        """)
            rows = cur.fetchall()
        conn.close()

        self.pref_table.setRowCount(len(rows))
        for i, row in enumerate(rows):
            for j, val in enumerate(row):
                self.pref_table.setItem(i, j, QTableWidgetItem(str(val)))

    def add_preference(self):
        """Добавляет новое предпочтение, используя списки локаций и возрастных диапазонов"""
        try:
            conn = get_connection()
            with conn.cursor() as cur:
                # Загружаем локации
                cur.execute("SELECT id_location, name_location FROM locations ORDER BY id_location;")
                locs = [(row[0], row[1]) for row in cur.fetchall()]
            conn.close()

            if not locs:
                QMessageBox.warning(self, "Ошибка", "Нет доступных локаций.")
                return

            # Выбор локации
            loc_names = [f"{loc_id} — {name}" for loc_id, name in locs]
            loc_str, ok1 = QInputDialog.getItem(self, "Выбор локации", "Локация:", loc_names, 0, False)
            if not ok1:
                return
            id_location = int(loc_str.split(" — ")[0])

            # Загружаем возрастные диапазоны
            conn = get_connection()
            with conn.cursor() as cur:
                cur.execute("SELECT id_preference, age_preference FROM preferences ORDER BY id_preference;")
                ages = [(row[0], row[1]) for row in cur.fetchall()]
            conn.close()

            if not ages:
                QMessageBox.warning(self, "Ошибка", "Нет возрастных диапазонов в таблице preference.")
                return

            # Выбор возрастного диапазона
            age_names = [f"{aid} — {arange}" for aid, arange in ages]
            age_str, ok2 = QInputDialog.getItem(self, "Возраст", "Возрастной диапазон:", age_names, 0, False)
            if not ok2:
                return
            age_range = age_str.split(" — ")[1]

            # Добавляем запись (без указания id_preference!)
            conn = get_connection()
            with conn.cursor() as cur:
                cur.execute("""
                            INSERT INTO preferences (id_location, age_preference)
                            VALUES (%s, %s);
                            """, (id_location, age_range))
                conn.commit()
            conn.close()

            QMessageBox.information(self, "Успешно", "Предпочтение добавлено.")
            self.load_preferences()

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось добавить предпочтение:\n{e}")

    def edit_preference_dialog(self, row, col):
        """Окно редактирования предпочтения"""
        pref_id = int(self.pref_table.item(row, 0).text())

        # Загружаем текущее значение
        conn = get_connection()
        with conn.cursor() as cur:
            cur.execute("SELECT id_location, age_preference FROM preferences WHERE id_preference = %s;", (pref_id,))
            record = cur.fetchone()
            if not record:
                QMessageBox.warning(self, "Ошибка", f"Предпочтение с ID {pref_id} не найдено.")
                return
            id_location, age_pref = record

            # Список локаций
            cur.execute("SELECT id_location, name_location FROM locations ORDER BY name_location;")
            locs = [(r[0], r[1]) for r in cur.fetchall()]

            # Список возрастных диапазонов
            cur.execute("SELECT age_preference FROM preferences ORDER BY id_preference;")
            ages = [r[0] for r in cur.fetchall()]
        conn.close()

        # === Диалог ===
        dlg = QDialog(self)
        dlg.setWindowTitle(f"Редактирование предпочтения #{pref_id}")
        form = QFormLayout(dlg)

        combo_loc = QComboBox()
        for lid, lname in locs:
            combo_loc.addItem(lname, lid)
        idx_loc = next((i for i, (lid, _) in enumerate(locs) if lid == id_location), 0)
        combo_loc.setCurrentIndex(idx_loc)
        form.addRow("Локация:", combo_loc)

        combo_age = QComboBox()
        combo_age.addItems(ages)
        idx_age = next((i for i, a in enumerate(ages) if a == age_pref), 0)
        combo_age.setCurrentIndex(idx_age)
        form.addRow("Возраст:", combo_age)

        btn_save = QPushButton("Сохранить")
        btn_cancel = QPushButton("Отмена")
        style_button(btn_save)
        style_button(btn_cancel)
        hbox = QHBoxLayout()
        hbox.addWidget(btn_save)
        hbox.addWidget(btn_cancel)
        form.addRow(hbox)

        btn_cancel.clicked.connect(dlg.reject)
        btn_save.clicked.connect(lambda: self.save_preference_changes(
            pref_id,
            combo_loc.currentData(),
            combo_age.currentText(),
            dlg
        ))

        dlg.exec()

    def save_preference_changes(self, pref_id, id_location, age_pref, dlg):
        """Сохраняет изменения предпочтения"""
        try:
            conn = get_connection()
            with conn.cursor() as cur:
                print("Сохраняем:", pref_id, id_location, age_pref)
                cur.execute("""
                            UPDATE preferences
                            SET id_location    = %s,
                                age_preference = %s
                            WHERE id_preference = %s;
                            """, (id_location, age_pref, pref_id))
            conn.commit()
            conn.close()
            QMessageBox.information(self, "Успешно", "Изменения сохранены.")
            dlg.accept()
            self.load_preferences()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить изменения:\n{e}")

    def insert_preference(self, id_location, id_age_preference, dlg):
        """Сохраняет новое предпочтение в БД"""
        try:
            conn = get_connection()
            with conn.cursor() as cur:
                cur.execute("""
                            INSERT INTO preferences (id_location, id_preference)
                            VALUES (%s, %s);
                            """, (id_location, id_age_preference))
            conn.commit()
            conn.close()

            QMessageBox.information(self, "Успех", "Предпочтение добавлено!")
            dlg.accept()
            self.load_preferences()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось добавить предпочтение:\n{e}")

    def delete_preference(self):
        """Удаляет выбранную запись из таблицы предпочтений"""
        selected = self.pref_table.currentRow()
        if selected < 0:
            QMessageBox.warning(self, "Ошибка", "Выберите запись для удаления!")
            return

        pref_id = self.pref_table.item(selected, 0).text()
        confirm = QMessageBox.question(self, "Подтверждение", "Удалить выбранное предпочтение?",
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if confirm != QMessageBox.StandardButton.Yes:
            return

        try:
            conn = get_connection()
            with conn.cursor() as cur:
                cur.execute("DELETE FROM preferences WHERE id_preference = %s;", (pref_id,))
            conn.commit()
            conn.close()

            QMessageBox.information(self, "Удалено", "Предпочтение удалено!")
            self.load_preferences()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось удалить предпочтение:\n{e}")

# ----------------- Запуск приложения -----------------
class App:

    def excepthook(exctype, value, tb):
        print("ОШИБКА:")
        traceback.print_exception(exctype, value, tb)

    sys.excepthook = excepthook
    def __init__(self):
        self.qt_app = QApplication(sys.argv)
        self.login_window = None
        self.registration_window = None
        self.main_window = None
        self.show_login()

    def show_login(self):
        if self.main_window:
            self.main_window.close()
            self.main_window=None
        self.login_window = LoginWindow(self.show_main, self.show_registration)
        self.login_window.show()

    def show_registration(self):
        self.login_window.hide()
        self.registration_window = RegistrationWindow(self.show_login)
        self.registration_window.show()

    def show_main(self, login, role):
        if self.login_window:
            self.login_window.hide()
        if self.registration_window:
            self.registration_window.hide()
        self.main_window = MainWindow(login, role, self.show_login)
        self.main_window.show()


    def run(self):
        sys.exit(self.qt_app.exec())


if __name__ == "__main__":
    App().run()