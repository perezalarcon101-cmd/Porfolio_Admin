from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

app = Flask(__name__)

# 1. Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///portfolio.db'
app.config['SECRET_KEY'] = 'perez_secret_key_123' # Palitan mo ito kahit ano
db = SQLAlchemy(app)

# 2. Login Setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# 3. Database Models (Tables)
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

class About(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), default="Hobbies / Interests") # Bagong column
    content = db.Column(db.Text, nullable=False)
    profile_pic = db.Column(db.String(200), default="image2.jpg") # Pangalan ng image file

class Skill(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    icon_class = db.Column(db.String(100))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# 4. Routes (Frontend at Backend)

@app.route('/')
def index():
    about_data = About.query.first()
    skills_data = Skill.query.all()
    return render_template('index.html', about=about_data, skills=skills_data)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            login_user(user)
            return redirect(url_for('admin'))
        flash('Invalid Username or Password!')
    return render_template('login.html')



# ADMIN SECTION

@app.route('/admin', methods=['GET', 'POST'])
@login_required
def admin():
    about_data = About.query.first()
    skills_data = Skill.query.all()
    
    if request.method == 'POST':
        new_content = request.form.get('about_content')

        if about_data:
            about_data.content = new_content
        else:
            about_data = About(content=new_content)
            db.session.add(about_data)

        db.session.commit()
        return redirect(url_for('admin'))
        
    return render_template('admin.html', about=about_data, skills=skills_data)



@app.route('/add_skill', methods=['POST'])
@login_required
def add_skill():
    name = request.form.get('skill_name')
    icon = request.form.get('skill_icon')
    if name:
        new_skill = Skill(name=name, icon_class=icon)
        db.session.add(new_skill)
        db.session.commit()
    return redirect(url_for('admin'))

@app.route('/delete_skill/<int:id>')
@login_required
def delete_skill(id):
    skill = Skill.query.get(id)
    db.session.delete(skill)
    db.session.commit()
    return redirect(url_for('admin'))

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all() # Gagawa ng portfolio.db file
    app.run(debug=True)

