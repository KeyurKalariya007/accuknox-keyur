# Django Rate Limiting Example

This Django project demonstrates how to implement rate limiting for API requests without using decorators. The rate limiting logic is implemented directly in the view.

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/yourusername/your-repo.git

2. Install the required packages 
    ```bash
    pip install -r requirements.txt

3. Run migrations:
    ```bash
    python manage.py makemigrations

    python manage.py migrate

4. Start the development server:
    ```bash
    python manage.py runserver


# Usage
Send POST requests to /api/users/friend-request/ to create a new friend request.
The rate limiting allows each user to send up to 3 friend requests per minute. If the limit is exceeded, a "Rate limit exceeded" message is returned.
