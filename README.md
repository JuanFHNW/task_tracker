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

### 🔑 Access & Security
* **As a user**, I want to **log in with my username and password** so that I can securely view and manage my personal task list.
* **As a user**, I want my data to be **automatically saved** so that I never lose my progress or task history when I close the application.

### 📝 Task Operations

* **As a user**, I want to **create new tasks** with descriptions and dates so that I can keep track of upcoming responsibilities.
* **As a user**, I want to **edit existing tasks** so that I can update details as my plans and circumstances change.
* **As a user**, I want to **delete specific tasks** so that I can remove items that are no longer relevant to my workload.
* **As a user**, I want the option to **cancel a current action** via a button to prevent saving unwanted changes or accidental entries.

### 🔍 Discovery & Organization

* **As a user**, I want to **filter and search my tasks by multiple criteria** (description keywords, date, priority level, and task type) so that I can instantly drill down to the exact subset of tasks I need to focus on.
* **As a user**, I want to **assign priority levels** (Low, Medium, High) to my tasks to visually distinguish my most critical work from minor to-dos.


### 🧬 Specialized Task Behaviors
* **As a user**, I want to create **Deadline Tasks** that automatically flag themselves as "Overdue" if the date passes, ensuring I don't miss urgent milestones.
* **As a user**, I want to create **Recurring Tasks** that automatically renew themselves for a future date once finished, eliminating the need for manual re-entry.

### 📊 Reporting & Export
* **As a user**, I want a **"Download Report" button** that immediately exports my task statistics into an **Excel/CSV file** so I can track my long-term productivity offline with one click.
  

