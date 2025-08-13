from fastapi import FastAPI
from pydantic import BaseModel
import pandas as pd
import os

csv_path = input("Input the address of the target CSV: ").strip()

app = FastAPI()

class global_input(BaseModel):
    date: str
    facility_id: str
    facility_name: str
    country: str
    region: str
    storage_site_type: str
    co2_emitted_tonnes: float
    co2_captured_tonnes: float
    co2_stored_tonnes: float
    capture_efficiency_percent: float
    storage_integrity_percent: float

@app.post("/update")
def update_csv(entry: global_input):
    new_entry = pd.DataFrame([entry.dict()])
    
    # Append to CSV if exists, otherwise create new
    if os.path.exists(csv_path):
        new_entry.to_csv(csv_path, mode="a", header=False, index=False)
    else:
        new_entry.to_csv(csv_path, mode="w", header=True, index=False)
    
    return {"status": "success", "message": f"Data added to {csv_path}"}
