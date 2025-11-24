from flask import Blueprint, request, redirect, url_for, render_template, session
from .models import db, User

main = Blueprint('main', __name__)


@main.route('/')
def index():
    """Homepage: toon eventueel de naam van de ingelogde user."""
    username = None
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        if user:
            username = user.name

    # Je index.html kan hier bijvoorbeeld een welkomstscherm tonen
    return render_template('index.html', username=username)


@main.route('/register', methods=['GET', 'POST'])
def register():
    """Registratie: nieuwe user opslaan in je Supabase-database via SQLAlchemy."""
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')

        # Check of email al bestaat
        if User.query.filter_by(email=email).first():
            return "Email is already registered."

        new_user = User(
            name=name,
            email=email,
            password_hash=""  # voorlopig nog niet gebruikt
        )

        db.session.add(new_user)
        db.session.commit()

        session['user_id'] = new_user.id

        # Na registratie naar analysis (of waar je wil)
        return redirect(url_for('main.analysis'))

    return render_template('register.html')


@main.route('/login', methods=['GET', 'POST'])
def login():
    """Login op basis van e-mailadres (nog zonder wachtwoordcontrole)."""
    if request.method == 'POST':
        email = request.form.get('email')

        user = User.query.filter_by(email=email).first()
        if not user:
            return "No account found with that email."

        session['user_id'] = user.id
        return redirect(url_for('main.analysis'))

    return render_template('login.html')


@main.route('/logout', methods=['POST'])
def logout():
    """Uitloggen: user_id uit de sessie verwijderen."""
    session.pop('user_id', None)
    return redirect(url_for('main.index'))


@main.route('/analysis')
def analysis():
    """Placeholder-pagina voor je analyse-flow."""
    return render_template('analysis.html')
