# Auth System

This microservice provides JWT Authentication, managing user's favorites and product question.

## Features
- **Django REST Framework:** DRF is employed to build a clean and well-structured API, facilitating seamless interactions between the frontend and backend services.
- **Redis:** In-Memory Data Storage, used for its high-speed data caching capabilities, significantly improving the performance of user favorites-related operations.
- **PostgreSQL:** provides a robust and secure database solution for persistently storing user data and comments.
- **JWT Authentication:** implements JSON Web Tokens (JWT) for secure user authentication, ensuring protected access to user-specific data and features.
- **Aiogram:** utilized for creating Telegram bots, allowing for interactive user notifications and real-time updates related to user activities.

## Installation

1. Clone the repository:
2. Create a virtual environment:

    ```bash
    python -m venv venv
    ```

3. Activate the virtual environment:
    ```bash
    source venv/bin/activate
    ```

4. Install the dependencies:

    ```bash
    pip install -r requirements.txt
    ```
   
## Usage

1. Run the Django application:

    ```bash
    python manage.py runserver
    ```

2. Open your web browser and navigate to `http://localhost:8000`

## API Endpoints

- `/questions`: GET or POST User's questions

- `/favorites`: GET or POST User's favorite list
