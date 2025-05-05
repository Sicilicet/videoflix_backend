## Project overview

This backend provides API endpoints for managing video uploads, encoding videos to multiple resolutions, tracking user watch history, and handling user registration, login / logout, email verification and password reset. It is built with Django and designed to support a video streaming platform.

## System requirements

- Linux (tested on Ubuntu 20.04 and higher)
- Python 3.8
- Redis
- FFmpeg (for media processing)

To install FFmpeg on Ubuntu:

```bash
sudo apt install ffmpeg
```

## Installation

1. Clone the repository:

```bash
git clone https://github.com/Sicilicet/videoflix_backend
cd videoflix-backend
```

2. Set up a virtual environment

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Environment variables

Create a `.env` file in the root directory and add the environment variables from the template.

## Running the application

To start the development server, run:

```bash
python manage.py runserver
```

Make sure Redis is running for background tasks:

```bash
redis-server
```

To start the RQ worker for processing tasks:

```bash
python manage.py rqworker
```

## Database setup

Apply database migrations:

```bash
Create the folder "migrations" with the file "__init__.py" in each app.
python manage.py makemigrations
python manage.py migrate
```

Create a superuser to access the Django admin:

```bash
python manage.py createsuperuser
```

## API endpoints

- `/api/registration/` - POST - Create a new user.
- `/api/verification/` - POST - Save the verification of a user.
- `/api/resend_verifiction/` - POST - Resends a verification email.
- `/api/forgot_password/` - POST - Sends email to reset password.
- `/api/reset_password/` - POST - Resets a password.
- `/api/login/` - POST - Logs in a user.
- `/api/logout/` - POST - Logs out a user.\*
- `/api/dashboard/` - GET - Gets the data for the dashboard.\*
- `/api/hero/` - GET - Gets the data for the hero section.\*
- `/api/video/<id>/` - GET - Gets the data for a video.\*
- `/api/update_watch_history/<id>/<resolution>` - POST - Updates the watch history of a user.\*

\*authentication token required

## Managing videos

To add a video, run the server and open it in the browser. Click on videos / add video.

To add a new video category add it in content/models.py in the video model to the array CATEGORY_CHOICES.

Once a video has been uploaded:

    Video File: This field cannot be edited. If changes are necessary, the existing video must be deleted, and a new video should be uploaded with the updated details.
    This approach ensures consistency in video metadata and avoids complications in the system.

## Managing users

When registrating a user, please make sure that the username and email are equal. As in the front end only the email is asked during registration, the email is set as the username which then will be used for the login process.
