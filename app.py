from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = 'SubaruwrxSTi'  # Replace with a more secure key in production

# Database configuration (change to PostgreSQL in production)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Database model
class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    message = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

# ROUTES
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/services')
def services():
    return render_template('services.html')

@app.route('/portfolio')
def portfolio():
    return render_template('portfolio.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        message = request.form['message']

        if not all([name, email, message]):
            flash("All fields are required.", "danger")
            return redirect(url_for('contact'))

        new_msg = Message(name=name, email=email, message=message)
        db.session.add(new_msg)
        db.session.commit()

        flash('Message sent successfully!', 'success')
        return redirect(url_for('contact'))

    return render_template('contact.html')

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == 'admin' and password == 'administrator':
            session['admin_logged_in'] = True
            return redirect(url_for('view_messages'))
        else:
            flash('Invalid credentials', 'danger')
    return render_template('admin_login.html')

@app.route('/messages')
def view_messages():
    if not session.get('admin_logged_in'):
        flash("Please log in to access admin messages.", 'warning')
        return redirect(url_for('admin'))

    # Pagination
    page = int(request.args.get('page', 1))
    per_page = 5
    skips = per_page * (page - 1)

    total = Message.query.count()
    paginated = Message.query.order_by(Message.timestamp.desc()).offset(skips).limit(per_page).all()

    return render_template('messages.html', messages=paginated, page=page, total=total, per_page=per_page)

@app.route('/logout')
def logout():
    session.pop('admin_logged_in', None)
    flash("Logged out successfully.", 'info')
    return redirect(url_for('index'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create DB tables if not exist
    app.run(debug=True)
