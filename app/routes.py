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

        # ------------------------
        # FORM DATA
        # ------------------------
        project_name = request.form.get('project_name')

        # ROI COST INPUTS
        days_required = float(request.form.get('days_required'))
        hours_per_day = float(request.form.get('hours_per_day'))
        internal_hourly_cost = float(request.form.get('internal_hourly_cost'))
        external_costs = float(request.form.get('external_costs'))
        one_time_costs = float(request.form.get('one_time_costs'))

        # ROI PROFIT INPUTS
        hours_saved_per_month = float(request.form.get('hours_saved_per_month'))
        extra_revenue_per_month = float(request.form.get('extra_revenue_per_month'))
        profit_margin_percent = float(request.form.get('profit_margin_percent'))
        horizon_months = float(request.form.get('horizon_months'))

        # TIME TO VALUE QUESTIONS
        q1 = int(request.form.get('q1_type_product'))
        q2 = int(request.form.get('q2_complexiteit'))
        q3 = int(request.form.get('q3_teams'))
        q4 = int(request.form.get('q4_sector'))
        q5 = int(request.form.get('q5_data'))
        q6 = int(request.form.get('q6_extern'))

        confidence = float(request.form.get('confidence'))

        # ------------------------
        # TIME TO VALUE ZONE BEREKENEN
        # ------------------------
        total_score = q1 + q2 + q3 + q4 + q5 + q6

        if total_score <= 8: zone = 1
        elif total_score <= 11: zone = 2
        elif total_score <= 14: zone = 3
        elif total_score <= 17: zone = 4
        elif total_score <= 20: zone = 5
        elif total_score <= 23: zone = 6
        elif total_score <= 26: zone = 7
        else: zone = 8

        # ------------------------
        # ROI BEREKENEN
        # ------------------------

        # Totale kost
        internal_cost = days_required * hours_per_day * internal_hourly_cost
        total_cost = internal_cost + external_costs + one_time_costs

        # Expected profit (enkel omzetwinst, tijdsbesparing niet meegerekend)
        expected_profit = (
            extra_revenue_per_month * (profit_margin_percent / 100)
        ) * horizon_months

        # ROI percentage
        roi_percentage = (expected_profit / total_cost) * 100 if total_cost > 0 else 0

        # ------------------------
        # REQUIREMENT OPSLAAN
        # ------------------------
        requirement = Requirement(
            name=project_name,
            company_id=user.company_id,
            created_by=user.id
        )
        db.session.add(requirement)
        db.session.commit()

        # ------------------------
        # DATA INPUT OPSLAAN
        # ------------------------
        data_input = DataInput(
            category="default",
            expected_profit=expected_profit,
            total_investment_cost=total_cost,
            time_to_value=zone,
            company_id=user.company_id,
            requirement_id=requirement.requirement_id
        )
        db.session.add(data_input)
        db.session.commit()

        # ------------------------
        # RESULT (ROI) OPSLAAN
        # ------------------------
        result = Result(
            roi_percentage=roi_percentage,
            time_to_value_days=zone,
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
        result.confidence_value = float(request.form.get('confidence'))

        db.session.commit()
        return redirect(url_for("main.projects"))

    return render_template("edit_project.html",
                           requirement=requirement,
                           data_input=data_input,
                           result=result)



# -----------------------
# DELETE PROJECT
# -----------------------
@main.route('/delete/<int:project_id>', methods=['POST'])
def delete_project(project_id):
    if 'user_id' not in session:
        return redirect(url_for("main.login"))

    requirement = Requirement.query.get(project_id)
    data_input = DataInput.query.filter_by(requirement_id=project_id).first()
    result = Result.query.filter_by(requirement_id=project_id).first()

    # In juiste volgorde verwijderen om foreign keys te respecteren
    if result:
        db.session.delete(result)
    if data_input:
        db.session.delete(data_input)
    if requirement:
        db.session.delete(requirement)

    db.session.commit()

    return redirect(url_for('main.projects'))
