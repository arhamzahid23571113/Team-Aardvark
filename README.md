# **Team Aardvark - Code Tutors Information System**

A web-based information system built with **Django** for **Code Tutors**, a fictitious tutoring business. This application streamlines administrative tasks such as managing lesson requests, scheduling, and invoicing. The system includes **role-based access** for:

- **Admins**: Full access to manage students, tutors, and schedules.
- **Tutors**: Access to view assigned lessons and manage availability.
- **Students**: Access to view lesson schedules and invoices.

---

## **Team Members**

The project was developed by the following team members:

- Arham Zahid
- Abiha Tasnim
- Bleona Miftari
- Amina Ali
- Abdullah Muzahir

---

## **Project Overview**

The project, named `task_manager`, consists of a single app called `tasks`. This app is responsible for managing tasks and workflows for the tutoring business.

---

## **Deployed Application**

The deployed version of the application is available at:  
(https://k23006731.pythonanywhere.com/)]

---

## **Installation Instructions**

To set up the application locally, follow these steps:

### **1. Set Up a Virtual Environment**:

From the root directory of the project:

```bash
$ virtualenv venv
$ source venv/bin/activate   # On Windows: .\venv\Scripts\activate
```

### **2. Install Dependencies**:

Install all required packages using:

```bash
$ pip3 install -r requirements.txt
```

### **3. Migrate the Database**:

Apply database migrations:

```bash
$ python3 manage.py migrate
```

### **4. Seed the Database**:

Populate the development database with sample data:

````bash
$ python3 manage.py seed


### **5. Run Tests**:
Verify the application by running all tests:
```bash
$ python3 manage.py test
````

> **Note**: If there are any deviations in these instructions for your version, please document them here.

---

## **Project Dependencies**

The packages required for this project are listed in `requirements.txt`. These include, but are not limited to:

- **Django**: The core web framework.
- **Other Dependencies**: [Add specific packages as needed].

---

## **AI Declaration**

For this project, AI was used to help form tests, namely:

- test_invoice_page.py
- test_admin_invoice_view.py
- test_generate_invoice.py
- test_manage_invoices.py
