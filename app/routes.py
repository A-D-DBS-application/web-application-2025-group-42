from flask import Blueprint, request, redirect, url_for, render_template, session
from .models import db, User, Requirement, DataInput, Result

main = Blueprint('main', __name__)


# -----------------------
# INDEX
# -----------------------
@main.route('/')
def index():
    username = None
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        username = user.name
    return render_template("index.html", username=username)


# -----------------------
# REGISTER
# -----------------------
@main.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')

        new_user = User(
            name=name,
            email=email,
            company_id=1
        )

        db.session.add(new_user)
        db.session.commit()

        session['user_id'] = new_user.id
        return redirect(url_for("main.projects"))

    return render_template("register.html")


# -----------------------
# LOGIN
# -----------------------
@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        user = User.query.filter_by(email=email).first()

        if not user:
            return "Geen account gevonden."

        session['user_id'] = user.id
        return redirect(url_for("main.projects"))

    return render_template("login.html")


# -----------------------
# LOGOUT
# -----------------------
@main.route('/logout', methods=['POST'])
def logout():
    session.pop('user_id', None)
    return redirect(url_for("main.index"))


# -----------------------
# PROJECT OVERVIEW PAGE
# -----------------------
@main.route('/projects')
def projects():
    if 'user_id' not in session:
        return redirect(url_for("main.login"))

    user = User.query.get(session['user_id'])

    requirements = Requirement.query.filter_by(created_by=user.id).all()

    project_data = []
    for r in requirements:
        data_input = DataInput.query.filter_by(requirement_id=r.requirement_id).first()
        result = Result.query.filter_by(requirement_id=r.requirement_id).first()

        project_data.append({
            "project_id": r.requirement_id,
            "name": r.name,
            "expected_profit": data_input.expected_profit if data_input else None,
            "total_cost": data_input.total_investment_cost if data_input else None,
            "time_to_value": data_input.time_to_value if data_input else None,
            "confidence": result.confidence_value if result else None,
            "roi": result.roi_percentage if result else None
        })

    return render_template("projects.html", username=user.name, project_data=project_data)


# -----------------------
# ANALYSIS (PROJECT AANMAKEN)
# -----------------------
@main.route('/analysis', methods=['GET', 'POST'])
def analysis():
    if 'user_id' not in session:
        return redirect(url_for("main.login"))

    user = User.query.get(session['user_id'])

    if request.method == 'POST':
        project_name = request.form.get('project_name')
        expected_profit = float(request.form.get('expected_profit'))
        total_cost = float(request.form.get('total_cost'))
        confidence = float(request.form.get('confidence'))

        # ---- NIEUW: 6 SCORE-VRAGEN ----
        q1 = int(request.form.get('q1_type_product'))
        q2 = int(request.form.get('q2_complexiteit'))
        q3 = int(request.form.get('q3_teams'))
        q4 = int(request.form.get('q4_sector'))
        q5 = int(request.form.get('q5_data'))
        q6 = int(request.form.get('q6_extern'))

        total_score = q1 + q2 + q3 + q4 + q5 + q6

        # ---- Zone bepalen ----
        if total_score <= 8: zone = 1
        elif total_score <= 11: zone = 2
        elif total_score <= 14: zone = 3
        elif total_score <= 17: zone = 4
        elif total_score <= 20: zone = 5
        elif total_score <= 23: zone = 6
        elif total_score <= 26: zone = 7
        else: zone = 8

        # Requirement maken
        requirement = Requirement(
            name=project_name,
            company_id=user.company_id,
            created_by=user.id
        )
        db.session.add(requirement)
        db.session.commit()

        # DataInput maken
        data_input = DataInput(
            category="default",
            expected_profit=expected_profit,
            total_investment_cost=total_cost,
            time_to_value=zone,  # <-- OPGESLAGEN ZONE!
            company_id=user.company_id,
            requirement_id=requirement.requirement_id
        )
        db.session.add(data_input)
        db.session.commit()

        # Result maken
        result = Result(
            roi_percentage=0,
            time_to_value_days=zone,   # <-- Zelfde zone opslaan
            confidence_value=confidence,
            requirement_id=requirement.requirement_id,
            data_input_id=data_input.data_input_id
        )
        db.session.add(result)
        db.session.commit()

        return redirect(url_for("main.projects"))

    return render_template("analysis.html", username=user.name)


# -----------------------
# EDIT PROJECT
# -----------------------
@main.route('/edit/<int:project_id>', methods=['GET', 'POST'])
def edit_project(project_id):
    if 'user_id' not in session:
        return redirect(url_for("main.login"))

    requirement = Requirement.query.get(project_id)
    data_input = DataInput.query.filter_by(requirement_id=project_id).first()
    result = Result.query.filter_by(requirement_id=project_id).first()

    if request.method == 'POST':
        requirement.name = request.form.get('project_name')
        data_input.expected_profit = float(request.form.get('expected_profit'))
        data_input.total_investment_cost = float(request.form.get('total_cost'))
        result.confidence_value = float(request.form.get('confidence'))

        db.session.commit()
        return redirect(url_for("main.projects"))

    return render_template("edit_project.html",
                           requirement=requirement,
                           data_input=data_input,
                           result=result)

