from flask import Flask, render_template, request, jsonify, flash, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import plotly
import plotly.express as px
import json
import pandas as pd
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here'

# Database configuration
DB_USER = os.getenv('DB_USER', 'postgres')
DB_PASSWORD = os.getenv('DB_PASSWORD', '')
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = os.getenv('DB_PORT', '5432')
DB_NAME = os.getenv('DB_NAME', 'tourism')

# SQLAlchemy database URI
app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_size': 10,
    'max_overflow': 2,
    'pool_timeout': 30,
    'pool_recycle': 1800,
}

db = SQLAlchemy(app)

# Models
class Tourist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    nationality = db.Column(db.String(50), nullable=False)
    age = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    visits = db.relationship('Visit', backref='tourist', lazy=True)

class Destination(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    city = db.Column(db.String(50), nullable=False)
    country = db.Column(db.String(50), nullable=False)
    price = db.Column(db.Float, nullable=False)
    visits = db.relationship('Visit', backref='destination', lazy=True)

class Visit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tourist_id = db.Column(db.Integer, db.ForeignKey('tourist.id'), nullable=False)
    destination_id = db.Column(db.Integer, db.ForeignKey('destination.id'), nullable=False)
    visit_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    rating = db.Column(db.Integer)

# Routes
@app.route('/')
def index():
    # Get total counts
    total_tourists = db.session.query(Tourist).count()
    total_destinations = db.session.query(Destination).count()
    total_visits = db.session.query(Visit).count()
    
    # Calculate tourist return rate
    tourists_with_multiple_visits = db.session.query(Tourist.id).join(Visit).group_by(Tourist.id).having(db.func.count(Visit.id) > 1).count()
    return_rate = round((tourists_with_multiple_visits / total_tourists * 100) if total_tourists > 0 else 0, 1)
    
    # Get lists for dropdowns
    tourists = Tourist.query.all()
    destinations = Destination.query.all()
    
    return render_template('index.html',
                         total_tourists=total_tourists,
                         total_destinations=total_destinations,
                         total_visits=total_visits,
                         return_rate=return_rate,
                         tourists=tourists,
                         destinations=destinations)

@app.route('/dashboard')
def dashboard():
    # Get basic statistics
    total_tourists = db.session.query(Tourist).count()
    total_destinations = db.session.query(Destination).count()
    total_visits = db.session.query(Visit).count()
    
    # Calculate average rating
    avg_rating = db.session.query(db.func.avg(Visit.rating)).scalar() or 0
    
    # Create visualization for nationality distribution
    tourists_by_nationality = db.session.query(
        Tourist.nationality, 
        db.func.count(Tourist.id)
    ).group_by(Tourist.nationality).all()
    
    df = pd.DataFrame(tourists_by_nationality, columns=['Nationality', 'Count'])
    fig = px.pie(df, values='Count', names='Nationality', title='Tourists by Nationality')
    nationality_chart = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    
    # Get destination ratings
    destination_ratings = db.session.query(
        Destination.name,
        Destination.city,
        Destination.country,
        db.func.avg(Visit.rating).label('avg_rating'),
        db.func.count(Visit.id).label('visit_count')
    ).join(Visit).group_by(Destination.id).having(db.func.count(Visit.id) > 0).all()
    
    # Get recent activities - Fixed query with explicit join
    recent_activities = db.session.query(
        Tourist.name.label('tourist_name'),
        Destination.name.label('destination_name'),
        Destination.city,
        Destination.country,
        Visit.rating,
        Visit.visit_date
    ).select_from(Visit).join(Tourist, Visit.tourist_id == Tourist.id).join(Destination, Visit.destination_id == Destination.id).order_by(Visit.visit_date.desc()).limit(10).all()
    
    # Format the visit dates - Convert UTC to IST (UTC+5:30)
    formatted_activities = []
    for activity in recent_activities:
        # Convert UTC to IST by adding 5 hours and 30 minutes
        ist_time = activity.visit_date + timedelta(hours=5, minutes=30)
        formatted_activity = {
            'tourist_name': activity.tourist_name,
            'destination_name': activity.destination_name,
            'city': activity.city,
            'country': activity.country,
            'rating': activity.rating,
            'visit_date': ist_time.strftime('%Y-%m-%d %H:%M IST')
        }
        formatted_activities.append(formatted_activity)
    
    # Advanced Analytics - Top Destinations by Revenue
    top_destinations = db.session.query(
        Destination.name,
        Destination.city,
        Destination.country,
        db.func.count(Visit.id).label('visit_count'),
        db.func.sum(Destination.price).label('total_revenue')
    ).join(Visit).group_by(Destination.id).order_by(db.func.sum(Destination.price).desc()).limit(5).all()
    
    # Advanced Analytics - Seasonal Trends
    seasonal_trends = db.session.query(
        db.extract('month', Visit.visit_date).label('month'),
        db.func.count(Visit.id).label('count')
    ).group_by('month').order_by('month').all()
    
    # Convert month numbers to month names
    month_names = {
        1: 'January', 2: 'February', 3: 'March', 4: 'April', 
        5: 'May', 6: 'June', 7: 'July', 8: 'August', 
        9: 'September', 10: 'October', 11: 'November', 12: 'December'
    }
    
    seasonal_data = []
    for month_num, count in seasonal_trends:
        seasonal_data.append({
            'month': month_names.get(month_num, f'Month {month_num}'),
            'count': count
        })
    
    # Advanced Analytics - Popular Destination Pairs
    # This shows which destinations are often visited together
    destination_pairs = db.session.query(
        Destination.name.label('destination1'),
        Destination.city.label('city1'),
        Destination.country.label('country1'),
        db.func.count(Visit.id).label('pair_count')
    ).join(Visit).group_by(Destination.id).order_by(db.func.count(Visit.id).desc()).limit(5).all()
    
    # Advanced Analytics - Tourist Return Rate
    # Calculate how many tourists visit multiple destinations
    tourist_visits = db.session.query(
        Tourist.id,
        db.func.count(db.distinct(Visit.destination_id)).label('destinations_visited')
    ).join(Visit).group_by(Tourist.id).all()
    
    return_rate = {
        'single_destination': sum(1 for _, count in tourist_visits if count == 1),
        'multiple_destinations': sum(1 for _, count in tourist_visits if count > 1),
        'total_tourists': len(tourist_visits) if tourist_visits else 0
    }
    
    # Calculate return rate percentage
    if return_rate['total_tourists'] > 0:
        return_rate['percentage'] = (return_rate['multiple_destinations'] / return_rate['total_tourists']) * 100
    else:
        return_rate['percentage'] = 0
    
    # Get all tourists with their visit counts
    all_tourists = db.session.query(
        Tourist.id,
        Tourist.name,
        Tourist.nationality,
        Tourist.age,
        db.func.count(Visit.id).label('visit_count'),
        db.func.count(db.distinct(Visit.destination_id)).label('destinations_visited')
    ).outerjoin(Visit).group_by(Tourist.id).all()
    
    # Separate tourists into single and multiple destination visitors
    single_destination_tourists = [t for t in all_tourists if t.destinations_visited == 1]
    multi_destination_tourists = [t for t in all_tourists if t.destinations_visited > 1]
    
    return render_template('dashboard.html',
                         total_tourists=total_tourists,
                         total_destinations=total_destinations,
                         total_visits=total_visits,
                         avg_rating=avg_rating,
                         nationality_chart=nationality_chart,
                         destination_ratings=destination_ratings,
                         recent_activities=formatted_activities,
                         top_destinations=top_destinations,
                         seasonal_trends=seasonal_data,
                         destination_pairs=destination_pairs,
                         return_rate=return_rate,
                         all_tourists=all_tourists,
                         single_destination_tourists=single_destination_tourists,
                         multi_destination_tourists=multi_destination_tourists)

@app.route('/api/tourists', methods=['GET', 'POST'])
def handle_tourists():
    if request.method == 'POST':
        data = request.json
        new_tourist = Tourist(
            name=data['name'],
            nationality=data['nationality'],
            age=data['age']
        )
        db.session.add(new_tourist)
        db.session.commit()
        return jsonify({'message': 'Tourist added successfully'})
    
    tourists = db.session.query(Tourist).all()
    return jsonify([{
        'id': t.id,
        'name': t.name,
        'nationality': t.nationality,
        'age': t.age
    } for t in tourists])

@app.route('/api/destinations', methods=['GET', 'POST'])
def handle_destinations():
    if request.method == 'POST':
        data = request.json
        new_destination = Destination(
            name=data['name'],
            city=data['city'],
            country=data['country'],
            price=float(data['price'])
        )
        db.session.add(new_destination)
        db.session.commit()
        return jsonify({'message': 'Destination added successfully'})
    
    destinations = db.session.query(Destination).all()
    return jsonify([{
        'id': d.id,
        'name': d.name,
        'city': d.city,
        'country': d.country,
        'price': d.price
    } for d in destinations])

@app.route('/api/visits', methods=['GET', 'POST'])
def handle_visits():
    if request.method == 'POST':
        data = request.json
        new_visit = Visit(
            tourist_id=data['tourist_id'],
            destination_id=data['destination_id'],
            rating=data.get('rating', 0)
        )
        db.session.add(new_visit)
        db.session.commit()
        return jsonify({'message': 'Visit recorded successfully'})
    
    visits = db.session.query(Visit).all()
    return jsonify([{
        'id': v.id,
        'tourist_id': v.tourist_id,
        'destination_id': v.destination_id,
        'visit_date': v.visit_date.isoformat(),
        'rating': v.rating
    } for v in visits])

@app.route('/add_tourist', methods=['POST'])
def add_tourist():
    name = request.form.get('name')
    nationality = request.form.get('nationality')
    age = request.form.get('age')
    
    new_tourist = Tourist(name=name, nationality=nationality, age=age)
    db.session.add(new_tourist)
    db.session.commit()
    
    flash('Tourist added successfully!', 'success')
    return redirect(url_for('index'))

@app.route('/add_destination', methods=['POST'])
def add_destination():
    name = request.form.get('name')
    country = request.form.get('country')
    city = request.form.get('city')
    price = request.form.get('price')
    
    new_destination = Destination(name=name, country=country, city=city, price=price)
    db.session.add(new_destination)
    db.session.commit()
    
    flash('Destination added successfully!', 'success')
    return redirect(url_for('index'))

@app.route('/record_visit', methods=['POST'])
def record_visit():
    tourist_id = request.form.get('tourist_id')
    destination_id = request.form.get('destination_id')
    visit_date = request.form.get('visit_date')
    rating = request.form.get('rating')
    
    # Convert string date to datetime
    visit_date = datetime.strptime(visit_date, '%Y-%m-%d')
    
    new_visit = Visit(tourist_id=tourist_id, destination_id=destination_id, 
                     visit_date=visit_date, rating=rating)
    db.session.add(new_visit)
    db.session.commit()
    
    flash('Visit recorded successfully!', 'success')
    return redirect(url_for('index'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True) 