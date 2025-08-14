<h1>On demand CO2 analytics</h1>
This project is a FastAPI-based service for managing and analyzing CO2 emission data. 
It allows users to upload a CSV dataset, update with entries, and generate analytical insights with a model (currently L2), 
including an optional plot.

<h2>Usage</h2>
The environment.yml contains all the dependencies. Use it to make a venv with conda.
Alternatively, use the requirements.txt to build a windows venv.
Start the service.py using uvicorn.

<h2>Endpoints</h2>
<ul>
  <li><b>set_csv: </b>This endpoint initializes the service by setting the path to the CSV file. It must be called before anything, 
    all other endpoints rely on the loaded dataset. If the CSV file doesn't exist, it will be created with the correct headers.</li>
  
  <li><b>update_csv: </b>This endpoint initializes the service by setting the path to the CSV file. It must be called before anything, 
    all other endpoints rely on the loaded dataset. If the CSV file doesn't exist, it will be created with the correct headers.</li>
    
  <li><b>get_insights: </b>This endpoint performs an L2 on the loaded data for a specific facility. 
    It returns a <b>base64 encoded PNG</b> string of the plot showing the relationship between emissions and capture efficiency.</li>
</ul>

<h2>Request Formats</h2>
The request formats are given as follows.
<ul>
  <li><b>For set_csv: </b> The local address of the csv.</li>
  <li><b>For update_csv: </b> The JSON in the given format.<br> 
{
  "date": "2025-08-15",
  "facility_id": "F-A01",
  "facility_name": "Alpha CCS Plant",
  "country": "USA",
  "region": "Texas",
  "storage_site_type": "Saline Aquifer",
  "co2_emitted_tonnes": 12500.5,
  "co2_captured_tonnes": 11000.2,
  "co2_stored_tonnes": 10980.1,
  "capture_efficiency_percent": 88.0,
  "storage_integrity_percent": 99.8
                                      }</li>
  <li><b>For get_insights: </b>The GET request needs to have the facility name and the bool for "scatter".<br> 
</ul>
