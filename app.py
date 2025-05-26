from flask import Flask, render_template, request, redirect, url_for, flash, session
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'SubaruwrxSTi'  # replace with a secure key for production

# Temporary message storage (resets on restart)
temp_messages = []

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

        temp_messages.append({
            "name": name,
            "email": email,
            "message": message,
            "timestamp": datetime.utcnow()
        })

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

    # Pagination manually
    page = int(request.args.get('page', 1))
    per_page = 5
    skips = per_page * (page - 1)

    paginated = temp_messages[::-1][skips:skips + per_page]
    total = len(temp_messages)

    return render_template('messages.html', messages=paginated, page=page, total=total, per_page=per_page)

@app.route('/logout')
def logout():
    session.pop('admin_logged_in', None)
    flash("Logged out successfully.", 'info')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
