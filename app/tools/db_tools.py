from app.database import SessionLocal
from app.models import WorkoutLog, NutritionLog, HealthMetric, User
from datetime import datetime

def log_workout(exercise: str, sets: int, reps: int, weight: float, user_id: int = 1):
    """Logs a workout session."""
    db = SessionLocal()
    try:
        new_log = WorkoutLog(user_id=user_id, exercise=exercise, sets=sets, reps=reps, weight=weight)
        db.add(new_log)
        db.commit()
        return f"Successfully logged {exercise}: {sets} sets of {reps} at {weight} lbs."
    except Exception as e:
        return f"Error logging workout: {str(e)}"
    finally:
        db.close()

def log_nutrition(meal_name: str, calories: int, protein: float, carbs: float, fats: float, user_id: int = 1):
    """Logs a nutrition entry."""
    db = SessionLocal()
    try:
        new_log = NutritionLog(user_id=user_id, meal_name=meal_name, calories=calories, protein=protein, carbs=carbs, fats=fats)
        db.add(new_log)
        db.commit()
        return f"Successfully logged meal: {meal_name}."
    except Exception as e:
        return f"Error logging nutrition: {str(e)}"
    finally:
        db.close()

def log_health_metric(metric_type: str, value: float, user_id: int = 1):
    """Logs a health metric like weight, heart rate, or sleep hours."""
    db = SessionLocal()
    try:
        new_log = HealthMetric(user_id=user_id, metric_type=metric_type, value=value)
        db.add(new_log)
        db.commit()
        return f"Successfully recorded {metric_type}: {value}."
    except Exception as e:
        return f"Error recording health metric: {str(e)}"
    finally:
        db.close()

def get_workout_history(user_id: int = 1, limit: int = 10):
    """Retrieves the recent workout history."""
    db = SessionLocal()
    try:
        logs = db.query(WorkoutLog).filter(WorkoutLog.user_id == user_id).order_by(WorkoutLog.date.desc()).limit(limit).all()
        return [{"exercise": log.exercise, "sets": log.sets, "reps": log.reps, "weight": log.weight, "date": log.date.isoformat()} for log in logs]
    finally:
        db.close()

def get_nutrition_history(user_id: int = 1, limit: int = 10):
    """Retrieves the recent nutrition history."""
    db = SessionLocal()
    try:
        logs = db.query(NutritionLog).filter(NutritionLog.user_id == user_id).order_by(NutritionLog.date.desc()).limit(limit).all()
        return [{"meal_name": log.meal_name, "calories": log.calories, "macros": {"p": log.protein, "c": log.carbs, "f": log.fats}, "date": log.date.isoformat()} for log in logs]
    finally:
        db.close()

def get_health_trends(metric_type: str, user_id: int = 1, limit: int = 30):
    """Retrieves trends for a specific health metric."""
    db = SessionLocal()
    try:
        metrics = db.query(HealthMetric).filter(HealthMetric.user_id == user_id, HealthMetric.metric_type == metric_type).order_by(HealthMetric.date.asc()).limit(limit).all()
        return [{"value": m.value, "date": m.date.isoformat()} for m in metrics]
    finally:
        db.close()
