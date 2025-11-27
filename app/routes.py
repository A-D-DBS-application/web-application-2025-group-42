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

        if data_input:
            internal_cost = (data_input.days_required or 0) * (data_input.worked_hours or 0) * (data_input.cost_per_hour or 0)
            total_cost = internal_cost + (data_input.extern_costs or 0) + (data_input.fixed_costs or 0)
        else:
            total_cost = None

        project_data.append({
            "project_id": r.requirement_id,
            "name": r.name,
            "total_cost": total_cost,

            # current values
            "time_to_value": data_input.time_to_value if data_input else None,
            "confidence": result.confidence_value if result else None,
            "roi": result.roi_percentage if result else None,

            # old values
            "old_time_to_value": result.old_time_to_value if result else None,
            "old_confidence": result.old_confidence_value if result else None
        })

    return render_template("projects.html", username=user.name, project_data=project_data)


# -----------------------
# ANALYSIS
# -----------------------
@main.route('/analysis', methods=['GET', 'POST'])
def analysis():
    if 'user_id' not in session:
        return redirect(url_for("main.login"))

    user = User.query.get(session['user_id'])

    if request.method == 'POST':
        project_name = request.form.get('project_name')

        days_required = float(request.form.get('days_required'))
        worked_hours = float(request.form.get('hours_per_day'))
        cost_per_hour = float(request.form.get('internal_hourly_cost'))
        extern_costs = float(request.form.get('external_costs'))
        fixed_costs = float(request.form.get('one_time_costs'))

        gained_hours = float(request.form.get('hours_saved_per_month'))
        extra_turnover = float(request.form.get('extra_revenue_per_month'))
        profit_margin = float(request.form.get('profit_margin_percent'))
        horizon = float(request.form.get('horizon_months'))

        q1 = int(request.form.get('q1_type_product'))
        q2 = int(request.form.get('q2_complexiteit'))
        q3 = int(request.form.get('q3_teams'))
        q4 = int(request.form.get('q4_sector'))
        q5 = int(request.form.get('q5_data'))
        q6 = int(request.form.get('q6_extern'))
        confidence = float(request.form.get('confidence'))

        total_score = q1 + q2 + q3 + q4 + q5 + q6

        if total_score <= 8: ttv_zone = 1
        elif total_score <= 11: ttv_zone = 2
        elif total_score <= 14: ttv_zone = 3
        elif total_score <= 17: ttv_zone = 4
        elif total_score <= 20: ttv_zone = 5
        elif total_score <= 23: ttv_zone = 6
        elif total_score <= 26: ttv_zone = 7
        else: ttv_zone = 8

        internal_cost = days_required * worked_hours * cost_per_hour
        total_investment_cost = internal_cost + extern_costs + fixed_costs

        time_saving_value = gained_hours * cost_per_hour * horizon
        revenue_profit = extra_turnover * (profit_margin / 100) * horizon

        expected_profit = time_saving_value + revenue_profit
        roi_percentage = (expected_profit / total_investment_cost) * 100 if total_investment_cost > 0 else 0

        requirement = Requirement(
            name=project_name,
            company_id=user.company_id,
            created_by=user.id
        )
        db.session.add(requirement)
        db.session.commit()

        data_input = DataInput(
            category="default",
            days_required=days_required,
            worked_hours=worked_hours,
            cost_per_hour=cost_per_hour,
            extern_costs=extern_costs,
            fixed_costs=fixed_costs,
            gained_hours=gained_hours,
            extra_turnover=extra_turnover,
            profit_margin=profit_margin,
            horizon=horizon,
            time_to_value=ttv_zone,
            company_id=user.company_id,
            requirement_id=requirement.requirement_id
        )
        db.session.add(data_input)
        db.session.commit()

        result = Result(
            roi_percentage=roi_percentage,
            time_to_value=ttv_zone,
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
        project_name = request.form.get('project_name')

        days_required = float(request.form.get('days_required'))
        worked_hours = float(request.form.get('hours_per_day'))
        cost_per_hour = float(request.form.get('internal_hourly_cost'))
        extern_costs = float(request.form.get('external_costs'))
        fixed_costs = float(request.form.get('one_time_costs'))

        gained_hours = float(request.form.get('hours_saved_per_month'))
        extra_turnover = float(request.form.get('extra_revenue_per_month'))
        profit_margin = float(request.form.get('profit_margin_percent'))
        horizon = float(request.form.get('horizon_months'))

        q1 = int(request.form.get('q1_type_product'))
        q2 = int(request.form.get('q2_complexiteit'))
        q3 = int(request.form.get('q3_teams'))
        q4 = int(request.form.get('q4_sector'))
        q5 = int(request.form.get('q5_data'))
        q6 = int(request.form.get('q6_extern'))
        confidence = float(request.form.get('confidence'))

        total_score = q1 + q2 + q3 + q4 + q5 + q6

        if total_score <= 8: ttv_zone = 1
        elif total_score <= 11: ttv_zone = 2
        elif total_score <= 14: ttv_zone = 3
        elif total_score <= 17: ttv_zone = 4
        elif total_score <= 20: ttv_zone = 5
        elif total_score <= 23: ttv_zone = 6
        elif total_score <= 26: ttv_zone = 7
        else: ttv_zone = 8

        internal_cost = days_required * worked_hours * cost_per_hour
        total_investment_cost = internal_cost + extern_costs + fixed_costs

        time_saving_value = gained_hours * cost_per_hour * horizon
        revenue_profit = extra_turnover * (profit_margin / 100) * horizon

        expected_profit = time_saving_value + revenue_profit
        new_roi = (expected_profit / total_investment_cost) * 100 if total_investment_cost > 0 else 0

        requirement.name = project_name

        data_input.days_required = days_required
        data_input.worked_hours = worked_hours
        data_input.cost_per_hour = cost_per_hour
        data_input.extern_costs = extern_costs
        data_input.fixed_costs = fixed_costs
        data_input.gained_hours = gained_hours
        data_input.extra_turnover = extra_turnover
        data_input.profit_margin = profit_margin
        data_input.horizon = horizon
        data_input.time_to_value = ttv_zone

        # SAVE OLD VALUES
        result.old_roi_percentage = result.roi_percentage
        result.old_confidence_value = result.confidence_value
        result.old_time_to_value = result.time_to_value

        # SAVE NEW VALUES
        result.roi_percentage = new_roi
        result.confidence_value = confidence
        result.time_to_value = ttv_zone

        db.session.commit()

        return redirect(url_for("main.projects"))

    return render_template(
        "edit_project.html",
        requirement=requirement,
        data_input=data_input,
        result=result
    )


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

    if result:
        db.session.delete(result)
    if data_input:
        db.session.delete(data_input)
    if requirement:
        db.session.delete(requirement)

    db.session.commit()

    return redirect(url_for('main.projects'))
