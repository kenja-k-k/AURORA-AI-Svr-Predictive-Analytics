import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_squared_error
import argparse
from sklearn.tree import DecisionTreeRegressor as DTR
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
import matplotlib.dates as mdates

#Live display of CO2 capture efficiency
def CO2_stats(data, facility_name):
    filtered = data[data["facility_name"] == facility_name].dropna(
        subset=["co2_emitted_tonnes", "capture_efficiency_percent"]
    )
    filtered["date"] = pd.to_datetime(filtered["date"], format="%d/%m/%Y", dayfirst=True)

    normal  = filtered[filtered["anomaly_flag"] == False]
    anomalies = filtered[filtered["anomaly_flag"] == True]
    graph   = plt.figure(figsize=(16,9))
    plt.plot(filtered["date"], filtered["capture_efficiency_percent"], label="Capture efficiency", color="blue")

    #plt.scatter(normal["date"], normal["capture_efficiency_percent"], label="Normal", color="green")
    plt.scatter(anomalies["date"], anomalies["capture_efficiency_percent"], label="Anomaly", color="red")
    
    plt.xlabel("Date")
    plt.xlim(filtered["date"].min(), filtered["date"].max())

    plt.ylabel("Efficiency")
    plt.ylim(bottom=0)
    plt.title(f"Efficiency tracking for {facility_name}")
    plt.legend()
    
    return graph, filtered[["date", "co2_captured_tonnes", "capture_efficiency_percent"]]
#_______________________________

#Seasonal Forecasts__________________
def get_dates_data (data, start_date, end_date): #This one is not in use for now
    
    data = data.copy()
    data["date"] = pd.to_datetime(data["date"], format="%d/%m/%Y", dayfirst=True)
    
    start = pd.to_datetime(start_date, format="%d/%m/%Y", dayfirst=True)
    end = pd.to_datetime(end_date, format="%d/%m/%Y", dayfirst=True)
    
    filtered = data[(data["date"] >= start) & (data["date"] <= end)]
    return filtered

def seasonify(data, start_month, end_month):

    data = data.copy()
    # Ensure 'date' is datetime
    data["date"] = pd.to_datetime(data["date"], format="%m/%d/%Y", dayfirst=True)
    data["month"] = data["date"].dt.month

    if start_month <= end_month:
        # Normal range within the year
        mask = (data["month"] >= start_month) & (data["month"] <= end_month)
    else:
        # Cross-year range (like dec to feb)
        mask = (data["month"] >= start_month) | (data["month"] <= end_month)

    filtered = data[mask]
    return filtered

def seasonal_emission_forecasts(data, facility_name):
    filtered = data[data["facility_name"] == facility_name].dropna(
        subset=["co2_emitted_tonnes", "co2_captured_tonnes", "capture_efficiency_percent"]
    )

    # Use the month-only version of seasonify
    summer_stats = seasonify(filtered, 5, 9)
    autumn_stats = seasonify(filtered, 10, 11)
    winter_stats = seasonify(filtered, 12, 2)
    spring_stats = seasonify(filtered, 3, 4)

    cols = ["co2_emitted_tonnes", "co2_captured_tonnes"]

    rows = []

    for season_name, df in [("Summer", summer_stats),
                            ("Autumn", autumn_stats),
                            ("Winter", winter_stats),
                            ("Spring", spring_stats)]:
        med = df[cols].median()
        lower = med * 0.9
        upper = med * 1.1

        for col in cols:
            rows.append({
                "season": season_name,
                "column": col,
                "median": med[col],
                "lower": lower[col],
                "upper": upper[col]
            })

    # Convert list of dicts to DataFrame
    ranges = pd.DataFrame(rows)

    
    plt.figure(figsize=(12,6))
    
    for col in cols:

        #medians = ranges[ranges["column"] == col]["median"]
        lowers = ranges[ranges["column"] == col]["lower"]
        uppers = ranges[ranges["column"] == col]["upper"]
        seasons = ranges[ranges["column"] == col]["season"]

        # Expected Range
        plt.fill_between(seasons, lowers, uppers, alpha=0.2, label=f"{col}")

    plt.xlabel("Season")
    plt.ylabel("CO2 stats")
    plt.title(f"Seasonal CO2 ranges for {facility_name}")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    
    # Save the figure object to return
    graph = plt.gcf()
    return ranges

