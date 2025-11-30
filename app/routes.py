from flask import Blueprint, request, redirect, url_for, render_template, session
from .models import db, User, Company, Requirement, DataInput, Results
from sqlalchemy.sql import func

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

        # USER FIELDS
        name = request.form.get('name')
        email = request.form.get('email')

        # COMPANY FIELDS
        company_name = request.form.get('company_name')
        industry = request.form.get('industry')
        founded_date = request.form.get('founded_date')
        description = request.form.get('description')
        country = request.form.get('country')

        # CREATE COMPANY
        new_company = Company(
            name=company_name,
            industry=industry,
            founded_date=founded_date,
            description=description,
            country=country
        )
        db.session.add(new_company)
        db.session.commit()

        # CREATE USER
        new_user = User(
            name=name,
            email=email,
            company=new_company.id
        )
        db.session.add(new_user)
        db.session.commit()

        session['user_id'] = new_user.id
        return redirect(url_for("main.projects"))
    countries = [
    "Afghanistan", "Albania", "Algeria", "Andorra", "Angola",
    "Argentina", "Armenia", "Australia", "Austria", "Azerbaijan",
    "Bahamas", "Bahrain", "Bangladesh", "Belgium", "Belize",
    "Benin", "Bhutan", "Bolivia", "Bosnia and Herzegovina",
    "Botswana", "Brazil", "Brunei", "Bulgaria", "Burkina Faso",
    "Burundi", "Cambodia", "Cameroon", "Canada", "Cape Verde",
    "Chile", "China", "Colombia", "Costa Rica", "Croatia",
    "Cuba", "Cyprus", "Czech Republic", "Denmark", "Djibouti",
    "Dominican Republic", "Ecuador", "Egypt", "El Salvador",
    "Estonia", "Eswatini", "Ethiopia", "Fiji", "Finland",
    "France", "Gabon", "Gambia", "Georgia", "Germany",
    "Ghana", "Greece", "Guatemala", "Haiti", "Honduras",
    "Hungary", "Iceland", "India", "Indonesia", "Iran",
    "Iraq", "Ireland", "Israel", "Italy", "Jamaica",
    "Japan", "Jordan", "Kazakhstan", "Kenya",
    "Kuwait", "Kyrgyzstan", "Laos", "Latvia", "Lebanon",
    "Lesotho", "Liberia", "Libya", "Lithuania",
    "Luxembourg", "Madagascar", "Malawi", "Malaysia",
    "Maldives", "Mali", "Malta", "Mauritania", "Mauritius",
    "Mexico", "Moldova", "Monaco", "Mongolia", "Montenegro",
    "Morocco", "Mozambique", "Myanmar", "Namibia", "Nepal",
    "Netherlands", "New Zealand", "Nicaragua", "Niger", "Nigeria",
    "North Korea", "North Macedonia", "Norway", "Oman", "Pakistan",
    "Panama", "Paraguay", "Peru", "Philippines", "Poland",
    "Portugal", "Qatar", "Romania", "Russia", "Rwanda",
    "Saudi Arabia", "Senegal", "Serbia", "Seychelles",
    "Sierra Leone", "Singapore", "Slovenia", "Somalia",
    "South Africa", "South Korea", "Spain", "Sri Lanka",
    "Sudan", "Suriname", "Sweden", "Switzerland",
    "Syria", "Taiwan", "Tajikistan", "Tanzania",
    "Thailand", "Tunisia", "Turkey", "Uganda", "Ukraine",
    "United Arab Emirates", "United Kingdom", "United States",
    "Uruguay", "Uzbekistan", "Venezuela", "Vietnam",
    "Yemen", "Zambia", "Zimbabwe"
]
    return render_template("register.html", countries=countries)


# -----------------------
# LOGIN
# -----------------------
@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        user = User.query.filter_by(email=email).first()

        if not user:
            return redirect(url_for('main.register'))

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
        result = Results.query.filter_by(requirement_id=r.requirement_id).first()

        # total project cost
        if data_input:
            internal_cost = (data_input.days_required or 0) * (data_input.worked_hours or 0) * (data_input.cost_per_hour or 0)
            total_cost = internal_cost + (data_input.extern_costs or 0) + (data_input.fixed_costs or 0)
        else:
            total_cost = None

        project_data.append({
            "project_id": r.requirement_id,
            "name": r.name,
            "total_cost": total_cost,
            "confidence": result.confidence_value if result else None,
            "time_to_value": result.time_to_value if result else None,
            "roi": result.roi_percentage if result else None,
            "old_confidence": result.old_confidence_value if result else None,
            "old_time_to_value": result.old_time_to_value if result else None,
            "old_roi": result.old_roi_percentage if result else None,
        })

    return render_template("projects.html", username=user.name, project_data=project_data)


