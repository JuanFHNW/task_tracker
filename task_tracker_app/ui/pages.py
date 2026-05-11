"""NiceGUI pages for Task Tracker Pro - Developer 3"""

from datetime import datetime, date

from nicegui import ui

from task_tracker_app.models.enums import Priority, Interval
from task_tracker_app.services.task_service import is_overdue
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

            # small helper to safely parse various date widget values
            def parse_date(value):
                if not value:
                    return None
                # already a datetime
                if isinstance(value, datetime):
                    return value
                # date object
                if isinstance(value, date):
                    return datetime.combine(value, datetime.min.time())
                # string: try common formats
                if isinstance(value, str):
                    try:
                        return datetime.fromisoformat(value)
                    except Exception:
                        try:
                            return datetime.strptime(value, "%Y-%m-%d")
                        except Exception:
                            return None
                return None

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

                    ui.label("End Date")
                    end_date = ui.date()

                    interval_label.bind_visibility_from(recurring, "value")
                    interval_select.bind_visibility_from(recurring, "value")
                    end_date.bind_visibility_from(recurring, "value")

                    def save():
                        try:
                            first_due = parse_date(due_date.value)
                            end_dt = parse_date(end_date.value)

                            if first_due and first_due < datetime.utcnow():
                                ui.notify("Due date cannot be in the past", type="negative")
                                return
                            if end_dt and first_due and end_dt < first_due:
                                ui.notify("End date must be after the first due date", type="negative")
                                return

                            self.task.create_task(
                                description=desc.value or "Untitled Task",
                                priority=prio.value,
                                interval=interval_select.value if recurring.value else None,
                                end_date=end_dt if recurring.value else None,
                                due_date=first_due,
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

            def edit_task_modal(task_id: int):
                # Build an edit dialog pre-filled with the task master and latest instance
                bundle = self.task.get_task_with_history(task_id)
                master = bundle.get("task")
                instances = bundle.get("instances") or []
                latest = instances[-1] if instances else None

                with ui.dialog() as dialog, ui.card().classes("w-full max-w-md"):
                    ui.label("Edit Task").classes("text-h6")
                    desc = ui.input("Description").classes("w-full")
                    ui.label("Priority")
                    prio = ui.select({p.value: p.value for p in Priority}, value="MEDIUM")
                    recurring = ui.checkbox("Recurring Task")
                    interval_label = ui.label("Interval")
                    interval_select = ui.select({i.value: i.value for i in Interval})
                    ui.label("Due Date")
                    due_date = ui.date()

                    ui.label("End Date")
                    end_date = ui.date()

                    interval_label.bind_visibility_from(recurring, "value")
                    interval_select.bind_visibility_from(recurring, "value")
                    end_date.bind_visibility_from(recurring, "value")

                    # Prefill values from master/instance
                    if master:
                        desc.value = master.description
                        if master.priority:
                            prio.value = master.priority.value
                        if master.interval:
                            recurring.value = True
                            interval_select.value = master.interval.value
                        if master.end_date:
                            end_date.value = master.end_date.date()
                    if latest and latest.due_date:
                        due_date.value = latest.due_date.date()

                    def save_edit():
                        try:
                            first_due = parse_date(due_date.value)
                            end_dt = parse_date(end_date.value)

                            if first_due and first_due < datetime.utcnow():
                                ui.notify("Due date cannot be in the past", type="negative")
                                return
                            if end_dt and first_due and end_dt < first_due:
                                ui.notify("End date must be after the first due date", type="negative")
                                return

                            ok = self.task.update_task(
                                task_id,
                                description=desc.value or "Untitled Task",
                                priority=Priority(prio.value) if prio.value else None,
                                interval=Interval(interval_select.value) if recurring.value and interval_select.value else None,
                                end_date=end_dt if recurring.value else None,
                            )
                            if ok:
                                ui.notify("Task updated", type="positive")
                                dialog.close()
                                refresh_table()
                            else:
                                ui.notify("Update rejected", type="negative")
                        except Exception as ex:
                            ui.notify(str(ex), type="negative")

                    with ui.row().classes("gap-2 mt-4"):
                        ui.button("Cancel", on_click=dialog.close)
                        ui.button("Save", on_click=save_edit).props("color=primary")
                dialog.open()

            # ==================== DASHBOARD HERO ====================
            with ui.card().classes("w-full rounded-3xl p-6 mb-6 bg-gradient-to-r from-slate-900 via-slate-800 to-slate-700 text-white shadow-lg"):
                with ui.row().classes("w-full items-center justify-between gap-4"):
                    ui.label(f"Welcome, {username}").classes("text-3xl font-bold")
                    with ui.row().classes("gap-2"):
                        ui.button("➕ New Task", on_click=create_task_modal).props("color=primary")
                        ui.button("📊 Download Report", on_click=download_report).props("color=teal")
                        ui.button("Logout", on_click=lambda: (self.auth.logout(), ui.navigate.to("/"))).props("outline")

            # ==================== SUMMARY CARDS ====================
            with ui.row().classes("w-full gap-4 mb-6"):
                with ui.card().classes("flex-1 p-4 rounded-2xl shadow-sm"):
                    with ui.column().classes("w-full items-center justify-center gap-2"):
                        total_value = ui.label("0").classes("text-3xl font-bold")
                        ui.label("Total Tasks").classes("text-xs uppercase tracking-wider text-gray-500")
                with ui.card().classes("flex-1 p-4 rounded-2xl shadow-sm"):
                    with ui.column().classes("w-full items-center justify-center gap-2"):
                        active_value = ui.label("0").classes("text-3xl font-bold text-blue-600")
                        ui.label("Active").classes("text-xs uppercase tracking-wider text-gray-500")
                with ui.card().classes("flex-1 p-4 rounded-2xl shadow-sm"):
                    with ui.column().classes("w-full items-center justify-center gap-2"):
                        completed_value = ui.label("0").classes("text-3xl font-bold text-green-600")
                        ui.label("Completed").classes("text-xs uppercase tracking-wider text-gray-500")
                with ui.card().classes("flex-1 p-4 rounded-2xl shadow-sm"):
                    with ui.column().classes("w-full items-center justify-center gap-2"):
                        recurring_value = ui.label("0").classes("text-3xl font-bold text-violet-600")
                        ui.label("Recurring").classes("text-xs uppercase tracking-wider text-gray-500")

            with ui.card().classes("w-full rounded-3xl shadow-md border border-slate-200/70 p-0 overflow-hidden bg-white"):
                with ui.row().classes("w-full items-center justify-between px-6 pt-5 pb-4 border-b border-slate-100"):
                    ui.label("Task Board").classes("text-lg font-semibold tracking-wide text-slate-800")
                    ui.label("Filter and sort your workflow").classes("text-sm text-slate-500")

                with ui.row().classes("w-full items-end gap-3 px-6 py-4 flex-wrap"):
                    with ui.column().classes("gap-1 min-w-[11rem]"):
                        ui.label("Priority").classes("text-xs uppercase tracking-wider text-slate-500")
                        filter_priority = ui.select(
                            {"All": "All", **{p.value: p.value for p in Priority}},
                            value="All",
                        ).props("outlined dense").classes("w-full")

                    with ui.column().classes("gap-1 min-w-[11rem]"):
                        ui.label("Status").classes("text-xs uppercase tracking-wider text-slate-500")
                        filter_status = ui.select(
                            {"All": "All", "TODO": "TODO", "IN_PROGRESS": "IN_PROGRESS", "DONE": "DONE"},
                            value="All",
                        ).props("outlined dense").classes("w-full")

                    with ui.card().classes("rounded-2xl border border-slate-200 bg-slate-50/70 p-3 min-w-[20rem]"):
                        with ui.column().classes("gap-2"):
                            ui.label("Sort Group").classes("text-xs uppercase tracking-wider text-slate-500")
                            with ui.row().classes("items-end gap-2 flex-wrap"):
                                with ui.column().classes("gap-1 min-w-[12rem]"):
                                    ui.label("Sort by").classes("text-xs uppercase tracking-wider text-slate-500")
                                    sort_field = ui.select(
                                        {"due_date": "Due Date", "end_date": "End Date", "priority": "Priority", "interval": "Interval", "status": "Status"},
                                        value="due_date",
                                    ).props("outlined dense").classes("w-full")
                                with ui.column().classes("gap-1"):
                                    ui.label("Order").classes("text-xs uppercase tracking-wider text-slate-500")
                                    sort_order = ui.toggle(["Asc", "Desc"], value="Asc").props("dense")

                    def reset_filters():
                        filter_priority.value = "All"
                        filter_status.value = "All"
                        sort_field.value = "due_date"
                        sort_order.value = "Asc"
                        refresh_table()

                    ui.button("Reset", on_click=reset_filters).props("flat")

            def refresh_table():
                tasks = self.task.list_tasks()
                rows = []
                total_count = len(tasks)
                active_count = 0
                completed_count = 0
                recurring_count = 0
                for t in tasks:
                    history = self.task.get_task_with_history(t.id)
                    latest = history["instances"][-1] if history.get("instances") else None
                    if t.interval is not None:
                        recurring_count += 1
                    if latest and latest.status.value == "DONE":
                        completed_count += 1
                    else:
                        active_count += 1
                    rows.append({
                        "description": t.description,
                        "priority": t.priority.value,
                        "interval": t.interval.value if t.interval else "One-time",
                        "end_date": t.end_date.strftime("%Y-%m-%d") if t.end_date else "",
                        "due_date": latest.due_date.strftime("%Y-%m-%d") if latest and latest.due_date else "",
                        "status": latest.status.value if latest else "TODO",
                        "overdue": bool(latest and is_overdue(latest)),
                        "id": t.id,
                    })
                total_value.text = str(total_count)
                active_value.text = str(active_count)
                completed_value.text = str(completed_count)
                recurring_value.text = str(recurring_count)

                # Apply filters
                fp = filter_priority.value if hasattr(filter_priority, "value") else "All"
                fs = filter_status.value if hasattr(filter_status, "value") else "All"
                if fp and fp != "All":
                    rows = [r for r in rows if r.get("priority") == fp]
                if fs and fs != "All":
                    rows = [r for r in rows if r.get("status") == fs]

                # Apply sorting
                field = sort_field.value if hasattr(sort_field, "value") else "due_date"

                def sort_key(r):
                    v = r.get(field)
                    if field in ("due_date", "end_date"):
                        try:
                            return datetime.fromisoformat(v) if v else datetime.max
                        except Exception:
                            return datetime.max
                    if field == "priority":
                        order = {"LOW": 0, "MEDIUM": 1, "HIGH": 2}
                        return order.get(v, -1)
                    if field == "interval":
                        order = {"One-time": 0, "DAILY": 1, "WEEKLY": 2, "MONTHLY": 3, "YEARLY": 4}
                        return order.get(v, 0)
                    if field == "status":
                        order = {"TODO": 0, "IN_PROGRESS": 1, "DONE": 2}
                        return order.get(v, 0)
                    return v or ""

                rows.sort(key=sort_key, reverse=(sort_order.value == "Desc"))

                task_table.rows = rows

            # ==================== UI LAYOUT ====================
            columns = [
                {"name": "description", "label": "Description", "field": "description", "align": "left"},
                {"name": "priority", "label": "Priority", "field": "priority"},
                {"name": "interval", "label": "Interval", "field": "interval"},
                {"name": "end_date", "label": "End Date", "field": "end_date"},
                {"name": "due_date", "label": "Due Date", "field": "due_date"},
                {"name": "status", "label": "Status", "field": "status"},
                {"name": "actions", "label": "Actions", "field": "actions", "align": "center"},
            ]

            task_table = ui.table(columns=columns, rows=[], row_key="id").classes("w-full px-4 pb-4")
            task_table.props("flat bordered separator=horizontal")

            # Refresh rows when filter/sort field changes
            filter_priority.on_value_change(lambda _: refresh_table())
            filter_status.on_value_change(lambda _: refresh_table())
            sort_field.on_value_change(lambda _: refresh_table())
            sort_order.on_value_change(lambda _: refresh_table())

            refresh_table()

            task_table.add_slot("body-cell-status", '''
                <q-td :props="props">
                    <div class="row items-center q-gutter-x-xs">
                        <q-badge :color="props.row.status === 'DONE' ? 'green' : (props.row.status === 'IN_PROGRESS' ? 'blue' : 'grey')" class="text-white">
                            {{ props.row.status }}
                        </q-badge>
                        <q-badge v-if="props.row.overdue && props.row.status !== 'DONE'" color="red" class="text-white">
                            OVERDUE
                        </q-badge>
                    </div>
                </q-td>
            ''')

            task_table.add_slot("body-cell-description", '''
                <q-td :props="props">
                    <span :class="props.row.status === 'DONE' ? 'text-grey-6 line-through' : (props.row.overdue ? 'text-red-7 font-medium' : '')">
                        {{ props.row.description }}
                    </span>
                </q-td>
            ''')

            # Action buttons
            task_table.add_slot("body-cell-actions", '''
                <q-td :props="props">
                    <q-btn dense flat icon="edit" @click="$parent.$emit('edit', props.row.id)" title="Edit"/>
                    <q-btn v-if="props.row.status === 'TODO'" dense flat icon="play_arrow" @click="$parent.$emit('start', props.row.id)" title="Start"/>
                    <q-btn v-if="props.row.status !== 'DONE'" dense flat icon="check" color="green" @click="$parent.$emit('finish', props.row.id)" title="Finish"/>
                    <q-btn dense flat icon="delete" color="red" @click="$parent.$emit('delete', props.row.id)" title="Delete"/>
                </q-td>
            ''')

            task_table.on('start', lambda e: (self.task.mark_started(e.args), refresh_table(), ui.notify("Started")))
            task_table.on('finish', lambda e: (self.task.mark_completed(e.args), refresh_table(), ui.notify("Completed!")))
            task_table.on('delete', lambda e: (self.task.delete_task(e.args), refresh_table(), ui.notify("Archived")))
            task_table.on('edit', lambda e: edit_task_modal(e.args))

