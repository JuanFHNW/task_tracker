# 🌐 Task Tracker Web Pro

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

## 👥 User Stories
To ensure the application meets the needs of its end-users, the following requirements have been defined:

### 🛡️ Administrator Roles

* **As an Administrator**, I want to **manage my own personal task list** with the same functionality as a Standard User, so I can stay productive while managing the system.

* **As an Administrator**, I want to **reset a user's password** to maintain system accessibility for the team.

* **As an Administrator**, I want to **access a system-wide dashboard** to view total task counts and user activity for project reporting.

### 👤 Standard User (Authenticated User)

* As a user, I want to **log in with my username and password** so that I can securely view and manage my personal task list.

* As a user, I want to **add a new task with a valid future date and description** to keep my schedule accurate.

* As a user, I want to **search for a task by date or description** so I can efficiently plan my activities.

* As a user, I want to **edit specific tasks** to update their details as my plans change.

* As a user, I want to **delete specific tasks** to keep my workload focused.

* As a user, I want the option to **cancel an action by clicking a button** if I change my mind during input.

* As a user, I want my **data automatically saved** so I never lose my progress.

* As a user, I want a **simple and well-organized interface** so that I can stay focused on completing tasks rather than navigating the app.
