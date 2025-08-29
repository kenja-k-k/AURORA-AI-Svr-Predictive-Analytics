<h1>Predictive analytics</h1>
This project is a fastapi based service for managing and analyzing CO2 emission data. 
It allows users to upload a CSV dataset, update with entries, and generate analytical insights with a model (currently L2), 
including an optional plot.

<h2>Usage</h2>
Use the requirements.txt to install all the necessary dependencies
The main entry point for the app is ```grpc_server.py``` which is gRPC server file with endpoints.
The app can be run in Docker by runing: 
```docker-compose build --no-cache``` to build the docker image 
then ```docker-compose up -d``` it will start the container.

The endpoints will be available at ```lochalhost:50051```

In order to test the service in Postman, you need to make sure to choose gRPC instead of HTTP. Postman requires .proto definition files
for methods and messages. Upload the file ```protos/service.proto``` that is available in the repo. This will allow Postman to identify endpoints 
that are used.
Example: ```localhost:50051/UploadCSV```

<h2>Endpoints</h2>
There are two main endpoints that are currently exposed and are ready for use:
<ul>
  <li><b> UploadCSV </b> This endpoint accepts a CSV file in base64 format as a string.
    
    ```localhost:50051/UploadCSV```
    ```{ "file_content": "base64 string here" }```
    
  </li>
    
  <li><b>GetSeasonalStats</b> This endpoint is for a function that function calculates and visualizes seasonal CO₂ emission and capture forecasts for a specific facility.
    
   ```localhost:50051/GetSeasonalStats```
   ```{ "facility_name": "Facility Name Here" }```

   <b>The process behind GetSeasonalStats</b>
   This process trains a regression model on the provided data after the training it does the follwoing:
       1. Filters the data;  
       2. Splits data into seasons (based on months). A helper function extracts seasonal subset of data on a given date range (by months);  
       3. Calculates median emission / capture values per season and defines +-10 range around those medians (lower/upper bounds);  
       4. Builds data points that can be used for plot / graph construction on the frontend;  
       <b>Main purpose</b>: Identifying seasonal trends in CO₂ emissions and capture efficiency at a facility, and to quickly spot when values fall outside the expected range as well as predicting future trends based on the historical data and seasonality.
    </li>
</ul>
