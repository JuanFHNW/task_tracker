# 🌐 Task Tracker Web Pro

![UI task_tracker](menu_task_tracker.png)

---

**Task Tracker Web Pro** is the full-stack evolution of our initial console-based application. Migrated for the **Advanced Programming** module, this version transforms a simple CLI into a modern, browser-based productivity suite. It leverages a professional software architecture featuring a dedicated frontend, backend, and persistent database layer.


---

## 🧐 Analysis & Context

### The Problem
Users often struggle to manage daily tasks because existing tools are either overly complex with overwhelming features or too simple, lacking secure data persistence. In the transition to advanced web applications, maintaining a clear separation of concerns between the user interface and the database becomes a critical challenge to ensure data integrity and security.

### Our Solution
**Task Tracker Web Pro** provides a professional three-tier web application that ensures scalability, privacy, and robust data management.

* **Integrated Web Interface:** Built with **NiceGUI**, the application runs as a thin client in the browser, while the UI state and components are managed securely as Python objects on the server.
* **Relational Persistence:** We have migrated from basic JSON storage to a robust **SQLite database**. Data is handled through an **Object-Relational Mapper (ORM)** to avoid direct SQL and ensure modularity.
* **Secure Access & Reporting:** The new version introduces a **Login System** for personalized task management and a **Reporting Module** to analyze productivity and download performance statistics.
* **Object-Oriented Architecture:** The backend utilizes modular Python units to organize business logic into self-contained, reusable components.
---

## 👥 User Stories
To ensure the application meets the needs of its end-users, the following requirements have been defined:

### 1. Secure Login
**As a user, I want to log in with my username and password so that I can securely view and manage my personal task list.**

- **Input:**
   * **Username:**
  <kbd>Username</kbd> : pro_user
  <kbd>Password</kbd> : password123
- **Output:**
   * **UI:** Redirects to the Dashboard and shows the user-specific task list, AuthService validates the hashed password and creates an active session.
---

### 2. Data Persistence
**As a user, I want my data to be automatically saved so that I never lose my progress.**

- **Input:** Any create, update, or delete action. 
- **Output:**
   * **UI:** Success notification (e.g., toast message).
   * **System:** The SQLModel session commits changes to the task_tracker.db file immediately.
---

### 3. Create New Tasks
**As a user, I want to create new tasks with descriptions and dates so that I can track responsibilities.**

- **Input:**
   * **Description:** Prepare for Statistics retake.
   * **Date:** 2026-06-25
- **Output:**
   * **UI:** New task card appears in the main dashboard view.
   * **System:** A new row is inserted into the Task table with a pending status.
---

### 4. Edit Existing Tasks
**As a user, I want to edit existing tasks so that I can update details as plans change.**

- **Input:** Task ID <kbd>int</kbd>, updated fields (description, date, or priority).
- **Output:**
   * **UI:** The task card reflects the new description without requiring a manual refresh.
   * **System:** <kbd>TaskService</kbd> updates the specific <kbd>Task_ID</kbd> in the database.
---

### 5. Delete Tasks
**As a user, I want to delete specific tasks so that I can remove irrelevant items.**

- **Input:**
   * **Action:** Click "Delete" on Task #101.
- **Output:**
   * **UI:** The task card is removed from the DOM.
   * **System:** The database record for Task #101 is deleted.
---

### 6. Cancel Action
**As a user, I want the option to cancel a current action to prevent accidental entries.**

- **Input:**
   * **Action:** Click "Cancel" button in the "New Task" modal.
- **Output:**
   * **UI:** Modal closes and clears all unsaved input fields.
   * **System:** No database session is opened; state remains unchanged.
---

### 7. Multi-Criteria Filtering
**As a user, I want to filter tasks by keywords and priority to focus on specific work.**

- **Input:**
   * **Search:** "Report".
   * **Filter:** "High Priority".
- **Output:**
   * **UI:** The task list updates instantly to show only matching tasks.
   * **System:** The app filters the database records to find tasks that contain the keyword AND match the selected priority.
---

### 8. Priority Assignment
**As a user, I want to assign priority levels to visually distinguish my work.**

