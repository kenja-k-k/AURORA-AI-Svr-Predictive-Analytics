from fastapi import FastAPI, UploadFile, File, HTTPException
import pandas as pd
from pydantic import BaseModel
from sklearn.linear_model import Ridge
import matplotlib.pyplot as plt
import io
import base64
from fastapi.responses import JSONResponse

app = FastAPI(title="CO2 analytics service")

# Upload csv before anything
data = pd.DataFrame()  # initialize as empty pd df

@app.post("/upload_csv/")
def upload_csv(file: UploadFile = File(...)):
    global data
    try:
        data = pd.read_csv(file.file)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Can't read csv: {e}")
    return {"csv": file.filename, "status": "loaded"}


class CO2Request(BaseModel):
    facility_name: str
    plot: bool = False
    scatter: bool = False


@app.post("/co2_pattern/")
def get_co2_pattern(request: CO2Request):
    if data.empty:
        raise HTTPException(status_code=400, detail="CSV data not uploaded yet")

    filtered = data[data["facility_name"] == request.facility_name].dropna(
        subset=["co2_emitted_tonnes", "capture_efficiency_percent"]
    )

    if filtered.empty:
        raise HTTPException(status_code=404, detail="Facility not found")

    features = filtered[["co2_emitted_tonnes"]]
    target = filtered["capture_efficiency_percent"]

    model = Ridge()
    model.fit(features, target)

    plot_base64 = None
    if request.plot:
        predictions = model.predict(features)
        plt.figure(figsize=(16, 9))

        if request.scatter:
            plt.scatter(features["co2_emitted_tonnes"], target, label="Actual", color="blue")

        plt.plot(features["co2_emitted_tonnes"], predictions, label="Regression line", color="red", linewidth=2.5)
        plt.xlabel("Emissions (tonnes)")
        plt.ylabel("Capture Efficiency (%)")
        plt.title(f"{request.facility_name}: Emissions vs Capture Efficiency")
        plt.legend()

        # Save plot to a bytes buffer, because getting error if raw img
        buf = io.BytesIO()
        plt.savefig(buf, format="png")
        plt.close()
        buf.seek(0)
        plot_base64 = base64.b64encode(buf.read()).decode("utf-8")

    return JSONResponse({
        "facility_name": request.facility_name,
        "regression_coefficient": model.coef_[0],
        "regression_intercept": model.intercept_,
        "plot": plot_base64  # base64 string of the plot img
    })
