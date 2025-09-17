# IMPORTS: Bringing in the tools we need
# -------------------------------

import pandas as pd               # Tool for handling tabular data (spreadsheets, CSVs)
import numpy as np                # Tool for working with numbers
import matplotlib.pyplot as plt   # Tool for plotting graphs, Shortcut to make charts and graphs
from sklearn.linear_model import Ridge                  # Machine Learning model: Ridge Regression (used to find patterns/relationships)
from sklearn.metrics import mean_squared_error          # Tool to measure how accurate the model’s predictions are
import argparse                   # Tool that lets us run the code from the command line with arguments
from sklearn.tree import DecisionTreeRegressor as DTR   # Another ML model (Decision Tree Regression)
from sklearn.preprocessing import OneHotEncoder         # Converts text categories into numeric form
from sklearn.compose import ColumnTransformer           # Combines numeric + text processing
from sklearn.pipeline import Pipeline                   # Chains together data processing steps
import matplotlib.dates as mdates                       # For formatting dates on graphs

# -------------------------------------------------------------------------------------
# FUNCTION 1: Live CO₂ Stats (efficiency over time + anomalies)
# What it does: Shows capture efficiency of a facility over time and highlights anomalies.

def CO2_stats(data, facility_name):                         # STEP 1: Filter for the requested facility + drop rows with missing values
    filtered = data[data["facility_name"] == facility_name].dropna(
        subset=["co2_emitted_tonnes", "capture_efficiency_percent"]
    )
    filtered["date"] = pd.to_datetime(filtered["date"], format="%d/%m/%Y", dayfirst=True)     # STEP 2: Convert 'date' column into proper date format

    normal  = filtered[filtered["anomaly_flag"] == False]   # STEP 3: Split into normal rows and anomaly-flagged rows
    anomalies = filtered[filtered["anomaly_flag"] == True]
    graph   = plt.figure(figsize=(16,9))                    # STEP 4: Create a line plot of capture efficiency
    plt.plot(filtered["date"], filtered["capture_efficiency_percent"], label="Capture efficiency", color="blue")

    #plt.scatter(normal["date"], normal["capture_efficiency_percent"], label="Normal", color="green")      # STEP 5: Overlay anomalies in red
    plt.scatter(anomalies["date"], anomalies["capture_efficiency_percent"], label="Anomaly", color="red")
    
    plt.xlabel("Date")                                      # STEP 6: Add labels/titles
    plt.xlim(filtered["date"].min(), filtered["date"].max())

    plt.ylabel("Efficiency")
    plt.ylim(bottom=0)
    plt.title(f"Efficiency tracking for {facility_name}")
    plt.legend()
    
    return graph, filtered[["date", "co2_captured_tonnes", "capture_efficiency_percent"]]             # STEP 7: Output = (graph, cleaned dataset with key columns)

# -------------------------------------------------------------------------------------
# FUNCTION 2: Seasonal Forecasts (expected ranges ±10%)

def get_dates_data (data, start_date, end_date): #This one is not in use for now
    
    data = data.copy()
    data["date"] = pd.to_datetime(data["date"], format="%d/%m/%Y", dayfirst=True)
    
    start = pd.to_datetime(start_date, format="%d/%m/%Y", dayfirst=True)
    end = pd.to_datetime(end_date, format="%d/%m/%Y", dayfirst=True)
    
    filtered = data[(data["date"] >= start) & (data["date"] <= end)]
    return filtered

def seasonify(data, start_month, end_month):         # Helper function: Assigns rows to a season based on month.

    data = data.copy()
    # Ensure 'date' is datetime
    data["date"] = pd.to_datetime(data["date"], format="%d/%m/%Y", dayfirst=True)
    data["month"] = data["date"].dt.month

    if start_month <= end_month:
        # Normal range within the year
        mask = (data["month"] >= start_month) & (data["month"] <= end_month)
    else:
        # Cross-year range (like dec to feb)
        mask = (data["month"] >= start_month) | (data["month"] <= end_month)

    filtered = data[mask]
    return filtered

