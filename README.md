# Social Networking API

## Description
This project is a Django Rest Framework-based API for a social networking application. It includes user authentication, friend request management, and user search functionalities.

## Installation Steps

1. **Clone the Repository**
   ```bash
   git clone https://github.com/Gullu06/socialMediaAPI.git
   cd socialMediaAPI

2. **Set Up a Virtual Environment**
    ```bash
    python -m venv env
    source env/bin/activate  # On Windows use: env\Scripts\activate

3. **Install Dependencies**
    ```bash
    pip install -r requirements.txt

4. **Apply Migrations**
    ```bash
    python manage.py migrate

5. **Run the Development Server**
    ```bash
    python manage.py runserver

6. **Access the API**
    Open your browser and go to http://127.0.0.1:8000/ to use the API endpoints

**API Endpoints**
    Signup: POST request to
        /api/users/signup/

    Login: POST request to
        /api/users/login/

    Search Users:  GET request to
        /api/users/search/

    Send/Accept/Reject Friend Request: POST request to
        /api/users/friend-request/

    List Friends: GET request to
        /api/users/friends/

    Pending Friend requests: GET request to
        /api/users/pending-friend-requests/

    Logout: POST request to
        /api/users/logout/
