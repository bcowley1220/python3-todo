import os
import json
from datetime import datetime, timedelta
from tkinter import Tk, Frame, Label, Button, Listbox, Entry, END, Scrollbar, StringVar

class ToDoApp:
    def __init__(self):
        self.todo_list = []
        self.archive_list = []
        self.history_stack = []
        self.redo_stack = []
        self.points = 0
        self.load_from_file()

        # Initialize GUI
        self.root = Tk()
        self.root.title("To-Do List")
        self.init_gui()
        self.refresh_view()
        self.show_notifications()

    def init_gui(self):
        # Frame for list display
        frame = Frame(self.root)
        frame.pack()

        scrollbar = Scrollbar(frame)
        scrollbar.pack(side="right", fill="y")

        self.task_listbox = Listbox(frame, width=60, height=20, yscrollcommand=scrollbar.set)
        self.task_listbox.pack(side="left", fill="y")
        scrollbar.config(command=self.task_listbox.yview)

        # Frame for controls
        controls = Frame(self.root)
        controls.pack()

        Button(controls, text="Add Task", command=self.add_task_prompt).grid(row=0, column=0)
        Button(controls, text="Mark Completed", command=self.mark_task_completed).grid(row=0, column=1)
        Button(controls, text="Remove Task", command=self.remove_task).grid(row=0, column=2)
        Button(controls, text="Undo", command=self.undo_action).grid(row=1, column=0)
        Button(controls, text="Redo", command=self.redo_action).grid(row=1, column=1)
        Button(controls, text="View Archive", command=self.view_archive).grid(row=1, column=2)
        Button(controls, text="Exit", command=self.exit_program).grid(row=2, column=1)

        # Points display
        self.points_var = StringVar()
        self.points_var.set(f"Points: {self.points}")
        Label(self.root, textvariable=self.points_var).pack()

    def refresh_view(self):
        self.task_listbox.delete(0, END)
        for task, priority, due_date, category, completed, recurrence, tags in self.todo_list:
            status = "✔" if completed else "✘"
            tags_text = f" [Tags: {', '.join(tags)}]" if tags else ""
            self.task_listbox.insert(END, f"{task} [Priority: {priority}] [Due: {due_date}] [Category: {category}] {status}{tags_text}")

    def add_task_prompt(self):
        new_task = self.simple_prompt("Enter task details:")
        if new_task:
            self.add_task(new_task)

    def simple_prompt(self, message):
        entry_win = Tk()
        entry_win.title(message)
        Label(entry_win, text=message).pack()
        entry = Entry(entry_win, width=50)
        entry.pack()

        def close_and_return():
            result = entry.get()
            entry_win.destroy()
            return result

        Button(entry_win, text="Submit", command=close_and_return).pack()
        entry_win.mainloop()
        return entry.get()

    def add_task(self, task):
        self.todo_list.append((task, "Medium", "No Due Date", "General", False, None, []))
        self.history_stack.append(("add", task))
        self.redo_stack.clear()
        self.refresh_view()

    def mark_task_completed(self):
        selection = self.task_listbox.curselection()
        if selection:
            index = selection[0]
            task = self.todo_list.pop(index)
            completed_task = task[:4] + (True,) + task[5:]
            self.archive_list.append(completed_task)
            self.history_stack.append(("complete", task))
            self.redo_stack.clear()
            self.points += 10
            self.points_var.set(f"Points: {self.points}")
            self.refresh_view()

    def remove_task(self):
        selection = self.task_listbox.curselection()
        if selection:
            index = selection[0]
            task = self.todo_list.pop(index)
            self.history_stack.append(("remove", task))
            self.redo_stack.clear()
            self.refresh_view()

    def undo_action(self):
        if not self.history_stack:
            return
        action, task = self.history_stack.pop()
        self.redo_stack.append((action, task))
        if action == "add":
            self.todo_list.remove(task)
        elif action == "remove":
            self.todo_list.append(task)
        elif action == "complete":
            self.archive_list.remove(task)
            self.todo_list.append(task)
        self.refresh_view()

    def redo_action(self):
        if not self.redo_stack:
            return
        action, task = self.redo_stack.pop()
        self.history_stack.append((action, task))
        if action == "add":
            self.todo_list.append(task)
        elif action == "remove":
            self.todo_list.remove(task)
        elif action == "complete":
            self.todo_list.remove(task)
            self.archive_list.append(task)
        self.refresh_view()

    def view_archive(self):
        archive_win = Tk()
        archive_win.title("Archived Tasks")
        listbox = Listbox(archive_win, width=60, height=20)
        listbox.pack()
        for task in self.archive_list:
            listbox.insert(END, task[0])
        Button(archive_win, text="Close", command=archive_win.destroy).pack()
        archive_win.mainloop()

    def show_notifications(self):
        overdue_tasks = [task[0] for task in self.todo_list if task[2] != "No Due Date" and datetime.strptime(task[2], "%Y-%m-%d").date() < datetime.now().date()]
        if overdue_tasks:
            print("\n⚠️ Overdue Tasks:")
            for task in overdue_tasks:
                print(f"- {task}")

    def exit_program(self):
        self.save_to_file()
        self.root.destroy()

    def save_to_file(self, filename="todo_list.json"):
        data = {"tasks": self.todo_list, "archive": self.archive_list, "points": self.points}
        with open(filename, "w") as file:
            json.dump(data, file)

    def load_from_file(self, filename="todo_list.json"):
        if os.path.exists(filename):
            with open(filename, "r") as file:
                data = json.load(file)
                self.todo_list = data.get("tasks", [])
                self.archive_list = data.get("archive", [])
                self.points = data.get("points", 0)

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = ToDoApp()
    app.run()
