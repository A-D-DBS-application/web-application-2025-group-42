from . import db
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid


# -----------------------
# ALEMBIC VERSION
# -----------------------
class AlembicVersion(db.Model):
    __tablename__ = "alembic_version"

    version_num = db.Column(db.String, primary_key=True)


# -----------------------
# COMPANY
# -----------------------
class Company(db.Model):
    __tablename__ = "company"

    id = db.Column(db.BigInteger, primary_key=True)
    name = db.Column(db.String, nullable=False, default="")
    industry = db.Column(db.String, nullable=False, default="")
    founded_date = db.Column(db.Date, nullable=False)
    description = db.Column(db.Text)
    country = db.Column(db.String, nullable=False)

    # Relationships
    users = db.relationship("User", backref="company_rel", lazy=True)
    requirements = db.relationship("Requirement", backref="company_rel", lazy=True)
    data_inputs = db.relationship("DataInput", backref="company_rel", lazy=True)


# -----------------------
# USER
# -----------------------
class User(db.Model):
    __tablename__ = "user"

    id = db.Column(db.BigInteger, primary_key=True)
    name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())

    # FK TO COMPANY
    company = db.Column(db.BigInteger, db.ForeignKey("company.id"), nullable=False)

    # Relationship
    requirements = db.relationship("Requirement", backref="creator_rel", lazy=True)


# -----------------------
# REQUIREMENT
# -----------------------
class Requirement(db.Model):
    __tablename__ = "requirement"

    requirement_id = db.Column(db.BigInteger, primary_key=True)
    name = db.Column(db.String)

    company_id = db.Column(db.BigInteger, db.ForeignKey("company.id"))
    created_by = db.Column(db.BigInteger, db.ForeignKey("user.id"))

    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())

    # Relationships
    data_inputs = db.relationship("DataInput", backref="requirement_rel", lazy=True)
    results = db.relationship("Results", backref="requirement_rel", lazy=True)


# -----------------------
# DATA INPUT
# -----------------------
class DataInput(db.Model):
    __tablename__ = "data_input"

    data_input_id = db.Column(db.BigInteger, primary_key=True)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())

    analysis_id = db.Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False)

    category = db.Column(db.String, nullable=False, default="")

    days_required = db.Column(db.BigInteger)
    worked_hours = db.Column(db.BigInteger)

    company_id = db.Column(db.BigInteger, db.ForeignKey("company.id"), nullable=False)
    requirement_id = db.Column(db.BigInteger, db.ForeignKey("requirement.requirement_id"))

    benchmark_1 = db.Column(db.BigInteger)
    benchmark_5 = db.Column(db.BigInteger)
    bench_mark_10 = db.Column(db.BigInteger)

    cost_per_hour = db.Column(db.Float)
    extern_costs = db.Column(db.Float)
    fixed_costs = db.Column(db.Float)
    gained_hours = db.Column(db.BigInteger)
    extra_turnover = db.Column(db.Float)
    profit_margin = db.Column(db.Float)
    horizon = db.Column(db.Float)

    # Relationship
    results = db.relationship("Results", backref="data_input_rel", lazy=True)


# -----------------------
# RESULTS
# -----------------------
class Results(db.Model):
    __tablename__ = "results"

    id = db.Column(db.BigInteger, primary_key=True)

    roi_percentage = db.Column(db.Float)
    time_to_value = db.Column(db.BigInteger)
    confidence_value = db.Column(db.Float)
    created_at = db.Column(db.Date)

    requirement_id = db.Column(db.BigInteger, db.ForeignKey("requirement.requirement_id"))
    data_input_id = db.Column(db.BigInteger, db.ForeignKey("data_input.data_input_id"))

    old_roi_percentage = db.Column(db.Float)
    old_confidence_value = db.Column(db.Float)
    old_time_to_value = db.Column(db.BigInteger)
