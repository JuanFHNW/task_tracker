"""NiceGUI pages for Task Tracker Pro - Developer 3"""

from datetime import datetime

from nicegui import ui

from task_tracker_app.models.enums import Priority, Interval
from .controllers import AuthController, TaskController


class Pages:
    """Registers all application pages."""

    def __init__(self, auth_controller: AuthController, task_controller: TaskController) -> None:
        self.auth = auth_controller
        self.task = task_controller

    def register(self) -> None:
        """Register all UI routes."""

        @ui.page("/")
        def login_page():
            if self.auth.is_authenticated():
                ui.navigate.to("/dashboard")
                return

            ui.markdown("# 🔐 Task Tracker Pro")
            with ui.card().classes("w-full max-w-md mx-auto mt-20 p-8"):
                username = ui.input("Username").classes("w-full")
                password = ui.input("Password", password=True).classes("w-full")

                def do_login():
                    success = self.auth.login(username.value, password.value)
                    if success:
                        ui.notify("Login successful!", type="positive")
                        ui.navigate.to("/dashboard")
                    else:
                        ui.notify("Invalid credentials", type="negative")

                ui.button("Login", on_click=do_login).classes("w-full mt-4")
                ui.button("Register", on_click=lambda: ui.navigate.to("/register")).classes("w-full mt-2")

        @ui.page("/register")
        def register_page():
            ui.markdown("# 📝 Create Account")
            with ui.card().classes("w-full max-w-md mx-auto mt-20 p-8"):
                username = ui.input("Username").classes("w-full")
                password = ui.input("Password", password=True).classes("w-full")

                def do_register():
                    try:
                        user = self.auth.register(username.value, password.value)
                        ui.notify(f"Account '{user.username}' created!", type="positive")
                        ui.navigate.to("/")
                    except Exception as e:
                        ui.notify(str(e), type="negative")

                ui.button("Register", on_click=do_register).classes("w-full mt-4")

        # ==================== DASHBOARD ====================
        @ui.page("/dashboard")
        def dashboard_page():
            if not self.auth.is_authenticated():
                ui.navigate.to("/")
                return

            username = self.auth.get_current_username()
            ui.markdown(f"# 👋 Welcome, **{username}**!")

            # ==================== MODALS DEFINED FIRST ====================
            def create_task_modal():
                with ui.dialog() as dialog, ui.card().classes("w-full max-w-md"):
                    ui.label("New Task").classes("text-h6")
                    desc = ui.input("Description").classes("w-full")
                    ui.label("Priority")
                    prio = ui.select({p.value: p.value for p in Priority}, value="MEDIUM")
                    recurring = ui.checkbox("Recurring Task")
                    interval_label = ui.label("Interval")
                    interval_select = ui.select({i.value: i.value for i in Interval})
                    ui.label("Due Date")
                    due_date = ui.date()

                    interval_label.bind_visibility_from(recurring, "value")
                    interval_select.bind_visibility_from(recurring, "value")

                    def save():
                        try:
                            self.task.create_task(
                                description=desc.value or "Untitled Task",
                                priority=prio.value,
                                interval=interval_select.value if recurring.value else None,
                                due_date=datetime.fromisoformat(due_date.value) if due_date.value else None,
                            )
                            ui.notify("Task created successfully!", type="positive")
                            dialog.close()
                            refresh_table()
                        except Exception as ex:
                            ui.notify(str(ex), type="negative")

                    with ui.row().classes("gap-2 mt-4"):
                        ui.button("Cancel", on_click=dialog.close)
                        ui.button("Save", on_click=save).props("color=primary")
                dialog.open()

            def download_report():
                try:
                    data, filename = self.task.generate_report()
                    ui.download(data, filename)
                    ui.notify(f"Downloaded {filename}", type="positive")
                except Exception as e:
                    ui.notify(str(e), type="negative")

            def refresh_table():
                tasks = self.task.list_tasks()
                rows = []
                for t in tasks:
                    history = self.task.get_task_with_history(t.id)
                    latest = history["instances"][-1] if history.get("instances") else None
                    rows.append({
                        "id": t.id,
                        "description": t.description,
                        "priority": t.priority.value,
                        "interval": t.interval.value if t.interval else "One-time",
                        "due_date": latest.due_date.strftime("%Y-%m-%d") if latest and latest.due_date else "",
                        "status": latest.status.value if latest else "TODO",
                    })
                task_table.rows = rows

            # ==================== UI LAYOUT ====================
            with ui.row().classes("w-full justify-between items-center my-4"):
                ui.button("➕ New Task", on_click=create_task_modal).props("color=primary")
                ui.button("📊 Download Report", on_click=download_report).props("color=teal")
                ui.button("Logout", on_click=lambda: (self.auth.logout(), ui.navigate.to("/"))).props("outline")

            columns = [
                {"name": "id", "label": "ID", "field": "id"},
                {"name": "description", "label": "Description", "field": "description", "align": "left"},
                {"name": "priority", "label": "Priority", "field": "priority"},
                {"name": "interval", "label": "Interval", "field": "interval"},
                {"name": "due_date", "label": "Due Date", "field": "due_date"},
                {"name": "status", "label": "Status", "field": "status"},
                {"name": "actions", "label": "Actions", "field": "actions", "align": "center"},
            ]

            task_table = ui.table(columns=columns, rows=[], row_key="id").classes("w-full")

            refresh_table()

            # Action buttons
            task_table.add_slot("body-cell-actions", '''
                <q-td :props="props">
                    <q-btn dense flat icon="play_arrow" @click="$parent.$emit('start', props.row.id)" title="Start"/>
                    <q-btn dense flat icon="check" color="green" @click="$parent.$emit('finish', props.row.id)" title="Finish"/>
                    <q-btn dense flat icon="delete" color="red" @click="$parent.$emit('delete', props.row.id)" title="Delete"/>
                </q-td>
            ''')

            task_table.on('start', lambda e: (self.task.mark_started(e.args), refresh_table(), ui.notify("Started")))
            task_table.on('finish', lambda e: (self.task.mark_completed(e.args), refresh_table(), ui.notify("Completed!")))
            task_table.on('delete', lambda e: (self.task.delete_task(e.args), refresh_table(), ui.notify("Archived")))

