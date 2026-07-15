# Social Media API project

A comprehensive REST API for social media platform, that supports user profiles, followers, posts, likes and comments. Built with Django REST Framework, featuring JWT authentication for secure access and leverages Celery with Flower for task scheduling and monitoring.

## Installation using GitHub
Python 3.11 must be already installed  
git clone https://github.com/viktoriaom/social-media-api  
cd social_media_api  
create .env file based on the example

## Local Setup with SQLite
python3 -m venv venv  
source venv/bin/activate # *creates virtual environment on macOS/Linux*    
venv\Scripts\activate # *creates virtual environment on Windows*  
pip install -r requirements.txt  
python manage.py makemigrations # *creates migrations*    
python manage.py migrate # *creates DB*  
python manage.py runserver # *starts Django server*    

The API will be available at http://127.0.0.1:8000/  

#### Optional
Load test data into db:  
python manage.py loaddata fixtures/social_data.json


## Run with Docker and PostgreSQL
docker-compose build  
docker-compose up  

The API will be available at `http://127.0.0.1:8002/

#### Optional
Load test data into db:  
docker-compose exec theatre python manage.py loaddata fixtures/social_data.json


## Getting Access
* register a new user via api/user/register  
* get access token via api/user/token  
* include the token in your request headers:  
Authorization: Bearer "your-access-token"

#### Demo Credentials
For testing purposes only:  
**email:** xenia@social.com  
**password:** qazwsx


## Features
### Core functionality
* **User Registration & Authentication** - Register with email/password, login to receive token, logout to invalidate token  
* **Profile Management** - Create, update, and view user profiles with picture, bio, and searchable details  
* **Follow System** - Follow/unfollow users, view followers and following lists  
* **Post Management** - Create posts with text, optional pictures and hashtags, retrieve own posts and posts from followed users  
* **Hashtag Filtering** - Retrieve posts by hashtags
* **Likes & Comments** - Like/unlike posts, view liked posts, add and view comments  
* **Scheduled Posts** - Schedule post creation for delayed publishing  


### Technical features
* **JWT Authentication** - Secure token-based authentication for all API endpoints  
* **Email-based Login** - Use email instead of username for authentication  
* **Search & Filtering** - Search users by different profile criteria, filter posts by hashtags  
* **Image Upload** - Optional image attachments for posts and profile pictures  
* **Role-based Permissions** - Restrict actions to authenticated users; enforce ownership rules for posts, comments, and profiles  
* **API Documentation** - Interactive Swagger/ReDoc docs  
* **Task Scheduling** - Celery & Flower integration for background job management  
* **Pagination** - Paginated results for large datasets
* **Comprehensive Tests** - Full test coverage for custom features
  

## Built With
* Django [https://www.djangoproject.com] - Web framework  
* Django REST Framework [https://www.django-rest-framework.org] - API toolkit  
* PostgreSQL [https://www.postgresql.org] - Database  
* SQLite [https://sqlite.org] - Database  
* JWT [https://www.jwt.io] - Authentication  
* Docker [https://www.docker.com] - Containerization  
* drf-spectacular [https://drf-spectacular.readthedocs.io] - API documentation  


## Usage Tips
* **User Actions** – Users can register, authenticate, and manage their own profiles, posts, likes, and comments  
* **Profile Ownership** – Users may update or delete only their own profile information  
* **Post Ownership** – Users can update or delete only their own posts; scheduled publishing does not count as editing  
* **Follow System** – Users can follow/unfollow others and view their own followers/following lists  
* **Access Control** – Users may only view and manage their own private data (e.g., profile, posts, likes)   
* **Permission Enforcement** – Most endpoints enforce custom permission classes to ensure authenticated access and ownership rules   
* **Media Handling** – Images are optional for posts and profiles; uploads are tied directly to the related resource  
