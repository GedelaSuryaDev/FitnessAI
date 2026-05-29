from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    age = Column(Integer)
    weight = Column(Float)
    height = Column(Float)
    goals = Column(Text)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class WorkoutLog(Base):
    __tablename__ = "workout_logs"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    exercise = Column(String, index=True)
    sets = Column(Integer)
    reps = Column(Integer)
    weight = Column(Float)
    date = Column(DateTime, default=datetime.datetime.utcnow)
    
    user = relationship("User")

class NutritionLog(Base):
    __tablename__ = "nutrition_logs"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    meal_name = Column(String)
    calories = Column(Integer)
    protein = Column(Float)
    carbs = Column(Float)
    fats = Column(Float)
    date = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User")

class HealthMetric(Base):
    __tablename__ = "health_metrics"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    metric_type = Column(String) # e.g., 'weight', 'heart_rate', 'sleep'
    value = Column(Float)
    date = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User")
