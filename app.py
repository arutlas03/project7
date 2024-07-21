from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'your_secret_key'

database = SQLAlchemy(app)

class User(database.Model):
    id = database.Column(database.Integer, primary_key=True)
    first_name = database.Column(database.String(50), nullable=False)
    last_name = database.Column(database.String(50), nullable=False)
    email = database.Column(database.String(100), unique=True, nullable=False)
    password = database.Column(database.String(100), nullable=False)

@app.route('/')
def index():
    return render_template('index.html')

def check_password(password):
    failedCases = []
    if not any(c.islower() for c in password):
        failedCases.append('Password must contain at least one lowercase letter.')
    if not any(c.isupper() for c in password):
        failedCases.append('Password must contain at least one uppercase letter.')
    if not password[-1].isdigit():
        failedCases.append('Password must end with a number.')
    if len(password) < 8:
        failedCases.append('Password should be at least 8 characters long.')
    return failedCases

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        failedCases = check_password(password)
        if failedCases:
            return render_template('signup.html', errors=failedCases)
        else:
            if password != confirm_password:
                return render_template('signup.html', errors=['Passwords do not match'])

            existing_user = User.query.filter_by(email=email).first()
            if existing_user:
                return render_template('signup.html', errors=['Email address already exists'])

            new_user = User(first_name=first_name, last_name=last_name, email=email, password=password)
            database.session.add(new_user)
            database.session.commit()

            return render_template('thankyou.html', first_name=first_name)
            

    return render_template('signup.html')

@app.route('/thankyou')
def thankyou():
    return render_template('thankyou.html')

@app.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email, password=password).first()
        if user:
            return render_template('secretPage.html', user=user)
        else:
            return render_template('index.html', message='Invalid credentials. Please try again.')

    return render_template('index.html')

with app.app_context():
    database.create_all()

if __name__ == '__main__':
    app.run(debug=True)
