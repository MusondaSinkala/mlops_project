from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import mlflow
import mlflow.sklearn
import pandas as pd
from prometheus_fastapi_instrumentator import Instrumentator

# Configure MLflow tracking URI
mlflow.set_tracking_uri("http://129.114.26.77:8000")

# Load latest model from MLflow by name
model = mlflow.sklearn.load_model("models:/player_cluster_model/Production")

# Define FastAPI app
app = FastAPI(
    title="Player Cluster API",
    description="API to classify soccer players into clusters",
    version="1.0.0"
)

# Define expected fields for input
class PlayerRequest(BaseModel):
    passing_accuracy: float
    shooting_accuracy: float
    minutes_played: float
    tackles: float
    interceptions: float
    aerial_duels_won: float
    sprint_speed: float
    stamina: float
    # Add all feature fields expected by the clustering model

class ClusterPredictionResponse(BaseModel):
    cluster: int

@app.post("/predict-cluster", response_model=ClusterPredictionResponse)
def predict_cluster(player: PlayerRequest):
    try:
        # Convert input to DataFrame
        player_df = pd.DataFrame([player.dict()])

        # Run inference
        cluster = model.predict(player_df)[0]

        return ClusterPredictionResponse(cluster=int(cluster))

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Inference error: {str(e)}")

# Enable Prometheus metrics
Instrumentator().instrument(app).expose(app)
