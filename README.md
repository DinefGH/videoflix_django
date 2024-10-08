VideoFlix Backend
This is the backend for the VideoFlix project, built with Django and Django REST Framework. The project provides APIs for video streaming, user authentication, and other functionalities necessary for a video streaming platform.

Features
User Authentication: Custom user model with email authentication.
JWT Authentication: Secure authentication using JSON Web Tokens.
Video Upload and Streaming: Upload videos and stream them in different resolutions.
Caching: Implemented caching using Redis for performance optimization.
Email Notifications: Support for sending emails (e.g., password reset).
CORS Support: Cross-Origin Resource Sharing configured for frontend integration.
Debugging Tools: Integrated Django Debug Toolbar for debugging purposes.

Technologies Used
Framework: Django 5.1
REST API: Django REST Framework
Authentication: Simple JWT
Database: PostgreSQL
Caching: Redis
Others: Django Import-Export, Django Debug Toolbar, CORS Headers

Prerequisites
Python 3.x
PostgreSQL
Redis
Git




Installation

Clone the Repository
git clone https://github.com/yourusername/videoflixbackend.git
cd videoflixbackend


Create a Virtual Environment
python -m venv env
source env/bin/activate  # On Windows: env\Scripts\activate


Install Dependencies
pip install -r requirements.txt


Install Redis
Download and install Redis from the official website.
Ensure Redis is running on localhost:6379.


Set Up PostgreSQL Database
Install PostgreSQL from the official website.
Create a new database and user for the project.

