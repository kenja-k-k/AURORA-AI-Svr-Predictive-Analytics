# AURORA AI Service – CO₂ Predictive Analytics

This repository contains the **CO₂ Predictive Analytics AI Service**, part of the broader **AURORA Project**, focused on verifiable carbon monitoring and reporting using **AI**, **blockchain**, and **IoT** technologies.

The service demonstrates how simulated IoT data from Carbon Capture and Storage (CCS) facilities can be analyzed for **seasonal trends and predictive forecasts**, providing actionable insights and alerts to improve operational performance and sustainability outcomes.

---

## 1. High-Level Architecture

The AURORA system integrates **SingularityNET**, AI Services, blockchain-based verification, and IoT data streams into a cohesive decentralized platform.

### System Overview
![AURORA Architecture](Architecture.jpg)

### Key Components
- **SingularityNET Integration**
  - Users and admins access the **Marketplace** and **Publisher Portal** to test and deploy AI services.
  - The CO₂ Predictive Analytics service is published to the marketplace for discovery and consumption.

- **Virtual Machine / Backend**
  - Each AI service is intended to be run inside **isolated containers**:
    - **Service 1 (CO₂ Analytics)** – Operational performance and anomaly detection.
    - **Service 2 (CO₂ Predictive Analytics)** – Implemented in this repository.
    - **Service 3, etc.** – Future services for additional analytics and ESG reporting.
  - Blockchain hashing ensures secure and tamper-proof records.
  - IoT data streams (simulated in PoC) feed into the analytics service for processing.

- **Frontend (Optional)**
  - A dashboard visualizes seasonal performance metrics, predictive insights, and alerts.

- **Database Container**
  - Stores processed data and enables querying for historical and seasonal analysis.

---

## 2. Role of This Service

This repository specifically implements **Service 2 Backend (CO₂ Predictive Analytics)** highlighted in **Container 1** of the architecture.

- **Input:** Simulated IoT data streams mimicking CCS facility operations (CO₂ emissions, capture rates, storage conditions, etc.).  
- **Output:** Seasonal performance metrics, predictive insights based on historical trends, and proactive alerts for anomalies.  
- **Blockchain Integration:** Hashes analytics data to the **internal Blockchain Hashing Service** for verifiable storage (separate from SingularityNET’s Ethereum metering).  

This service extends the CO₂ analytics by focusing on **seasonal patterns and short-term forecasts**, helping operators anticipate performance shifts due to seasonal variations.

### Choice of Models (Decision Tree + Ridge Regression)
- **Decision Tree Regression** is used to check whether a given entry falls within the expected seasonal values. This model can flag anomalies when performance deviates from the seasonal norm.  
- **Ridge Regression (forecasting)** is applied across historical data to predict future emissions and capture performance, with results projected forward into the current year.  
- Together, these approaches balance **predictive power** with **interpretability**, allowing CCS operators to identify trends, set realistic expectations, and take corrective measures in advance.  

From a business perspective, this service answers:  
- *What performance should we expect in each season?*  
- *Are current values falling outside normal seasonal ranges?*  
- *What are the likely near-term forecasts for emissions and capture efficiency?*

---

## 3. PoC Features and Requirements

The **Proof of Concept (PoC)** demonstrates three primary features using simulated IoT data, as specified in the *CO₂ Predictive Analytics Specification*:

| Feature ID | Feature Name              | Description                                                                 |
|------------|---------------------------|-----------------------------------------------------------------------------|
| **2.1**    | Seasonal Trend Analysis   | Detects seasonal variations in emissions and capture efficiency.             |
| **2.2**    | Predictive Forecasting    | Uses regression models to forecast CO₂ emissions and efficiency for near-term dates. |
| **2.3** *(planned)*    | Proactive Seasonal Alerts | Flags anomalies when current performance falls outside expected seasonal ranges. |

**Summary of PoC Objectives:**
- Demonstrate seasonal CO₂ analytics using **simulated IoT data**.  
- Highlight **expected ranges per season** and deviations from the norm.  
- Showcase **short-term forecasts** of emissions and efficiency.  

---

## 4. Repository Structure

The repository is structured to reflect the modular design of the CO₂ Predictive Analytics service.  
Core components include the gRPC server, analytics module, sample datasets, and deployment files.

| Path / File            | Description                                                                                          | Related Features |
|-------------------------|------------------------------------------------------------------------------------------------------|------------------|
| **`/protos/`**          | gRPC protocol buffer definitions for service communication.                                          | All services |
| **`.gitignore`**        | Rules to exclude Python/IDE/cache files from git.                                                   | Housekeeping |
| **`Dockerfile`**        | Container build instructions for the service.                                                       | Deployment |
| **`README.md`**         | Project overview, installation, and usage instructions (this file).                                  | Documentation |
| **`docker-compose.yml`**| Orchestration for multi-container setup (service + gRPC server).                                     | Deployment |
| **`environment.yml`**   | Conda environment specification for reproducible setup.                                              | Deployment |
| **`grpc_server.py`**    | gRPC server implementation. Hosts the endpoints for data upload and seasonal stats queries.           | All services |
| **`insights.py`**       | Analytics logic: includes season classification (`seasonify`), median range calculations, and predictive regression models. | 2.1, 2.2, 2.3 |
| **`requirements.txt`**  | Python dependencies for the service (FastAPI, pandas, scikit-learn, etc.).                           | Deployment |
| **`service.py`**        | FastAPI entry point exposing endpoints: `UploadCSV` and `GetSeasonalStats`.                          | 2.1, 2.2, 2.3 |
| **`clean_data.csv`**    | Example dataset with seasonal tracking for testing the service.                                       | Demo |
| **`dataset_file.csv`**  | Sample dataset for regression and seasonal stats analysis.                                            | Demo |
| **`live.json`**         | Early JSON configuration for live testing (work in progress).                                        | Demo |

---

## 5. Deployment Instructions

### Prerequisites
- **Docker** for containerized deployment.  
- **Python 3.10+** for running locally.  
- **SingularityNET CLI** for publishing to the marketplace (optional).  
- **Metamask Wallet (TestNet Account)** for blockchain testnet interactions (optional).  

### Steps

1. **Clone the repository:**
   ```bash
   git clone https://github.com/kenja-k-k/AURORA-AI-Svr-Predictive-Analytics.git
   cd AURORA-AI-Svr-Predictive-Analytics

