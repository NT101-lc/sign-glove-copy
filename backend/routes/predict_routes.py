from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from core.model import predict_gesture
from models.sensor_models import SensorData

router = APIRouter(prefix="/gesture", tags=["gesture"])

@router.post("/predict")
async def predict(sensor_data: SensorData):
    """
    Predict gesture from a single sensor data input.
    """
    try:
        # Run inference (synchronously is fine for demo)
        first_sample = sensor_data.sensor_values[0]
        prediction = predict_gesture(first_sample)
        return JSONResponse(
            status_code=200,
            content={
                "status": "success",
                "prediction": prediction,
                "session_id": sensor_data.session_id
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")