- **Input:**
   * **Priority Select:** "Medium".
- **Output:**
   * **UI:** The task is styled with a distinct color-coded badge (e.g., Orange for Medium).
   * **System:** The <kbd>priority</kbd> attribute of the Task object is updated.
---

### 9. Deadline Tracking
**As a user, I want to create Deadline Tasks that flag themselves as "Overdue."**

- **Input:**
   * **Type:** "Deadline".
   * **Due Date:** Yesterday's date.
- **Output:**
   * **UI:** Task displays a prominent red "Overdue" badge.
   * **System:** A logical check <kbd>due_date < current_date</kbd> triggers the status update.
---

### 10. Task Recursion
**As a user, I want to create Recurring Tasks that renew themselves automatically.**

- **Input:**
   * **Task Type:** "Recurring".
   * **Action:** User marks task as "Completed."
- **Output:**
   * **UI:** The current instance disappears; a new instance appears for the next interval.
   * **System:** <kbd>TaskService</kbd> archives the old instance and instantiates a new <kbd>TaskInstance</kbd>.
---

### 11. Productivity Export
**As a user, I want a "Download Report" button to export statistics.**

- **Input:**
   * **Action:** Click "Download Report."
- **Output:**
   * **UI:** Browser initiates a download for <kbd>task_data.csv</kbd>.
   * **System:** <kbd>ReportService</kbd> generates a CSV file from the aggregated task data.
---


## Use Cases

![use_case_diagram task_tracker](docs/ucd_task_tracker.png)


### 🔑 Access & Security
| Field | Details |
| :--- | :--- |
| **User case ID** | TC_001 |
| **User case title/description** | Verify that a user can log in with valid username and password  |
| **Preconditions** | - User is registered; - Login page is accessible  |
| **User steps** | 1. Open login page; 2. Enter username `pro_user`; 3. Enter password `Password@123`; 4. Click Login  |
| **User data/input** | Username: `pro_user`, Password: `Password@123`  |
| **Expected result** | User is logged in successfully and dashboard is displayed  |
| **Status** | Pass |

| Field | Details |
| :--- | :--- |
| **User case ID** | TC_002 |
| **User case title/description** | Verify login failure with incorrect password |
| **Preconditions** | User is registered; Login page is accessible |
| **User steps** | 1. Enter valid username; 2. Enter incorrect password; 3. Click Login |
| **User data/input** | Username: `pro_user`, Password: `WrongPassword` |
| **Expected result** | System rejects login and displays an error message |
| **Status** | Pass |

| Field | Details |
| :--- | :--- |
| **User case ID** | TC_003 |
| **User case title/description** | Verify user can securely log out of the system |
| **Preconditions** | User is currently logged in |
| **User steps** | 1. Click the "Logout" button |
| **User data/input** | N/A |
| **Expected result** | Session is terminated and user is redirected to login screen |
| **Status** | Pass |

---

### 📝 Task Operations
| Field | Details |
| :--- | :--- |
| **User case ID** | TC_004 |
| **User case title/description** | Verify creation of a new standard task |
| **Preconditions** | User is logged in and on the dashboard |
| **User steps** | 1. Click "New Task"; 2. Enter description; 3. Select Priority; 4. Click Save |
| **User data/input** | Description: "Buy groceries", Priority: "Medium" |
| **Expected result** | Task appears in the list and is saved to the SQLite database |
| **Status** | Pass |

| Field | Details |
| :--- | :--- |
| **User case ID** | TC_005 |
| **User case title/description** | Verify that an existing task can be updated |
| **Preconditions** | A task already exists in the database |
| **User steps** | 1. Click "Edit" on a task; 2. Change the description; 3. Click Save |
| **User data/input** | New Description: "Buy organic groceries" |
| **Expected result** | The task description is updated in the UI and database |
| **Status** | Pass |

| Field | Details |
| :--- | :--- |
| **User case ID** | TC_006 |
| **User case title/description** | Verify removal of a task from the list |
| **Preconditions** | At least one task exists for the user |
| **User steps** | 1. Click the "Delete" icon; 2. Confirm deletion |
| **User data/input** | Target Task ID: 101 |
| **Expected result** | Task is removed from the UI and the database record is deleted |
| **Status** | Pass |

