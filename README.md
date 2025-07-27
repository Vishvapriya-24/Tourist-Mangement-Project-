# 🧳 Tourist Management System

A web-based application built with Flask and PostgreSQL to manage tourists, destinations, and visit records with insightful analytics and interactive dashboards.

---

## 📌 Features

- Add and manage:
  - Tourists (name, nationality, age)
  - Destinations (name, city, country, price)
  - Visits (date, rating)
- Dashboard with:
  - Total tourist, destination, and visit count
  - Pie chart for tourist nationalities
  - Average ratings, top destinations by revenue
  - Recent activity logs
  - Seasonal travel trends
  - Return rate analysis
- RESTful API access for data automation
- Clean form submissions with flash messages
- Timezone conversion to IST (UTC+5:30)

---

## 🛠 Tech Stack

- **Backend:** Python, Flask, SQLAlchemy
- **Database:** PostgreSQL
- **Frontend:** HTML + Jinja2, Plotly.js
- **Libraries:** pandas, python-dotenv

---

## 📦 Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/tourist-management-system.git
cd tourist-management-system
python app.py