#___________________________


#Main function for analytics. This may use different models_________
def CO2_emssion_pattern(data, facility_name, plot=False, scatter=False):
    filtered = data[data["facility_name"] == facility_name].dropna(
        subset=["co2_emitted_tonnes", "capture_efficiency_percent"]
    )

    if filtered.empty:
        print(f"No data found for facility: {facility_name}")
        return None, None

    features = filtered[["co2_emitted_tonnes"]]
    target = filtered["capture_efficiency_percent"]

    model = Ridge()
    model.fit(features, target)
    predictions = model.predict(features)
    correlation_matrix = np.corrcoef(target, predictions)
    correlation_coef = correlation_matrix[0, 1]
    print(f"Correlation coef = {correlation_coef}")
    graph = None
    if plot:
      
        graph = plt.figure(figsize=(16, 9))
        if scatter:
            plt.scatter(features["co2_emitted_tonnes"], target, label="Actual", color="blue")
        plt.plot(features["co2_emitted_tonnes"], predictions, label="Regression line", color="red", linewidth=2.5)
        plt.xlabel("Emissions (tonnes)")
        plt.ylabel("Capture Efficiency (%)")
        plt.title(f"{facility_name}: Emissions vs Capture Efficiency")
        plt.legend()
        #plt.show()  #not needed for now
        

    return model, graph, correlation_coef
#__________________________________________________________________

#DTR for multivariable calculations__________________
def CO2_emission_pattern_DTR(data, facility_name, plot=False, scatter = False):
    filtered = data[data["facility_name"] == facility_name].dropna(subset=["co2_emitted_tonnes", "capture_efficiency_percent"])
    if filtered.empty:
        print(f"Data not found for the input facility name ({facility_name})")
        return None, None

    features = filtered[["region", "storage_site_type", "co2_emitted_tonnes"]]
    target   = filtered["capture_efficiency_percent"]

    preprocessor = ColumnTransformer(        #Need one-hot encoding, so using preprocessor
        transformers=[
            ("types", OneHotEncoder(handle_unknown="ignore"), ["region", "storage_site_type"]),
            ("num", "passthrough", ["co2_emitted_tonnes"])
        ]
    )

    model = Pipeline(steps=[("Preprocessor", preprocessor), 
    ("Regressor", DTR(random_state = 42, max_depth = 5))])

    model.fit(features, target)

    one_hot = model.named_steps["Preprocessor"].named_transformers_["types"]
    one_hot_features = one_hot.get_feature_names_out(["region","storage_site_type"])
    all_features = list(one_hot_features) + ["co2_emitted_tonnes"]

    importances = model.named_steps["Regressor"].feature_importances_

    importance_df = pd.DataFrame({
    "Features": all_features,
    "Importances": importances
    }).sort_values(by="Importances", ascending=False)

    print(importance_df)

    return model, importance_df
#______________________________________
        

#Run from cli______________________________
if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(description="Get emission patterns per facility")
    parser.add_argument("csv_file", type=str, help="Path to the csv with emission data")
    parser.add_argument("--facility", type=str, help="Facility name", required=True)
    parser.add_argument("--plot", action="store_true", help="Plot L2 for analytics")
    parser.add_argument("--scatter", action="store_true", help="Get the scatter plot along with L2")
    args = parser.parse_args()
    data = pd.read_csv(args.csv_file)
    #CO2_emssion_pattern(data, args.facility, plot=args.plot, scatter=args.scatter)
    CO2_emission_pattern_DTR(data, args.facility, plot=args.plot, scatter=args.scatter)
    
    #_________________________________________________________