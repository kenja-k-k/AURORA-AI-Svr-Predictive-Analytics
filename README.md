# AURORA AI Service – CO₂ Predictive Analytics

This repository contains the **CO₂ Predictive Analytics AI Service**, part of the broader **AURORA Project**, focused on verifiable carbon monitoring and reporting using **AI**, **blockchain**, and **IoT** technologies.

The service demonstrates how simulated IoT data from Carbon Capture and Storage (CCS) facilities can be analyzed for **seasonal trends and predictive forecasts**, providing actionable insights and alerts to improve operational performance and sustainability outcomes.

---

## 1. High-Level Architecture

The AURORA system integrates **SingularityNET**, AI Services, blockchain-based verification, and IoT data streams into a cohesive decentralized platform. All three services are independent of each other and can therefore be used individually. However, they are hosted on the same server.

### System Overview
![Aurora component diagram](https://github.com/kenja-k-k/AURORA-AI-Svr-Predictive-Analytics/blob/main/Aurora%20component%20diagram.jpg)

### Key Components
- **SingularityNET Integration**
  - Users and admins access the **Marketplace** and **Publisher Portal** to test and deploy AI services.
  - The CO₂ Predictive Analytics service is published to the marketplace for discovery and consumption.
  - The main way to use the service is as a component to be integrated into an external/pre-existing system, by said system calling the service's exposed endpoint(s) through the daemon. Frontend display and further processing of this or other services' outputs are up to the aforementioned system. By making these kinds of integratable components (services) available, SingularityNET simplifies AI application development.

- **Virtual Machine / Backend**
  - Each AI service is intended to be run inside **isolated containers**:
    - **Service 1 (CO₂ Analytics)** – Operational performance and anomaly detection.
    - **Service 2 (CO₂ Predictive Analytics)** – Implemented in this repository.
    - **Service 3, etc.** – Other available services for additional analytics and ESG reporting.
  - Blockchain hashing (placeholder in Poc) ensures secure and tamper-proof records through creating cyptographic fingerprints.
  - IoT data streams (simulated in PoC) feed into the analytics service for processing.

- **Daemon**
  - This acts as your trusted **gateway** between SingularityNET and your chosen service.
  - You interact with the daemon using the standard SingularityNET tools (SDKs, CLI).
  - The daemon exposes the standard SingularityNET API endpoint. It takes care of **authentication** and payment **verification** automatically, so only valid, authorized requests reach the AI service.
  - It ensures requests are properly formatted and reliably delivered, while also handling responses back to your application.
  - This design means your application connects to our service in a secure, predictable, and marketplace-compliant way, without needing to worry about the internal details of our infrastructure.

- **Frontend (Optional)**
  - A dashboard visualizes seasonal performance metrics, predictive insights, and alerts.
  - Mostly for demo purposes, there is a dedicated simple frontend available, to visualize the services' generated outputs. It is connected to the service backend through the daemon in the same way as intended in the original way of use. Direct access to the frontend code deployment (on the VM) is neded for this setup.

- **Database Container**
  - Stores processed data and enables querying for historical and seasonal analysis.

---

## 2. Role of This Service

This repository specifically implements **Service 2 Backend (CO₂ Predictive Analytics)** highlighted in **Container 2** of the architecture.

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
| **`Aurora component diagram.jpg`**   | High-level component diagram of the ESG Reporting service.                                         | Documentation |
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
- **SingularityNET CLI** for publishing to the marketplace.  
- **Metamask Wallet (TestNet Account)** for blockchain testnet interactions.  

### Steps
1. **Clone the repository:**
   ```bash
   git clone https://github.com/kenja-k-k/AURORA-AI-Svr-Predictive-Analytics.git
   cd AURORA-AI-Svr-Predictive-Analytics
2. **Build and run the container:**
  The first one will build the three images specified in the docker-compose.yml file (the service, the ETCD store and the daemon).
The second one will start the containers based on the built images. There is no need to specify ports and names of containers, as everything is specified in the docker-compose.yml file.
   ```bash
   docker compose build
   docker compose up -d
3. **Access the service:**
    Backend API: http://localhost:7000
    Optional frontend dashboard: http://localhost:3000
4. **Publish to SingularityNet testnet (optional)**
      Configure daemon files in /backend/daemon/.
      Use the SingularityNET Publisher Portal

## 6. Deployment Instructions for True Integration

Our service is available on the **SingularityNET Marketplace**. You can integrate it into your application in just a few steps.
- You don’t interact with our infrastructure directly.
- You just use the SingularityNET CLI or SDK.
- The daemon + marketplace handle authentication, payments, and routing to our AI service.

### 1. Create a SingularityNET Account
1. Go to the [SingularityNET Marketplace] (https://beta.singularitynet.io/).  
2. Create an account.
3. Link your **Metamask (or compatible wallet)**
4. Fund your wallet with **AGIX tokens** (required for service usage).

### 2. Install the SingularityNET CLI or SDK
**Prerequisites**
- **Python 3.8+** for CLI and Python SDK  
- **Node.js (LTS)** if using the JavaScript SDK

**Steps**
1. Install the CLI with pip
   ```bash
   pip install snet-cli
3. (Optional) Install SDKs for integration (Python or JavaScript SDK)

### 3. Open a Payment Channel
**Prerequisites**
- SNET CLI installed and configured
- AGIX tokens available in your wallet

**Steps**
1. Deposit AGIX into your account
   ```bash
   snet account deposit 100
3. Open a payment channel for the service
   ```bash
   snet channel open <org_id> <service_id> 10 1

Where:
- `<org_id>` → the organization ID on the marketplace
- `<service_id>` → the identifier of our AI service
- `10` → amount of AGIX tokens allocated
- `1` → channel expiration in blocks

### 4. Call the Service
**Prerequisites**
- Open payment channel to our service
- Service method name (from marketplace metadata)

**Steps**
1. Call the service via CLI
   ```bash
   snet call <org_id> <service_id> <service_method> \
   -y '{"input": "Your request here"}'
2. Or call the service via Python SDK
   ```bash
   from snet import sdk
   snet_sdk = sdk.SnetSDK(config_path="~/.snet/config")
   client = snet_sdk.create_service_client(
       org_id="<org_id>",
       service_id="<service_id>",
       group_name="default_group"
   )
   response = client.call_rpc("service_method", {"input": "Your request here"})
   print(response)

### 5. Integrate Into Your Application
**Prerequisites**
- Working backend (Python, Node.js, or other supported runtime)
- Access to the SNET SDK or CLI

**Steps**
1. Wrap the SDK call into your backend service or workflow.
2. Pass inputs from your application into the request.
3. Handle the responses just like any other API result.
4. Rely on the daemon to ensure authentication, payments, and secure execution.

### 6. Monitor & Manage Usage
**Prerequisites**
- SNET CLI configured
- Active payment channels

**Steps**
1. Check channel balance
   ```bash
   snet channel balance
3. Extend or open new channels as needed
   ```bash
   net channel extend-add-for-service <org_id> <service_id> 10 10000
4. Monitor logs and metrics through your SingularityNET account dashboard.