# ------------------------------------------------------------
# TIME TO VALUE SCORE → LINEAIRE INTERPOLATIE
# ------------------------------------------------------------
def calculate_ttv_score(benchmark_1, benchmark_5, benchmark_10, ttv):

    # buiten de range → clampen
    if ttv <= benchmark_1:
        return 1
    if ttv >= benchmark_10:
        return 10

    # tussen score 1 en score 5
    if ttv <= benchmark_5:
        return 1 + ( (ttv - benchmark_1) / (benchmark_5 - benchmark_1) ) * 4

    # tussen score 5 en score 10
    return 5 + ( (ttv - benchmark_5) / (benchmark_10 - benchmark_5) ) * 5


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

        # COST
        days_required = int(request.form.get('days_required'))
        worked_hours = int(request.form.get('hours_per_day'))
        cost_per_hour = float(request.form.get('internal_hourly_cost'))
        extern_costs = float(request.form.get('external_costs'))
        fixed_costs = float(request.form.get('one_time_costs'))

        # PROFIT
        gained_hours = int(request.form.get('hours_saved_per_month'))
        extra_turnover = float(request.form.get('extra_revenue_per_month'))
        profit_margin = float(request.form.get('profit_margin_percent'))
        horizon = float(request.form.get('horizon_months'))

        # BENCHMARKS
        benchmark_1 = int(request.form.get('benchmark_1'))
        benchmark_5 = int(request.form.get('benchmark_5'))
        benchmark_10 = int(request.form.get('benchmark_10'))


        # TIME INPUTS
        time_to_market = float(request.form.get('time_to_market'))
        time_to_business = float(request.form.get('time_to_business'))

        ttv_sum = time_to_market + time_to_business
        ttv_score = calculate_ttv_score(benchmark_1, benchmark_5, benchmark_10, ttv_sum)

        confidence = float(request.form.get('confidence'))

        # ROI
        internal_cost = days_required * worked_hours * cost_per_hour
        total_investment_cost = internal_cost + extern_costs + fixed_costs

        time_saving_value = gained_hours * cost_per_hour * horizon
        revenue_profit = extra_turnover * (profit_margin / 100) * horizon
        expected_profit = time_saving_value + revenue_profit

        roi_percentage = (expected_profit / total_investment_cost) * 100 if total_investment_cost > 0 else 0

        # REQUIREMENT
        requirement = Requirement(
            name=project_name,
            company_id=user.company,
            created_by=user.id
        )
        db.session.add(requirement)
        db.session.commit()

        # DATA INPUT
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

            benchmark_1=benchmark_1,
            benchmark_5=benchmark_5,
            bench_mark_10=benchmark_10,

            company_id=user.company,
            requirement_id=requirement.requirement_id
        )
        db.session.add(data_input)
        db.session.commit()

        # RESULT
        result = Results(
            roi_percentage=roi_percentage,
            time_to_value=ttv_score,
            confidence_value=confidence,

            old_roi_percentage=None,
            old_confidence_value=None,
            old_time_to_value=None,

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
    result = Results.query.filter_by(requirement_id=project_id).first()

    if request.method == 'POST':

        project_name = request.form.get('project_name')
        requirement.name = project_name

        # COST
        days_required = int(request.form.get('days_required'))
        worked_hours = int(request.form.get('hours_per_day'))
        cost_per_hour = float(request.form.get('internal_hourly_cost'))
        extern_costs = float(request.form.get('external_costs'))
        fixed_costs = float(request.form.get('one_time_costs'))

        # PROFIT
        gained_hours = int(request.form.get('hours_saved_per_month'))
        extra_turnover = float(request.form.get('extra_revenue_per_month'))
        profit_margin = float(request.form.get('profit_margin_percent'))
        horizon = float(request.form.get('horizon_months'))

        # BENCHMARKS (NIEUW)
        benchmark_1 = data_input.benchmark_1
        benchmark_5 = data_input.benchmark_5
        benchmark_10 = data_input.bench_mark_10


        # TIME
        time_to_market = float(request.form.get('time_to_market'))
        time_to_business = float(request.form.get('time_to_business'))
        ttv_sum = time_to_market + time_to_business
        ttv_score = calculate_ttv_score(benchmark_1, benchmark_5, benchmark_10, ttv_sum)

        confidence = float(request.form.get('confidence'))

        # ROI
        internal_cost = days_required * worked_hours * cost_per_hour
        total_cost = internal_cost + extern_costs + fixed_costs

        time_saving_value = gained_hours * cost_per_hour * horizon
        revenue_profit = extra_turnover * (profit_margin / 100) * horizon
        expected_profit = time_saving_value + revenue_profit

        new_roi = (expected_profit / total_cost) * 100 if total_cost > 0 else 0

        # UPDATE DATA INPUT
        data_input.days_required = days_required
        data_input.worked_hours = worked_hours
        data_input.cost_per_hour = cost_per_hour
        data_input.extern_costs = extern_costs
        data_input.fixed_costs = fixed_costs
        data_input.gained_hours = gained_hours
        data_input.extra_turnover = extra_turnover
        data_input.profit_margin = profit_margin
        data_input.horizon = horizon

        data_input.benchmark_1 = benchmark_1
        data_input.benchmark_5 = benchmark_5
        data_input.bench_mark_10 = benchmark_10

        # SAVE OLD VALUES
        result.old_roi_percentage = result.roi_percentage
        result.old_confidence_value = result.confidence_value
        result.old_time_to_value = result.time_to_value

        # UPDATE NEW VALUES
        result.roi_percentage = new_roi
        result.time_to_value = ttv_score
        result.confidence_value = confidence

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
    result = Results.query.filter_by(requirement_id=project_id).first()

    if result:
        db.session.delete(result)
    if data_input:
        db.session.delete(data_input)
    if requirement:
        db.session.delete(requirement)

    db.session.commit()

    return redirect(url_for('main.projects'))