| Field | Details |
| :--- | :--- |
| **User case ID** | TC_007 |
| **User case title/description** | Verify "Cancel" button prevents unwanted changes |
| **Preconditions** | "Edit Task" or "New Task" modal is open |
| **User steps** | 1. Modify task details; 2. Click "Cancel" |
| **User data/input** | Description: "Mistake task" |
| **Expected result** | Modal closes; no new task is created and no changes are saved |
| **Status** | Pass |

---

### 🔍 Discovery & Organization
| Field | Details |
| :--- | :--- |
| **User case ID** | TC_008 |
| **User case title/description** | Verify task filtering by description keywords |
| **Preconditions** | Multiple tasks exist with different names |
| **User steps** | 1. Enter keyword in the search bar |
| **User data/input** | Keyword: "Report" |
| **Expected result** | Only tasks containing "Report" are visible in the list |
| **Status** | Pass |

| Field | Details |
| :--- | :--- |
| **User case ID** | TC_009 |
| **User case title/description** | Verify list filtering by Priority Level |
| **Preconditions** | Tasks with varied priorities exist (Low, Medium, High) |
| **User steps** | 1. Select "High" from the Priority filter dropdown |
| **User data/input** | Filter: "High" |
| **Expected result** | Only tasks with "High" priority are displayed |
| **Status** | Pass |

| Field | Details |
| :--- | :--- |
| **User case ID** | TC_010 |
| **User case title/description** | Verify behavior when no tasks match search criteria (Edge Case) |
| **Preconditions** | Standard tasks exist in the database |
| **User steps** | 1. Enter a non-matching string in search |
| **User data/input** | Search: "xyz123nonexistent" |
| **Expected result** | List displays "No tasks found"; system remains stable |
| **Status** | Pass |

---

### 🧬 Specialized Task Behaviors
| Field | Details |
| :--- | :--- |
| **User case ID** | TC_011 |
| **User case title/description** | Verify "Overdue" flag triggers for Deadline Tasks |
| **Preconditions** | User is on the creation screen |
| **User steps** | 1. Create Deadline Task; 2. Set Due Date to a past date |
| **User data/input** | Due Date: `2020-01-01` |
| **Expected result** | Task is created and automatically marked with an "Overdue" badge |
| **Status** | Pass |

| Field | Details |
| :--- | :--- |
| **User case ID** | TC_012 |
| **User case title/description** | Verify task automatically renews after completion |
| **Preconditions** | A Recurring Task with a "Daily" interval is present |
| **User steps** | 1. Mark the Recurring Task as "Completed" |
| **User data/input** | Interval: "Daily" |
| **Expected result** | Old task is archived; a new task instance is created for the next day |
| **Status** | Pass |

| Field | Details |
| :--- | :--- |
| **User case ID** | TC_013 |
| **User case title/description** | Verify UI adapts when switching Task types |
| **Preconditions** | "New Task" modal is open |
| **User steps** | 1. Change type from "Deadline" to "Recurring" |
| **User data/input** | Type Selector |
| **Expected result** | "Due Date" field is hidden and "Interval" field is displayed |
| **Status** | Pass |

---

### 📊 Reporting & Persistence
| Field | Details |
| :--- | :--- |
| **User case ID** | TC_014 |
| **User case title/description** | Verify data remains after a browser refresh (System Test) |
| **Preconditions** | User has created multiple tasks |
| **User steps** | 1. Manually refresh the browser page (F5) |
| **User data/input** | N/A |
| **Expected result** | All tasks are re-fetched from SQLite and persist in the UI |
| **Status** | Pass |

| Field | Details |
| :--- | :--- |
| **User case ID** | TC_015 |
| **User case title/description** | Verify export of task data to external file |
| **Preconditions** | User has task history in the system |
| **User steps** | 1. Click "Download Report" button |
| **User data/input** | N/A |
| **Expected result** | A downloadable file (.csv/.xlsx) is generated with task statistics |
| **Status** | Pass |

---

### Wireframes / Mockups