def seasonal_emission_forecasts(data, facility_name):         # Groups a facility’s data into seasons and calculates median ranges.
    filtered = data[data["facility_name"] == facility_name].dropna(                  # STEP 1: Filter facility + drop rows with missing values
        subset=["co2_emitted_tonnes", "co2_captured_tonnes", "capture_efficiency_percent"]
    )

    # Use the month-only version of seasonify
    summer_stats = seasonify(filtered, 5, 9)                       # STEP 2: Split data into seasons
    autumn_stats = seasonify(filtered, 10, 11)
    winter_stats = seasonify(filtered, 12, 2)
    spring_stats = seasonify(filtered, 3, 4)

    cols = ["co2_emitted_tonnes", "co2_captured_tonnes"]           # STEP 3: For each season, calculate median ±10%

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

    ranges = pd.DataFrame(rows)          # STEP 4: Create summary table, Convert list of dicts to DataFrame

    
    plt.figure(figsize=(12,6))           # STEP 5: Plot shaded seasonal ranges
    
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
    return ranges                         # STEP 6: Output = summary table of ranges

# -------------------------------------------------------------------------------------
# FUNCTION 3: Ridge Regression (emission vs efficiency)
# What it does: Fits a Ridge Regression model to find relationship between CO₂ emissions and capture efficiency.

#Main function for analytics. This may use different models_________
def CO2_emssion_pattern(data, facility_name, plot=False, scatter=False):
    filtered = data[data["facility_name"] == facility_name].dropna(             # STEP 1: Filter rows for facility + drop missing values
        subset=["co2_emitted_tonnes", "capture_efficiency_percent"]
    )

    if filtered.empty:
        print(f"No data found for facility: {facility_name}")
        return None, None

    features = filtered[["co2_emitted_tonnes"]]              # STEP 2: Define input = emissions, target = efficiency
    target = filtered["capture_efficiency_percent"]

    model = Ridge()                                          # STEP 3: Train Ridge Regression model
    model.fit(features, target)
    predictions = model.predict(features)                    # STEP 4: Make predictions + calculate correlation
    correlation_matrix = np.corrcoef(target, predictions)
    correlation_coef = correlation_matrix[0, 1]
    print(f"Correlation coef = {correlation_coef}")
    graph = None                                             # STEP 5: Optional graph
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
        

    return model, graph, correlation_coef                    # STEP 6: Output = trained model + correlation value
# -------------------------------------------------------------------------------------
# FUNCTION 4: Next-Month Forecasts (30-day predictions)
# What it does: Predicts next 30 days of:
    """
    - CO₂ emissions
    - Capture efficiency
    - Storage integrity
    Based on last year’s same period.
    """

def predict_following_month_emission(data, facility_name):
    filtered = data[data["facility_name"] == facility_name].dropna(            # STEP 1: Filter facility rows + clean dates
        subset=["co2_emitted_tonnes", "capture_efficiency_percent", "storage_integrity_percent", "date"]
    )
    if filtered.empty:
        print(f"No data found for facility: {facility_name}")
        return None, None
    filtered["date"] = pd.to_datetime(filtered["date"], errors="coerce").dt.normalize()
    filtered = filtered.dropna(subset=["date"])
    today = pd.Timestamp.today().normalize()                                   # STEP 2: Define "this year" vs "last year" time window
    end_date = today + pd.Timedelta(days=30)
    last_year_today = today - pd.DateOffset(years=1)
    last_year_end = end_date - pd.DateOffset(years=1)
    range_filtered = filtered[(filtered["date"] >= last_year_today) & (filtered["date"] <= last_year_end)].copy()               # STEP 3: Extract last year’s data for the window

    if range_filtered.empty:
        print("No data in the next 30 days.")
        return None
    results = range_filtered.copy()
    pc_features = range_filtered[["co2_emitted_tonnes"]]                # STEP 4: Train Ridge models for each variable
    pc_target = range_filtered["capture_efficiency_percent"]

    pc_model = Ridge() #pc - predict capture                            # (a) Capture efficiency vs emissions
    pc_model.fit(pc_features, pc_target)
    results["predicted_capture_percent"] = pc_model.predict(pc_features)

    ps_features = range_filtered[["co2_emitted_tonnes"]]
    ps_target = range_filtered["storage_integrity_percent"]

    ps_model = Ridge() # ps - predict storage                            # (b) Storage integrity vs emissions
    ps_model.fit(ps_features, ps_target)
    results["predicted_storage_percent"] = ps_model.predict(ps_features)

    range_filtered["month"] = range_filtered["date"].dt.month
    range_filtered["day"] = range_filtered["date"].dt.day
    pe_features = range_filtered[["month", "day"]]                       # (c) Emissions vs day-of-year (month + day)
    pe_target = range_filtered["co2_emitted_tonnes"]

    pe_model = Ridge() # pe - predicted emission
    pe_model.fit(pe_features, pe_target)
    results["predicted_co2_emitted"] = pe_model.predict(pe_features)
    results["date"] = results["date"].apply(lambda d: d.replace(year=2025) if pd.notnull(d) else d)             # STEP 5: Shift predictions to current year
    results["date_range"] = results["date"]

    return results                                                 # STEP 6: Output = DataFrame of next 30 days predictions

