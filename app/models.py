from . import db
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
import uuid


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

    users = db.relationship("User", back_populates="company", lazy="dynamic")
    requirements = db.relationship("Requirement", back_populates="company", lazy="dynamic")
    data_inputs = db.relationship("DataInput", back_populates="company", lazy="dynamic")


# -----------------------
# USER
# -----------------------
class User(db.Model):
    __tablename__ = "user"

    id = db.Column(db.BigInteger, primary_key=True)
    name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False)
    role = db.Column(db.String, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())

    # Supabase FK = column "company"
    company_id = db.Column("company", db.BigInteger, db.ForeignKey("company.id"), nullable=False)

    company = db.relationship("Company", back_populates="users")
    requirements_created = db.relationship("Requirement", back_populates="created_by_user", lazy="dynamic")


# -----------------------
# REQUIREMENT (PROJECT)
# -----------------------
class Requirement(db.Model):
    __tablename__ = "requirement"

    requirement_id = db.Column(db.BigInteger, primary_key=True)
    name = db.Column(db.String)
    company_id = db.Column(db.BigInteger, db.ForeignKey("company.id"))
    created_by = db.Column(db.BigInteger, db.ForeignKey("user.id"))
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())

    company = db.relationship("Company", back_populates="requirements")
    created_by_user = db.relationship("User", back_populates="requirements_created")

    data_inputs = db.relationship("DataInput", back_populates="requirement", lazy="dynamic")
    results = db.relationship("Result", back_populates="requirement", lazy="dynamic")


# -----------------------
# DATA INPUT
# -----------------------
class DataInput(db.Model):
    __tablename__ = "data_input"

    data_input_id = db.Column(db.BigInteger, primary_key=True)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
    analysis_id = db.Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False)
    category = db.Column(db.String, nullable=False, default="")
    expected_profit = db.Column(db.Float)
    total_investment_cost = db.Column(db.Float)
    company_id = db.Column(db.BigInteger, db.ForeignKey("company.id"), nullable=False)
    requirement_id = db.Column(db.BigInteger, db.ForeignKey("requirement.requirement_id"))
    time_to_value = db.Column(db.BigInteger)

    company = db.relationship("Company", back_populates="data_inputs")
    requirement = db.relationship("Requirement", back_populates="data_inputs")

    results = db.relationship("Result", back_populates="data_input", lazy="dynamic")


# -----------------------
# RESULT
# -----------------------
class Result(db.Model):
    __tablename__ = "results"

    id = db.Column(db.BigInteger, primary_key=True)
    roi_percentage = db.Column(db.Float)
    time_to_value_days = db.Column(db.BigInteger)
    confidence_value = db.Column(db.Float)
    created_at = db.Column(db.Date)

    requirement_id = db.Column(db.BigInteger, db.ForeignKey("requirement.requirement_id"))
    data_input_id = db.Column(db.BigInteger, db.ForeignKey("data_input.data_input_id"))

    requirement = db.relationship("Requirement", back_populates="results")
    data_input = db.relationship("DataInput", back_populates="results")
