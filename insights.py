import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_squared_error


def CO2_emssion_pattern(facility_name, plot = False, scatter = False):

  filtered = data2[data2["facility_name"] == facility_name].dropna(subset=["co2_emitted_tonnes", "capture_efficiency_percent"])
  features = filtered[["co2_emitted_tonnes"]]
  target   = filtered["capture_efficiency_percent"]

  model = Ridge()
  model.fit(features,target)

  graph = None
  if plot == True:
    predictions = model.predict(features)
    graph = plt.figure(figsize=(16,9))
    plt.scatter(target, label="Actual", color="blue") if scatter == True else None
    plt.plot(features["co2_emitted_tonnes"], predictions, label="Regression line", color="red", linewidth=2.5)
    plt.xlabel("Emissions")
    plt.ylabel("Capture Efficiency %")
    plt.title(f"Emission and Capture Efficiency")
    plt.legend()

    plt.show()


  return model, graph