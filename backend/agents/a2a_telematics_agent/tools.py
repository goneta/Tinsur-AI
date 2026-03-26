
from google.adk.tools import tool
from app.core.database import SessionLocal
from app.models.telematics import TelematicsData
import uuid
from datetime import datetime, timedelta
import random
from app.services.telematics_service import TelematicsService

@tool
def get_driving_stats(policy_id: str) -> str:
    """
    Retrieves the latest driving statistics and safety score for a given policy.
    Args:
        policy_id: The UUID of the policy (UBI).
    """
    db = SessionLocal()
    try:
        # Get the latest trip
        data = db.query(TelematicsData).filter(TelematicsData.policy_id == uuid.UUID(policy_id)).order_by(TelematicsData.trip_date.desc()).first()
        
        if not data:
            return f"No telematics data found for policy {policy_id}."
            
        return (f"Latest Driving Stats for Policy {policy_id} ({data.trip_date}):\n"
                f"- Distance: {data.distance_km} km\n"
                f"- Safety Score: {data.safety_score}/100\n"
                f"- Harsh Braking: {data.harsh_braking_count} times\n"
                f"- Harsh Acceleration: {data.harsh_acceleration_count} times\n"
                f"- Night Driving: {data.night_driving_km} km")
    except Exception as e:
        return f"Error retrieving driving stats: {str(e)}"
    finally:
        db.close()

@tool
def get_safety_recommendations(policy_id: str) -> str:
    """
    Analyzes historical telematics data and provides personalized safety tips.
    Args:
        policy_id: The UUID of the policy (UBI).
    """
    db = SessionLocal()
    try:
        # Get last 5 trips
        trips = db.query(TelematicsData).filter(TelematicsData.policy_id == uuid.UUID(policy_id)).order_by(TelematicsData.trip_date.desc()).limit(5).all()
        
        if not trips:
             return "No driving history available to generate recommendations."
        
        avg_score = sum([(t.safety_score or 0) for t in trips]) / len(trips)
        total_braking = sum([(t.harsh_braking_count or 0) for t in trips])
        
        recommendations = [f"Your current average safety score is {avg_score:.1f}/100."]
        
        if total_braking > 5:
            recommendations.append("- Tip: Try to anticipate stops earlier to reduce harsh braking events.")
        
        if any((t.night_driving_km or 0) > 50 for t in trips):
            recommendations.append("- Tip: Night driving increases risk. Consider planning trips during daylight hours when possible.")
            
        if avg_score > 90:
            recommendations.append("- Great job! Keep maintaining your safe driving habits for potential premium discounts.")
        
        return "Safety Insights:\n" + "\n".join(recommendations)
    except Exception as e:
        return f"Error generating recommendations: {str(e)}"
    finally:
        db.close()

@tool
def simulate_trip(policy_id: str) -> str:
    """
    Simulates a driving trip for a policy to generate telematics data.
    Useful for testing UBI scoring updates and demonstrating safety features.
    
    Args:
        policy_id: The UUID of the policy (UBI).
    """
    db = SessionLocal()
    try:
        service = TelematicsService(db)
        
        # Generate varied trip data
        distance = random.randint(5, 50)
        avg_speed = random.randint(30, 100)
        max_speed = avg_speed + random.randint(5, 30)
        
        # Determine safety events based on "random" driver behavior profiles
        profile = random.choice(['safe', 'aggressive', 'normal'])
        
        hard_brakes = 0
        rapid_accel = 0
        
        if profile == 'aggressive':
            hard_brakes = random.randint(1, 4)
            rapid_accel = random.randint(1, 5)
            max_speed += 20
        elif profile == 'normal':
             hard_brakes = random.randint(0, 1)
             rapid_accel = random.randint(0, 2)
        
        service_payload = {
            "device_id": "SIM-AGENT-001",
            "distance_km": distance,
            "avg_speed": avg_speed,
            "max_speed": max_speed,
            "harsh_braking_count": hard_brakes,
            "harsh_acceleration_count": rapid_accel,
            "night_driving_km": 0 if random.random() > 0.2 else random.randint(1, distance)
        }
        
        result = service.process_trip_data(uuid.UUID(policy_id), service_payload)
        
        # Get updated score
        new_score = service.calculate_safety_score(uuid.UUID(policy_id))
        
        return (f"Trip simulated successfully!\n"
                f"- Profile: {profile.capitalize()}\n"
                f"- Distance: {distance}km\n"
                f"- Safety Score for this trip: {result.safety_score}\n"
                f"- Updated Policy Safety Score: {new_score:.1f}")
                
    except Exception as e:
        return f"Error simulating trip: {str(e)}"
    finally:
        db.close()
