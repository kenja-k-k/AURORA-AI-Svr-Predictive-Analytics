from fastapi import FastAPI, HTTPException, UploadFile, File
from pydantic import BaseModel
import pandas as pd
import os
import base64
from io import BytesIO
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timezone

app = FastAPI(title="CSV Update Service")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import the analytics function from the insights.py file
from insights import CO2_emssion_pattern



#Initialize the csv as nothing___________
data = pd.DataFrame()
csv_path = None
#___________________________


# Expected format for requests___________________________
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


# endpoint to upload from frontend____________
@app.post("/upload_csv/")
async def upload_csv(file: UploadFile = File(...)):
    global csv_path, data
     
    timestamp = datetime.now().astimezone().strftime("%Y-%m-%d_%H-%M-%S_%Z")
    csv_path = f"./{timestamp}_{file.filename}" #save file to local dir
    with open(csv_path, "wb") as f:
        f.write(await file.read())

    data = pd.read_csv(csv_path) #data is now the uploaded csv
    """
    if "anomaly_flag" not in data.columns: #check if the anomaly_flag field even exists
        data["anomaly_flag"] = False
        data.to_csv(csv_path, index=False)
    """
    return {"status": "success", "message": f"Your csv has been uploaded, and saved to {csv_path}"}
#___________________________


# endpoint to a set csv that exists the server___________
@app.post("/use_csv/")
async def use_csv(csv_name: str):
    global csv_path, data
    
    csv_path = fr".\{csv_name}" 
    if os.path.exists(csv_path):

        data = pd.read_csv(csv_path)
        return {f"CSV data set to local path on server: {csv_path}"}
    else:
        return {"error": "CSV not found on server. Please check the file name."}

#__________________________________

# endpoint to a print a csv that exists the server___________
    """
    This is very slow right now, because a lot of rows need to be transformed or dropped
    will try to find a bette way to do this.
    """
@app.get("/get_csv/")
async def use_csv(csv_name: str):
    global csv_path, data
    
    csv_path = fr".\{csv_name}" 
    if os.path.exists(csv_path):

        data = pd.read_csv(csv_path)
        data = data.fillna("") 
        return data.to_dict(orient="records")
    else:
        return {"error": "CSV not found on server. Please check the file name."}

#__________________________________

# endpoint for updates
@app.post("/update_csv/")
async def update_csv(entry: GlobalInput):
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


# endpoint to get only the plot image
@app.get("/get_insights/")
async def get_insights_plot(facility_name: str, scatter: bool = False):
    global csv_path, data
    if csv_path is None:
        raise HTTPException(status_code=400, detail="CSV path not set. Use /set_csv/ before anything.")
    
    if data.empty:
        raise HTTPException(status_code=400, detail="No csv loaded. Use /set_csv/ before anything.")

    # Call the CO2_emssion_pattern. For now, only returning the plot. Might modify the response in future commits
    model, graph = CO2_emssion_pattern(data, facility_name=facility_name, plot=True, scatter=scatter)

    if graph is None:
        raise HTTPException(status_code=404, detail=f"No data for {facility_name}.")
    
    """
    Converting the img from the CO2_emssion_pattern() into b64, 
    because cant send a matplot directly.
    This can be decoded to get the actual plot on the front end.
    """

    buf = BytesIO()
    graph.savefig(buf, format="png")
    buf.seek(0)
    plot_base64 = base64.b64encode(buf.getvalue()).decode("utf-8")

    return {plot_base64}
#___________________________