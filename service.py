from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi import Request
from fastapi.responses import StreamingResponse
import asyncio
from pydantic import BaseModel
import pandas as pd
import os
import base64
from io import BytesIO
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timezone, timedelta

# Import the analytics function from the local insights.py file
from insights import CO2_emssion_pattern, CO2_stats, seasonal_emission_forecasts

app = FastAPI(title="CSV Update Service")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)





#Initialize the csv as nothing___________
data = pd.DataFrame()
csv_path = None
#___________________________


# Expected format for requests___________________________
class GlobalInput(BaseModel):
    date                        : str
    facility_id                 : str
    facility_name               : str
    country                     : str
    region                      : str
    storage_site_type           : str
    co2_emitted_tonnes          : float | None = None
    co2_captured_tonnes         : float | None = None
    co2_stored_tonnes           : float | None = None
    capture_efficiency_percent  : float | None = None
    storage_integrity_percent   : float | None = None
    #anomaly_flag                :
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


#For streaming graphs___________________
fronts = []
@app.get("/graph_stream/")
async def graph_stream(facility_name: str):
    async def event_generator():
        queue = asyncio.Queue()
        fronts.append((queue, facility_name))

        try:
            while True:
                graph_base64 = await queue.get()
                yield f"data: {graph_base64}\n\n"
        finally:
            fronts.remove((queue, facility_name))

    return StreamingResponse(event_generator(), media_type="text/event-stream")

async def graph_update():
    for queue, facility in fronts:
        graph = CO2_stats(data, facility)
        buf = BytesIO()
        graph.savefig(buf, format="png")
        buf.seek(0)
        graph_base64 = base64.b64encode(buf.getvalue()).decode("utf-8")
        await queue.put(graph_base64)
#___________________


#To update the csv___________________________
@app.post("/update_csv/")
async def update_csv(entry: GlobalInput):
    global data, csv_path
    if csv_path is None:
        raise HTTPException(status_code=400, detail="CSV path not set. Use /set_csv/ before anything.")

    entry_dict = entry.dict()

    
    anomaly_flag = any(value is None for value in entry_dict.values()) # flag missing values beforehand

    
    model, _, _ = CO2_emssion_pattern(data, entry_dict["facility_name"], plot=False, scatter=False) # Train the model for facility

    predicted = None
    if model is not None:
        predicted = model.predict([[entry_dict["co2_emitted_tonnes"]]])[0]
        
        if entry_dict["capture_efficiency_percent"] <= 0.9 * predicted: # Permissable range
            anomaly_flag = True

    entry_dict["anomaly_flag"] = anomaly_flag

    new_entry = pd.DataFrame([entry_dict])
    data = pd.concat([data, new_entry], ignore_index=True)
    new_entry.to_csv(csv_path, mode="a", header=False, index=False)

    await graph_update()
    return {
        "status": "success",
        "message": f"Data added to {csv_path}",
        "anomaly_flag": anomaly_flag,
        "predicted_efficiency": predicted
    }
#________________________________________


# endpoint for live tracking with every csv update___________
@app.get("/get_graph/")
async def efficiency_tracking_graph(facility_name: str, nums: bool = False):
    global csv_path, data
    if csv_path is None:
        raise HTTPException(status_code=400, detail="CSV path not set. Use /set_csv/ before anything.")
    
    graph, numbers = CO2_stats(data, facility_name)
    if graph is None:
        raise HTTPException(status_code=404, detail=f"No data for {facility_name}.")
    
    buf = BytesIO()
    graph.savefig(buf, format="png")
    buf.seek(0)
    plot_base64 = base64.b64encode(buf.getvalue()).decode("utf-8")

    if nums == True:
        return {plot_base64}, numbers

    else: return {plot_base64}

#__________________________________

#for seasonal stats
@app.get("/get_seasonal_stats/")
async def get_seasonal_stats(facility_name: str, plot: bool = False):
    global csv_path, data

    if csv_path is None:
        raise HTTPException(status_code=400, detail="CSV path not set. Use /set_csv/ before anything.")
    
    stats, graph = seasonal_emission_forecasts(data, facility_name)
    if graph is None:
        raise HTTPException(status_code=404, detail=f"No data for {facility_name}.")

    buf = BytesIO()
    graph.savefig(buf, format="png")
    buf.seek(0)
    plot_base64 = base64.b64encode(buf.getvalue()).decode("utf-8")

    if plot == True:
        return {plot_base64}, stats

    else: return stats
#_________________________________


# endpoint to get only the plot image______________________
@app.get("/get_insights/")
async def get_insights_plot(facility_name: str, scatter: bool = False):
    global csv_path, data
    if csv_path is None:
        raise HTTPException(status_code=400, detail="CSV path not set. Use /set_csv/ before anything.")
    
    if data.empty:
        raise HTTPException(status_code=400, detail="No csv loaded. Use /set_csv/ before anything.")

    # Call the CO2_emssion_pattern. For now, only returning the plot. Might modify the response in future commits
    model, graph, _ = CO2_emssion_pattern(data, facility_name=facility_name, plot=True, scatter=scatter)

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