from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Use a strong secret in production

# Database config
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'messages.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Database model
class ContactMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    message = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Message from {self.name}>'

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

        new_msg = ContactMessage(name=name, email=email, message=message)
        db.session.add(new_msg)
        db.session.commit()

        flash('Message sent successfully!', 'success')
        return redirect(url_for('contact'))

    return render_template('contact.html')

# Simple admin login
@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # Replace with real authentication
        if username == 'admin' and password == 'admin123':
            session['admin_logged_in'] = True
            return redirect(url_for('view_messages'))
        else:
            flash('Invalid credentials', 'danger')

    return render_template('admin_login.html')

# Protected message view
@app.route('/messages')
def view_messages():
    if not session.get('admin_logged_in'):
        flash("Please log in to access admin messages.", 'warning')
        return redirect(url_for('admin'))

    page = request.args.get('page', 1, type=int)
    per_page = 5  # messages per page

    pagination = ContactMessage.query.order_by(ContactMessage.timestamp.desc()).paginate(page=page, per_page=per_page)
    messages = pagination.items

    return render_template('messages.html', messages=messages, pagination=pagination)


# Logout route
@app.route('/logout')
def logout():
    session.pop('admin_logged_in', None)
    flash("Logged out successfully.", 'info')
    return redirect(url_for('index'))

# Run server
if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Make sure tables exist
    app.run(debug=True)
