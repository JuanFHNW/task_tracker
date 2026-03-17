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
