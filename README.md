# solid-octo-eureka

A Django-based Library Management System with a modern dashboard, book/borrowing management, and data export features.

---

## Features

- Librarian dashboard with statistics and charts
- Quick book issue/return panel
- Overdue book notifications and email reminders
- Export data (books, borrowings, overdue) as CSV
- Activity feed and overdue list
- Dark mode toggle

---

## Getting Started

### 1. Clone the Repository

```sh
git clone https://github.com/yourusername/solid-octo-eureka.git
cd solid-octo-eureka
```

### 2. Create and Activate a Virtual Environment

```sh
python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies

```sh
pip install -r requirements.txt
```

### 4. Apply Migrations

```sh
python manage.py migrate
```

### 5. Create a Superuser (Admin)

```sh
python manage.py createsuperuser
```

### 6. Run the Development Server

```sh
python manage.py runserver
```

Visit [http://127.0.0.1:8000/](http://127.0.0.1:8000/) in your browser.

---

## Usage

- Log in as admin to access the dashboard.
- Issue or return books using the quick panel.
- View statistics, charts, and recent activity.
- Export data as CSV from the dashboard.
- Send overdue email reminders with one click.

---

## Project Structure

- `companyapp/` - Main Django app (models, views, templates, static files)
- `project/` - Django project settings and URLs
- `requirements.txt` - Python dependencies

---

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/YourFeature`)
3. Commit your changes (`git commit -am 'Add some feature'`)
4. Push to the branch (`git push origin feature/YourFeature`)
5. Open a Pull Request

---

## License

This project is licensed under the MIT License.