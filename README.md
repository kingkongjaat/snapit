# SnapIt

SnapIt is a modern, highly interactive social media platform built with Django. It features real-time messaging, comprehensive user profiles, a dynamic notification system, and customizable user settings to deliver a seamless and engaging user experience.

## 🌟 Features

* **User Authentication & Profiles:** Secure login/signup system with detailed user profiles, featuring tabbed content (Posts, Followers, Following).
* **Dynamic Feed & Posts:** Create, view, and interact with posts in a dynamic dashboard feed.
* **Real-time Messaging:** Integrated chat system with emoji support for private conversations between users.
* **Notification System:** Robust notifications for likes, comments, follows, and messages, featuring deep-linking for seamless navigation.
* **User Settings & Privacy:** Granular controls over account privacy, notifications, and an aesthetic theme switcher (Dark/Light mode).
* **Interactive Widgets:** A persistent, interactive To-Do list widget integrated directly into the dashboard feed.

## 🛠️ Technology Stack

* **Backend:** Django (Python)
* **Database:** SQLite (Development) / PostgreSQL (Recommended for Production)
* **Frontend:** HTML, Vanilla CSS, JavaScript
* **Environment Management:** `python-dotenv` for secure environment variables.

## 🚀 Getting Started

Follow these instructions to get a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

* Python 3.8+
* `pip` (Python package installer)

### Installation

1. **Clone the repository** (if you have uploaded it to GitHub):
   ```bash
   git clone https://github.com/your-username/snapit.git
   cd snapit
   ```

2. **Create a Virtual Environment** (Recommended):
   ```bash
   python -m venv venv
   
   # Activate on Windows:
   venv\Scripts\activate
   
   # Activate on macOS/Linux:
   source venv/bin/activate
   ```

3. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
   *(Note: Make sure to run `pip freeze > requirements.txt` before sharing your project to generate this file).*

4. **Environment Variables:**
   Create a `.env` file in the root directory (same level as `manage.py`) and add the following:
   ```env
   SECRET_KEY=your_secure_random_secret_key_here
   DEBUG=True
   ```

5. **Apply Migrations:**
   Set up your database tables by running:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **Create a Superuser (Admin):**
   ```bash
   python manage.py createsuperuser
   ```

7. **Run the Development Server:**
   ```bash
   python manage.py runserver
   ```
   Visit `http://127.0.0.1:8000/` in your browser to view the application.

## 🔒 Deployment & Security

When deploying this application to a production environment (like Render, Heroku, or AWS), ensure the following:

* Set `DEBUG=False` in your `.env` file.
* Update `ALLOWED_HOSTS` in `settings.py` to include your production domain.
* Configure a production-grade database like PostgreSQL instead of the default SQLite.
* Use a production WSGI server like Gunicorn.
* Run `python manage.py collectstatic` to serve static files correctly.

## 🤝 Contributing

Contributions, issues, and feature requests are welcome! 
Feel free to check the [issues page](#) if you want to contribute.

## 📝 License

This project is open-source and available under the [MIT License](LICENSE).
