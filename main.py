import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading

import database
import attendance_manager
import student_manager
import face_recognition_service
import export_manager
from config import APP_TITLE, WINDOW_SIZE
from utils import today, now_text, validate_student_form


class AttendanceApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.geometry(WINDOW_SIZE)
        self.minsize(1000, 650)

        self.configure(bg="#f4f6f8")
        self._build_style()
        self._build_layout()
        self.show_dashboard()

    def _build_style(self):
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("Treeview", rowheight=30, font=("Segoe UI", 10))
        style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))
        style.configure("TButton", font=("Segoe UI", 10), padding=8)
        style.configure("Title.TLabel", font=("Segoe UI", 20, "bold"))
        style.configure("Card.TFrame", background="white")

    def _build_layout(self):
        sidebar = tk.Frame(self, bg="#202832", width=210)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        tk.Label(
            sidebar, text="Face Attendance", bg="#202832", fg="white",
            font=("Segoe UI", 16, "bold")
        ).pack(pady=(30, 25))

        buttons = [
            ("Dashboard", self.show_dashboard),
            ("Register Student", self.show_register),
            ("Face Recognition", self.start_recognition),
            ("Attendance", self.show_attendance),
            ("Students", self.show_students),
            ("Export", self.export_dialog),
            ("About", self.show_about),
            ("Exit", self.destroy),
        ]
        for text, command in buttons:
            tk.Button(
                sidebar, text=text, command=command, anchor="w",
                bg="#202832", fg="white", activebackground="#34414f",
                activeforeground="white", relief="flat", bd=0,
                padx=22, pady=10, font=("Segoe UI", 10)
            ).pack(fill="x")

        self.content = tk.Frame(self, bg="#f4f6f8")
        self.content.pack(side="right", fill="both", expand=True)

    def clear_content(self):
        for widget in self.content.winfo_children():
            widget.destroy()

    def page_title(self, title, subtitle=""):
        tk.Label(
            self.content, text=title, bg="#f4f6f8", fg="#202832",
            font=("Segoe UI", 20, "bold")
        ).pack(anchor="w", padx=28, pady=(25, 3))
        if subtitle:
            tk.Label(
                self.content, text=subtitle, bg="#f4f6f8", fg="#66717d",
                font=("Segoe UI", 10)
            ).pack(anchor="w", padx=30, pady=(0, 18))

    def show_dashboard(self):
        self.clear_content()
        self.page_title("Dashboard", "Today's attendance overview")

        present = database.count_present(today())
        total = database.count_students()
        absent = max(total - present, 0)
        percentage = (present / total * 100) if total else 0

        cards = tk.Frame(self.content, bg="#f4f6f8")
        cards.pack(fill="x", padx=25)

        values = [
            ("Registered Students", total),
            ("Present Today", present),
            ("Absent Today", absent),
            ("Attendance", f"{percentage:.1f}%"),
        ]
        for label, value in values:
            card = tk.Frame(cards, bg="white", padx=22, pady=18)
            card.pack(side="left", fill="x", expand=True, padx=5)
            tk.Label(card, text=label, bg="white", fg="#66717d").pack(anchor="w")
            tk.Label(
                card, text=value, bg="white", fg="#202832",
                font=("Segoe UI", 22, "bold")
            ).pack(anchor="w", pady=(8, 0))

        info = tk.Frame(self.content, bg="white", padx=22, pady=18)
        info.pack(fill="both", expand=True, padx=30, pady=25)
        tk.Label(
            info, text="Quick Start", bg="white", fg="#202832",
            font=("Segoe UI", 14, "bold")
        ).pack(anchor="w")
        tk.Label(
            info,
            text="Register students first, capture one face per student, then start Face Recognition.",
            bg="white", fg="#66717d", wraplength=750, justify="left"
        ).pack(anchor="w", pady=12)

    def show_register(self, student_id_to_edit=None):
        self.clear_content()
        self.page_title("Register Student", "Enter student details and capture a clear face encoding.")

        frame = tk.Frame(self.content, bg="white", padx=28, pady=25)
        frame.pack(fill="x", padx=30)

        fields = [
            ("Student ID", "student_id"),
            ("Student Name", "name"),
            ("Department", "department"),
            ("Year", "year"),
            ("Email", "email"),
            ("Phone", "phone"),
        ]
        entries = {}
        for row, (label, key) in enumerate(fields):
            tk.Label(frame, text=label, bg="white", fg="#303943").grid(
                row=row, column=0, sticky="w", pady=7
            )
            entry = ttk.Entry(frame, width=45)
            entry.grid(row=row, column=1, sticky="w", padx=18, pady=7)
            entries[key] = entry

        if student_id_to_edit:
            student = database.get_student(student_id_to_edit)
            if not student:
                messagebox.showerror("Student", "Student not found.")
                return
            for key in entries:
                entries[key].insert(0, student[key])
            entries["student_id"].configure(state="disabled")

        status = tk.StringVar(value="No face captured yet.")

        def capture():
            try:
                encoding = face_recognition_service.capture_single_face()
                if encoding is None:
                    status.set("Face capture cancelled.")
                    return
                entries["_encoding"] = encoding
                status.set("Face captured successfully.")
            except Exception as exc:
                messagebox.showerror("Camera Error", str(exc))

        def save():
            student = {
                key: entries[key].get().strip()
                for key in ("student_id", "name", "department", "year", "email", "phone")
            }
            valid, error = validate_student_form(student)
            if not valid:
                messagebox.showwarning("Invalid Form", error)
                return

            encoding = entries.get("_encoding")
            if student_id_to_edit:
                try:
                    student_manager.update_student(student)
                    if encoding is not None:
                        student_manager.save_face_encoding(student["student_id"], encoding)
                    messagebox.showinfo("Saved", "Student details updated.")
                    self.show_students()
                except Exception as exc:
                    messagebox.showerror("Save Error", str(exc))
                return

            if encoding is None:
                messagebox.showwarning("Face Required", "Capture the student's face before saving.")
                return

            try:
                student_manager.add_student(student, encoding, now_text())
                messagebox.showinfo("Saved", "Student registered successfully.")
                self.show_dashboard()
            except Exception as exc:
                messagebox.showerror("Registration Error", str(exc))

        tk.Button(
            frame, text="Capture Face", command=capture, bg="#2d6cdf", fg="white",
            relief="flat", padx=15, pady=8
        ).grid(row=6, column=1, sticky="w", pady=(18, 5))

        tk.Label(
            frame, textvariable=status, bg="white", fg="#66717d"
        ).grid(row=7, column=1, sticky="w")

        tk.Button(
            frame, text="Save Student", command=save, bg="#218838", fg="white",
            relief="flat", padx=15, pady=8
        ).grid(row=8, column=1, sticky="w", pady=(18, 0))

    def start_recognition(self):
        def run():
            try:
                face_recognition_service.recognize_from_camera(
                    on_recognized=self._recognition_callback
                )
            except Exception as exc:
                self.after(0, lambda: messagebox.showerror("Recognition", str(exc)))

        threading.Thread(target=run, daemon=True).start()

    def _recognition_callback(self, student):
        success, message = attendance_manager.mark_attendance(student["student_id"])
        # The recognition loop is intentionally independent from Tkinter widgets.
        # This keeps the webcam window responsive and avoids cross-thread UI updates.

    def show_attendance(self):
        self.clear_content()
        self.page_title("Attendance", "Search and review recorded attendance.")

        controls = tk.Frame(self.content, bg="#f4f6f8")
        controls.pack(fill="x", padx=30, pady=(0, 10))

        search = ttk.Entry(controls, width=25)
        search.pack(side="left", padx=(0, 8))
        search.insert(0, "")

        date_entry = ttk.Entry(controls, width=15)
        date_entry.pack(side="left", padx=8)
        date_entry.insert(0, today())

        departments = ["All"] + database.get_departments()
        department = ttk.Combobox(controls, values=departments, width=18, state="readonly")
        department.set("All")
        department.pack(side="left", padx=8)

        table = self._make_table(
            ["Student ID", "Name", "Department", "Date", "Time", "Status"],
            [110, 180, 150, 110, 100, 100]
        )

        def refresh():
            for item in table.get_children():
                table.delete(item)
            date_value = date_entry.get().strip()
            rows = attendance_manager.get_attendance(
                date=date_value or None,
                department=department.get(),
                search_text=search.get().strip() or None,
            )
            for row in rows:
                table.insert("", "end", values=tuple(row))

        ttk.Button(controls, text="Refresh", command=refresh).pack(side="left", padx=8)
        ttk.Button(
            controls, text="View All",
            command=lambda: (date_entry.delete(0, "end"), refresh())
        ).pack(side="left")

        refresh()

    def show_students(self):
        self.clear_content()
        self.page_title("Students", "Manage registered student profiles and face encodings.")

        controls = tk.Frame(self.content, bg="#f4f6f8")
        controls.pack(fill="x", padx=30, pady=(0, 10))
        search = ttk.Entry(controls, width=35)
        search.pack(side="left")
        ttk.Button(controls, text="Search", command=lambda: refresh()).pack(side="left", padx=8)
        ttk.Button(controls, text="Add Student", command=self.show_register).pack(side="right")

        table = self._make_table(
            ["Student ID", "Name", "Department", "Year", "Email", "Phone", "Face"],
            [110, 180, 150, 70, 190, 120, 80]
        )

        def refresh():
            for item in table.get_children():
                table.delete(item)
            for row in database.get_all_students(search.get()):
                face_state = "Saved" if row["face_encoding"] else "Missing"
                table.insert(
                    "", "end",
                    values=(row["student_id"], row["name"], row["department"],
                            row["year"], row["email"], row["phone"], face_state)
                )

        def selected_id():
            selected = table.selection()
            if not selected:
                messagebox.showwarning("Student", "Select a student first.")
                return None
            return table.item(selected[0])["values"][0]

        def edit():
            student_id = selected_id()
            if student_id:
                self.show_register(student_id)

        def recapture():
            student_id = selected_id()
            if not student_id:
                return
            try:
                encoding = face_recognition_service.capture_single_face()
                if encoding is not None:
                    student_manager.save_face_encoding(student_id, encoding)
                    refresh()
                    messagebox.showinfo("Face", "Face encoding updated.")
            except Exception as exc:
                messagebox.showerror("Face Capture", str(exc))

        def remove_face():
            student_id = selected_id()
            if student_id and messagebox.askyesno(
                "Confirm", "Delete this student's stored face encoding?"
            ):
                student_manager.remove_face_encoding(student_id)
                refresh()

        def delete():
            student_id = selected_id()
            if not student_id:
                return
            if messagebox.askyesno(
                "Confirm Delete",
                "Delete this student? Existing attendance records prevent accidental removal."
            ):
                try:
                    database.delete_student(student_id)
                    refresh()
                except Exception as exc:
                    messagebox.showerror("Delete", str(exc))

        actions = tk.Frame(self.content, bg="#f4f6f8")
        actions.pack(fill="x", padx=30, pady=8)
        for text, command in (
            ("Edit", edit), ("Re-capture Face", recapture),
            ("Delete Face", remove_face), ("Delete Student", delete)
        ):
            ttk.Button(actions, text=text, command=command).pack(side="left", padx=(0, 7))

        refresh()

    def export_dialog(self):
        date = today()
        file_path = filedialog.asksaveasfilename(
            title="Export Attendance",
            initialfile=f"attendance_{date}.csv",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
        )
        if not file_path:
            return

        try:
            count = export_manager.export_attendance(file_path)
            messagebox.showinfo("Export Complete", f"Exported {count} attendance records.")
        except Exception as exc:
            messagebox.showerror("Export Error", str(exc))

    def show_about(self):
        self.clear_content()
        self.page_title("About")
        frame = tk.Frame(self.content, bg="white", padx=30, pady=30)
        frame.pack(fill="x", padx=30)
        text = (
            "Face Recognition Attendance System\n\n"
            "A local desktop attendance application built with Python, "
            "Tkinter, OpenCV, face_recognition and SQLite.\n\n"
            "Face encodings are stored locally. The application does not upload "
            "biometric data or continuously record webcam footage."
        )
        tk.Label(
            frame, text=text, bg="white", fg="#303943",
            justify="left", font=("Segoe UI", 11), wraplength=750
        ).pack(anchor="w")

    def _make_table(self, columns, widths):
        container = tk.Frame(self.content, bg="white")
        container.pack(fill="both", expand=True, padx=30, pady=5)

        table = ttk.Treeview(container, columns=columns, show="headings")
        for column, width in zip(columns, widths):
            table.heading(column, text=column)
            table.column(column, width=width, anchor="center")
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=table.yview)
        table.configure(yscrollcommand=scrollbar.set)
        table.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        return table


def main():
    try:
        database.initialize_database()
    except Exception as exc:
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("Database Error", str(exc))
        root.destroy()
        return

    app = AttendanceApp()
    app.mainloop()


if __name__ == "__main__":
    main()
