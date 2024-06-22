import sqlite3
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.properties import ObjectProperty, StringProperty
from kivy.uix.modalview import ModalView

DATABASE = 'tasks.db'

class EditTaskPopup(Popup):
    task_widget = ObjectProperty(None)

    def save_task(self):
        new_text = self.ids.edit_task_input.text
        if new_text:
            # Update task text in the widget
            self.task_widget.task_text = new_text
            # Update task in the database
            self.task_widget.update_task_in_db(new_text)
            self.dismiss()

class Task(BoxLayout):
    task_text = StringProperty("")
    task_id = StringProperty("")

    def __init__(self, text="", task_id="", **kwargs):
        super().__init__(**kwargs)
        self.task_text = text
        self.task_id = task_id

    def open_edit_popup(self):
        popup = EditTaskPopup(task_widget=self)
        popup.ids.edit_task_input.text = self.task_text
        popup.open()

    def remove_task(self):
        # Remove task from the database
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM tasks WHERE id = ?", (self.task_id,))
        conn.commit()
        conn.close()
        # Remove task from the UI
        self.parent.remove_widget(self)

    def update_task_in_db(self, new_text):
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute("UPDATE tasks SET text = ? WHERE id = ?", (new_text, self.task_id))
        conn.commit()
        conn.close()

class TaskList(BoxLayout):
    task_input = ObjectProperty()
    task_list_layout = ObjectProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.load_tasks_from_db()

    def load_tasks_from_db(self):
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute("SELECT id, text FROM tasks")
        tasks = cursor.fetchall()
        conn.close()

        for task_id, text in tasks:
            new_task = Task(text=text, task_id=str(task_id))
            self.task_list_layout.add_widget(new_task)

    def add_task(self):
        task_text = self.task_input.text
        if task_text:
            conn = sqlite3.connect(DATABASE)
            cursor = conn.cursor()
            cursor.execute("INSERT INTO tasks (text) VALUES (?)", (task_text,))
            task_id = cursor.lastrowid
            conn.commit()
            conn.close()
            # Add the task to the UI with the new ID
            new_task = Task(text=task_text, task_id=str(task_id))
            self.task_list_layout.add_widget(new_task)
            self.task_input.text = ''

class TaskListApp(App):
    def build(self):
        self.init_db()
        return TaskList()

    def init_db(self):
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                text TEXT NOT NULL
            )
        ''')
        conn.commit()
        conn.close()

if __name__ == "__main__":
    TaskListApp().run()
