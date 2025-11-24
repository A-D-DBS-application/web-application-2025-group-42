from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid

db = SQLAlchemy()


class Company(db.Model):
    __tablename__ = "company"

    id = db.Column(db.BigInteger, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    industry = db.Column(db.String(255))
    founded_date = db.Column(db.Date)
    description = db.Column(db.Text)
    country = db.Column(db.String(255))

    # relaties
    users = db.relationship("User", back_populates="company", lazy="dynamic")
    requirements = db.relationship("Requirement", back_populates="company", lazy="dynamic")
    data_inputs = db.relationship("DataInput", back_populates="company", lazy="dynamic")

    def __repr__(self):
        return f"<Company {self.name}>"


class User(db.Model):
    __tablename__ = "user"

    id = db.Column(db.BigInteger, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, index=True, nullable=False)
    role = db.Column(db.String(100))
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
    # kolomnaam in Supabase is "company" (zonder _id)
    company_id = db.Column("company", db.BigInteger, db.ForeignKey("company.id"))

    company = db.relationship("Company", back_populates="users")
    requirements_created = db.relationship(
        "Requirement", back_populates="created_by_user", lazy="dynamic"
    )

    def __repr__(self):
        return f"<User {self.email}>"


class Requirement(db.Model):
    __tablename__ = "requirement"

    requirement_id = db.Column(db.BigInteger, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    company_id = db.Column(db.BigInteger, db.ForeignKey("company.id"), nullable=False)
    created_by = db.Column(db.BigInteger, db.ForeignKey("user.id"), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())

    company = db.relationship("Company", back_populates="requirements")
    created_by_user = db.relationship("User", back_populates="requirements_created")
    data_inputs = db.relationship("DataInput", back_populates="requirement", lazy="dynamic")
    results = db.relationship("Result", back_populates="requirement", lazy="dynamic")

    def __repr__(self):
        return f"<Requirement {self.name}>"


class DataInput(db.Model):
    __tablename__ = "data_input"

    data_input_id = db.Column(db.BigInteger, primary_key=True)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
    analysis_id = db.Column(
        UUID(as_uuid=True),
        default=uuid.uuid4,
        nullable=False
    )
    category = db.Column(db.String(255))
    expected_profit = db.Column(db.Float)
    total_investment_cost = db.Column(db.Float)
    company_id = db.Column(db.BigInteger, db.ForeignKey("company.id"), nullable=False)
    requirement_id = db.Column(
        db.BigInteger, db.ForeignKey("requirement.requirement_id"), nullable=False
    )
    time_to_market_days = db.Column(db.Integer)
    time_to_business_days = db.Column(db.Integer)

    company = db.relationship("Company", back_populates="data_inputs")
    requirement = db.relationship("Requirement", back_populates="data_inputs")
    results = db.relationship("Result", back_populates="data_input", lazy="dynamic")

    def __repr__(self):
        return f"<DataInput {self.data_input_id}>"


class Result(db.Model):
    __tablename__ = "results"

    id = db.Column(db.BigInteger, primary_key=True)
    roi_percentage = db.Column(db.Float)
    time_to_value_days = db.Column(db.Integer)
    confidence_value = db.Column(db.Float)
    created_at = db.Column(db.Date)
    requirement_id = db.Column(
        db.BigInteger, db.ForeignKey("requirement.requirement_id"), nullable=False
    )
    data_input_id = db.Column(
        db.BigInteger, db.ForeignKey("data_input.data_input_id"), nullable=False
    )

    requirement = db.relationship("Requirement", back_populates="results")
    data_input = db.relationship("DataInput", back_populates="results")

    def __repr__(self):
        return f"<Result {self.id}>"
