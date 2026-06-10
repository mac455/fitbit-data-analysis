import joblib 
import pandas as pd 
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel 
from fastapi.middleware.cors import CORSMiddleware
from database import supabase

app = FastAPI(title="Fitness AI pipeline API")


app.add_middleware(
    CORSMiddleware, 
    allow_origins=["*"],
    allow_credentials=True, 
    allow_methods=["*"], 
    allow_headers=["*"], 
)

try: 
    model = joblib.load("step_goal_classifier.pkl")
    print ("Model Loaded Success")
except Exception as e: 
    print(f"Failed to Load ML Model: Details{e}")


class TelemetryInput(BaseModel): 
    client_id: str 
    activity_date: str 
    total_calories: float 
    max_intensity: float 
    total_intensity: float
    avg_intensity: float 
    calorie_intensity_ratio: float

@app.get("/clients")
async def get_clients(): 
    try: 
        response = supabase.table("clients").select("id, first_name, last_name").execute()
        return response.data
    except Exception as e: 
        raise HTTPException(status_code=500, detail=f"Failed to get clients data: Details {str(e)}")
    

@app.post("/predict")
async def predict_and_log_activity(data:TelemetryInput):
    if model is None: 
        raise HTTPException(status_code=500, detail="Inference engine unavailable: ML model binary not loaded")
    
    calorie_intensity_ratio = data.total_calories / (data.total_intensity + 1)

# Need to recreate the dataframe 
    input_df = pd.DataFrame([{
        "Total_Calories": data.total_calories, 
        "Total_Intensity": data.total_intensity, 
        "Max_Intensity": data.max_intensity, 
        "Avg_Intensity": data.avg_intensity, 
        "Calorie_Intensity_Ratio": calorie_intensity_ratio
}])
    
    try: 
        prediction = int(model.predict(input_df)[0])
        probabilities = model.predict_proba(input_df)[0]
        confidence = float(probabilities[prediction])

        telemetry_payload = {
            "client_id": data.client_id,
            "activity_date": data.activity_date,
            "total_calories": data.total_calories,
            "max_intensity": data.max_intensity,
            "calorie_intensity_ratio": calorie_intensity_ratio
        }
        telemetry_res = supabase.table("client_telemetry").insert(telemetry_payload).execute()
        
        # Extract the auto-generated primary key (id) from the newly created telemetry row
        telemetry_id = telemetry_res.data[0]["id"]
        
        # Part B: Insert the generated model prediction, linking it via foreign key
        prediction_payload = {
            "telemetry_id": telemetry_id,
            "predicted_goal_achieved": prediction,
            "prediction_probability": confidence,
            "model_version": "gradient_boosting_v1.0"
        }
        supabase.table("ml_predictions").insert(prediction_payload).execute()
        
        # --- STEP 5: SUCCESSFUL PIPELINE RESPONSE ---
        return {
            "status": "success",
            "telemetry_id": telemetry_id,
            "prediction_results": {
                "is_step_goal_predicted": prediction,  # 1 = Achieved, 0 = Missed
                "confidence_score": round(confidence, 4)
            }
        }
    except Exception as e: 
        raise HTTPException(status_code=400,detail=f"Pipeline Processing Exception: {str(e)}")