# -------------------------------------------------------------------------------------
# FUNCTION 5: Decision Tree Regression (multi-variable), "DTR for multivariable calculations"
# Inputs: region, storage site type, emissions.
# Output: capture efficiency + feature importance.

def CO2_emission_pattern_DTR(data, facility_name, plot=False, scatter = False):
    filtered = data[data["facility_name"] == facility_name].dropna(subset=["co2_emitted_tonnes", "capture_efficiency_percent"])             # STEP 1: Filter + clean
    if filtered.empty:
        print(f"Data not found for the input facility name ({facility_name})")
        return None, None

    features = filtered[["region", "storage_site_type", "co2_emitted_tonnes"]]                    # STEP 2: Define inputs and target
    target   = filtered["capture_efficiency_percent"]

    preprocessor = ColumnTransformer(        #Need one-hot encoding, so using preprocessor        # STEP 3: Preprocess categorical inputs (region, type → numbers)
        transformers=[
            ("types", OneHotEncoder(handle_unknown="ignore"), ["region", "storage_site_type"]),
            ("num", "passthrough", ["co2_emitted_tonnes"])
        ]
    )

    model = Pipeline(steps=[("Preprocessor", preprocessor),                          # STEP 4: Train Decision Tree model
    ("Regressor", DTR(random_state = 42, max_depth = 5))])

    model.fit(features, target)

    one_hot = model.named_steps["Preprocessor"].named_transformers_["types"]         # STEP 5: Extract feature importance
    one_hot_features = one_hot.get_feature_names_out(["region","storage_site_type"])
    all_features = list(one_hot_features) + ["co2_emitted_tonnes"]

    importances = model.named_steps["Regressor"].feature_importances_

    importance_df = pd.DataFrame({
    "Features": all_features,
    "Importances": importances
    }).sort_values(by="Importances", ascending=False)

    print(importance_df)

    return model, importance_df                                                     # STEP 6: Output = trained model + importance table
# -------------------------------------------------------------------------------------
        

#Run from cli______________________________
if __name__ == "__main__":
#section allows script to be run manually by user in the terminal:    
    parser = argparse.ArgumentParser(description="Get emission patterns per facility")
    parser.add_argument("csv_file", type=str, help="Path to the csv with emission data")
    parser.add_argument("--facility", type=str, help="Facility name", required=True)
    parser.add_argument("--plot", action="store_true", help="Plot L2 for analytics")
    parser.add_argument("--scatter", action="store_true", help="Get the scatter plot along with L2")
    args = parser.parse_args()
    data = pd.read_csv(args.csv_file) # Load the CSV file into a pandas DataFrame
    #CO2_emssion_pattern(data, args.facility, plot=args.plot, scatter=args.scatter)
    CO2_emission_pattern_DTR(data, args.facility, plot=args.plot, scatter=args.scatter) # Run one of the functions (basic CO2 pattern analysis)
    
    #_________________________________________________________
