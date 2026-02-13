import torch
import torch.nn as nn
import joblib
import os
import uvicorn
import numpy as np
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from preprocess import URLExtractor
from train import PhishingSentinelModel
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Sentinel Intelligence API")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

MODEL = None
SCALER = None
EXTRACTOR = URLExtractor()

def load_assets():
    global MODEL, SCALER
    try:
        # Check current working directory to find models folder
        base_path = os.path.dirname(os.path.abspath(__file__))
        models_dir = os.path.join(os.path.dirname(base_path), "models")
        
        m_path = os.path.join(models_dir, "sentinel_v1.pth")
        s_path = os.path.join(models_dir, "scaler.pkl")
        
        SCALER = joblib.load(s_path)
        MODEL = PhishingSentinelModel(input_size=41)
        # map_location ensures it works on CPU even if trained on GPU
        MODEL.load_state_dict(torch.load(m_path, map_location=torch.device('cpu')))
        MODEL.eval()
        print("[Sentinel] Model and Scaler loaded successfully.")
    except Exception as e:
        print(f"[Sentinel] Error loading assets: {e}")

class AnalysisRequest(BaseModel):
    url: str
    dom_content: str = ""

@app.on_event("startup")
async def startup_event():
    load_assets()

@app.post("/analyze")
async def analyze(request: AnalysisRequest):
    if MODEL is None or SCALER is None:
        raise HTTPException(status_code=500, detail="Assets not loaded")

    # 1. Extract raw features
    raw_features = EXTRACTOR.extract_features(request.url)
    
    # 2. Scale Features
    # If this isn't working, the model receives massive numbers and outputs 1.0
    features_scaled = SCALER.transform(raw_features)
    
    # DEBUG: See the first 5 scaled features in terminal
    print(f"Scaled Sample: {features_scaled[0][:5]}")

    features_tensor = torch.FloatTensor(features_scaled)

    # 3. Predict
    with torch.no_grad():
        output = MODEL(features_tensor)
        confidence = output.item()
    
    print(f"URL: {request.url} | AI Score: {confidence:.4f}")

    # Increase threshold to 0.8 for higher precision
    is_spoof = confidence > 0.8 
    threat_level = "high" if confidence > 0.95 else "medium" if is_spoof else "low"
    
    return {
        "is_spoof": is_spoof,
        "confidence_score": confidence,
        "threat_level": threat_level,
        "detected_anomalies": ["Lexical Pattern Anomaly"] if is_spoof else []
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)