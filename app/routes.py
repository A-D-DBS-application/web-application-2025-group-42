from flask import Blueprint, request, redirect, url_for, render_template, session
from .models import db, User, Company

main = Blueprint('main', __name__)


@main.route('/')
def index():
    username = None
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        username = user.name
    return render_template('index.html', username=username)


@main.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':

        # User info
        name = request.form.get('name')
        email = request.form.get('email')
        role = request.form.get('role')

        # Company info
        company_name = request.form.get('company_name')
        industry = request.form.get('industry')
        founded_date = request.form.get('founded_date')
        description = request.form.get('description')
        country = request.form.get('country')

        # Alles verplicht behalve description
        if not all([name, email, role, company_name, industry, founded_date, country]):
            return render_template("register.html", error="Gelieve alle velden in te vullen.")

        # Check email dubbel
        if User.query.filter_by(email=email).first():
            return render_template("register.html", error="Email bestaat al.")

        # Stap 1: Company aanmaken
        new_company = Company(
            name=company_name,
            industry=industry,
            founded_date=founded_date,
            description=description,
            country=country
        )
        db.session.add(new_company)
        db.session.commit()

        # Stap 2: User aanmaken gelinkt aan bedrijf
        new_user = User(
            name=name,
            email=email,
            role=role,
            company_id=new_company.id
        )
        db.session.add(new_user)
        db.session.commit()

        session['user_id'] = new_user.id

        return redirect(url_for("main.analysis"))

    return render_template("register.html")


@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        user = User.query.filter_by(email=email).first()
        if not user:
            return "Geen account gevonden."
        session['user_id'] = user.id
        return redirect(url_for("main.analysis"))
    return render_template("login.html")


@main.route('/logout', methods=['POST'])
def logout():
    session.pop('user_id', None)
    return redirect(url_for("main.index"))


@main.route('/analysis')
def analysis():
    return render_template("analysis.html")
