# 🏋️ FitTrack Pro — Gym Membership Management System

A full-stack web application for managing gym memberships, built with Flask and deployed via Docker + Jenkins CI/CD pipeline.

---

## 📌 Features

- **Dashboard** — Live stats: total members, active, expired, today's check-ins, revenue
- **Member Management** — Enroll, edit, renew, delete members with plan selection
- **Membership Plans** — Basic / Standard / Premium / Annual with auto-expiry calculation
- **Attendance Tracking** — Daily check-in log for active members
- **Payment Logs** — Full transaction history with revenue summary
- **Expiry Alerts** — Highlights members expiring within 7 days

---

## 🛠️ Tech Stack

| Layer      | Technology           |
|------------|----------------------|
| Backend    | Python 3.11, Flask   |
| Database   | SQLite               |
| Frontend   | HTML5, CSS3, Jinja2  |
| Container  | Docker               |
| CI/CD      | Jenkins Pipeline     |
| VCS        | Git                  |

---

## 🚀 Run Locally

```bash
# 1. Clone the repo
git clone https://github.com/your-username/gym-management.git
cd gym-management

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the app
python app.py

# 4. Open in browser
http://localhost:5000
```

---

## 🐳 Run with Docker

```bash
# Build the image
docker build -t fittrack-gym-app .

# Run the container
docker run -d -p 5000:5000 --name fittrack-app fittrack-gym-app

# Or use Docker Compose
docker-compose up -d
```

---

## 🔁 Jenkins CI/CD Pipeline

The `Jenkinsfile` defines a 6-stage pipeline:

```
Checkout → Install Dependencies → Run Tests → Build Docker Image → Deploy Container → Health Check
```

### Setup Jenkins:
1. Install Jenkins + Docker on your server
2. Create a new **Pipeline** job
3. Set Source to **Git** and point to this repo
4. Jenkins auto-detects the `Jenkinsfile` and runs the pipeline

---

## 📁 Project Structure

```
gym-management/
├── app.py               # Flask application & routes
├── requirements.txt     # Python dependencies
├── Dockerfile           # Docker build instructions
├── docker-compose.yml   # Multi-container setup
├── Jenkinsfile          # CI/CD pipeline stages
├── .gitignore
└── templates/
    ├── base.html        # Shared layout & sidebar
    ├── index.html       # Dashboard
    ├── members.html     # Members list
    ├── form.html        # Add/Edit member
    ├── attendance.html  # Check-in tracking
    └── payments.html    # Payment logs
```

---

## 📊 Membership Plans

| Plan     | Price  | Duration | Features              |
|----------|--------|----------|-----------------------|
| Basic    | ₹499   | 30 days  | Gym Access            |
| Standard | ₹999   | 30 days  | Gym + Cardio          |
| Premium  | ₹1799  | 90 days  | Gym + Cardio + PT     |
| Annual   | ₹4999  | 365 days | All Access + Diet Plan|

---

## 👨‍💻 Author

Developed as a Mini Project for DevOps & CI/CD coursework.
