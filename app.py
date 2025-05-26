from flask import Flask, render_template, request, redirect, url_for, flash, session
from pymongo import MongoClient
from datetime import datetime
import os


app = Flask(__name__)
app.config['MONGO_URI'] = os.environ.get('MONGO_URI')
app.config['MONGO_URI'] = 'mongodb+srv://topminduser:<db_password>@topmind-cluster.1tlh8xr.mongodb.net/?retryWrites=true&w=majority&appName=topmind-cluster'
app.secret_key = 'SubaruwrxSTi'#replace with a secure key from production

# MongoDB configuration
mongo_uri = os.environ.get("MONGO_URI")  # You’ll set this on Render
client = MongoClient(mongo_uri)
db = client["topmind-db"]  # Use any database name
messages_collection = db["messages"]

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

        # Insert into MongoDB
        messages_collection.insert_one({
            "name": name,
            "email": email,
            "message": message,
            "timestamp": datetime.utcnow()
        })

        flash('Message sent successfully!', 'success')
        return redirect(url_for('contact'))

    return render_template('contact.html')

# Simple admin login
@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == 'admin' and password == 'admin123':
            session['admin_logged_in'] = True
            return redirect(url_for('view_messages'))
        else:
            flash('Invalid credentials', 'danger')
    return render_template('admin_login.html')

# View messages
@app.route('/messages')
def view_messages():
    if not session.get('admin_logged_in'):
        flash("Please log in to access admin messages.", 'warning')
        return redirect(url_for('admin'))

    # Pagination manually
    page = int(request.args.get('page', 1))
    per_page = 5
    skips = per_page * (page - 1)

    all_messages = list(messages_collection.find().sort("timestamp", -1).skip(skips).limit(per_page))
    total = messages_collection.count_documents({})

    return render_template('messages.html', messages=all_messages, page=page, total=total, per_page=per_page)

@app.route('/logout')
def logout():
    session.pop('admin_logged_in', None)
    flash("Logged out successfully.", 'info')
    return redirect(url_for('index'))

# Run server
if __name__ == '__main__':
    app.run(debug=True)