![UI task_tracker](log_in_task_tracker.png)

![UI task_tracker](new_task_task_tracker.png)

---
## 🏛️ Architecture

![architecture task_tracker](docs/architecture_task_tracker.png)

### Layers
The application is built using a **professional three-tier architecture** to ensure a clean separation of concerns:

- **UI Layer:** Built with **NiceGUI**, providing a browser-based interface where the UI state and components are managed securely as Python objects on the server.
- **Application Logic Layer:** Consists of **Controllers** and **Services**.
    - **Controllers:** Orchestrate the interaction between UI pages and backend services.
    - **Services:** Encapsulate business logic, such as `TaskService` for lifecycle management, `AuthService` for security, and `ReportService` for data exports.
- **Persistence Layer:** Utilizes **SQLite** combined with **SQLModel (ORM)** and the **Data Access Object (DAO)** pattern.

### Design Decisions
- **MVC Structure (Model–View–Controller):** A layered MVC variant is used to decouple user interactions from business objects, making the project easier to understand and test.
- **Clear Separation of Concerns:** Business logic in the Service layer remains independent of the UI components in the Page layer.
- **Relational Persistence:** Data management has been migrated to a robust SQLite database using an ORM to avoid direct SQL and ensure modularity.

### Design Patterns Used
- **Model-View-Controller / Layered MVC:** Ideal for applications with graphical interfaces and database access, ensuring that UI logic and domain logic are separated.
- **Facade Pattern:** Implemented in `db.py`, this pattern hides the technical details of database engine initialization and session management from the rest of the application.
- **Singleton Pattern:** The database connection and engine initialization follow a Singleton-like approach within `db.py`. This ensures that the application maintains a single, consistent point of access to the database engine, preventing redundant connections and resource leaks.


---

## 🗄️ Database and ORM

![ERM Diagram](docs/erm_task_tracker.png)

The application uses **SQLModel** to map domain objects to a local **SQLite** database. This approach allows for type-safe database interactions and seamless integration with the NiceGUI frontend.

### Entities
- **`User`**: Represents the system users, storing hashed credentials and profile information.
- **`Task`**: The core entity containing task descriptions, priority levels, and metadata.
- **`TaskInstance`**: Specifically for **Recurring Tasks**, these represent individual occurrences of a repeating task.

### Relationships
- **One `User` → many `Tasks`**: Each task is owned by exactly one user, ensuring data privacy and personalized lists.
- **One `Task` → many `TaskInstances`**: A single recurring task definition can generate multiple instances over time as they are completed.

---

## 📂 Repository Structure

 

```text
task_tracker_app/
├── __main__.py
├── application.py
├── data_access/
│   ├── __init__.py
│   ├── base_dao.py
│   ├── dao.py
│   └── db.py
├── models/
│   ├── __init__.py
│   └── enums.py
│   └── task.py
│   └── task_instance.py
│   └── user.py
├── services/
│   ├── __init__.py
│   ├── auth_service.py
│   ├── report_service.py
│   ├── task_service.py
└── ui/
    ├── __init__.py
    ├── controllers.py
    └── pages.py
```
---

### How to Run

### **1. Prerequisites**
 * Python 3.10+

### **2. Create & activate a virtual environment**
   - **macOS/Linux:**
      ```bash
      python3 -m venv .venv
      source .venv/bin/activate
      ```
   - **Windows:**
      ```bash
      python -m venv .venv
      .venv\Scripts\Activate
      ```

### **3. Install dependencies**
 ```bash
   pip install nicegui sqlmodel sqlalchemy pytest
   ```

### **4. Start the app**
 * Via python run the file __main__.py

###  5. Usage

1. Register/log in
2. Create a task
3. Edit or delete a task
4. Search and filter tasks
5. Complete tasks
6. Download a report

---

## 👥 Team & Contributions


| Name | Contribution |
| :--- | :--- |
| Bernardo Alfonso Suárez Espinoza | NiceGUI UI + documentation |
| Janusz Büeler | Business Logic + testing + documentation |
| Juan Vock | DataBase ORM + testing + documentation |
| Fernando Mauracher García | Controller + documentation |

---
