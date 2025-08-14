from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pandas as pd
import os

app = FastAPI(title="CSV Update Service")

#Initialize the csv as nothing___________
data = pd.DataFrame()
csv_path = None
#___________________________


#Expected format for requests___________________________
class GlobalInput(BaseModel):
    date: str
    facility_id: str
    facility_name: str
    country: str
    region: str
    storage_site_type: str
    co2_emitted_tonnes: float | None = None
    co2_captured_tonnes: float | None = None
    co2_stored_tonnes: float | None = None
    capture_efficiency_percent: float | None = None
    storage_integrity_percent: float | None = None
#___________________________



# endpoint to set csv
@app.post("/set_csv/")
def set_csv(path: str):
    global csv_path, data
    csv_path = path
    if os.path.exists(csv_path):
        data = pd.read_csv(csv_path)
        
        if "anomaly_flag" not in data.columns:# check if anomaly_flag exists
            data["anomaly_flag"] = False
    else:
        columns = list(GlobalInput.schema()["properties"].keys()) + ["anomaly_flag"]
        data = pd.DataFrame(columns=columns)
        data.to_csv(csv_path, index=False)
    return {"status": "success", "message": f"CSV path set to {csv_path}"}
#___________________________


# endpoint for updates
@app.post("/update/")
def update_csv(entry: GlobalInput):
    global data, csv_path
    if csv_path is None:
        raise HTTPException(status_code=400, detail="CSV path not set. Use /set_csv/ before anythong.")
    
    entry_dict = entry.dict()
    entry_dict["anomaly_flag"] = any(value is None for value in entry_dict.values()) # Set the flag anomaly to True if any value is None
    new_entry = pd.DataFrame([entry_dict])
    data = pd.concat([data, new_entry], ignore_index=True) #append the pd df in memory
    new_entry.to_csv(csv_path, mode="a", header=False, index=False) #append current CSV on disk
    
    return {"status": "success", "message": f"Data added to {csv_path}", "anomaly_flag": entry_dict["anomaly_flag"]}
#___________________________
