# Flask Group Gifting App

## Overview
This Flask application helps friends and families plan thoughtful, non-repetitive group gifts with minimal effort. It includes features for event management, group gifting, recipient profiles, and gift history.

## Features
- Event and reminder management
- Recipient profiles
- Group gifting with voting and budget setting
- Gift history logging
- User authentication
- Dashboard for key information
- JSON API endpoints under `/api/*`
- OpenAPI specification in `api.yaml`

## Project Structure (MVC Style)
```
.
├── app.py
├── api.yaml
├── mvc_app/
│   ├── __init__.py
│   ├── models.py
│   └── controllers/
│       ├── web.py
│       └── api.py
├── templates/
└── static/
```

## Setup Instructions

### Prerequisites
- Python 3.9+
- AWS CLI (for deployment with Zappa)

### Installation
1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd flask-group-gifting-app
   ```
2. Create and activate a virtual environment:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Initialize the database:
   ```bash
   flask db upgrade
   ```

### Running the Application
1. Start the Flask development server:
   ```bash
   flask run
   ```

2. To run the app on gunicorn server:

   gunicorn -w 4 'mvc_app:create_app()' --access-logfile=- --bind 0.0.0.0:8000

   - i created gunicorn.conf.py with the settings above so only the following command can be used: gunicorn -w 4 'mvc_app:create_app()'

- I tried making it publically accessible by just ngrok
- I also learned to run it via gunicorn but I also need to put nginx HTTP server as reverse proxy so client can call it which will call gunicorn WSGI server in background
-- nginx is found in /opt/homebrew/etc/nginx
   -- to find what is running on a specific port: sudo lsof -i TCP:8080 
      -- ps -ax | grep nginx
      -- kill -s QUIT <pid>

- to find logs of Nginx server, navigate to /opt/homebrew/var/log/nginx to find access.log & error.log
   -- use tail -f access.log to see real-time updates to logs



To-do:
- Set up frontend 

   - I imported the build js and css files into /static after exporting the frontend app from Figma. I had to tweak the static files' path. 
   - Now I need to gut the frontend app to remove the dummy data and connect it to backend to pull data from DB. 
      1. I got the first frontend page /users to call backend route /login after resolving CORS issue.
      2. /register done
      3. /login done ; session mgmt using flask (/login's response header has set-cookie field)

- Sort out the users 
- secure APIs
- track user token; figure it out
- Investigate why route '/' is only accessible after user has logged in
   - 

- Group creation is done

- Usage of a group
   - Prompt: Given users are already added (yes, lets assume invitation part is bypassed therefore, every user is already registered), I can add my friends to it. For each user's brithday, an event should be created for the next year. frontend will have a section for upcoming events that can call this API so it can display the remaining days. Any user in the group can go into an event, add a min and max budget 
   - 

- Usage of an event
   - Assume an event has been created for a group member, we want to be able to add min and max budget and gift ideas.
   - Gift ideas can be added under an event. Each gift idea can be voted on.
   - Flag to determine the completion of an event should be present to indicate a gift was given. At the time of marking this flag, user will be asked which gift idea was chosen.

   i just added #sym:FakeVote  table and while running flask db mirgate returns 'No changes in schema detected.'. Without running 'flask db upgrade', i found the table to be automatically created in DB. How can this be?
      - 

- Connecting frontend app
   - Login and register done
   - For dashboard:
      - Show groups