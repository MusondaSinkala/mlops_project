
## Identifying neighborhood trends using NYC OpenData

Value Proposition:
When people move to New York, they often struggle to determine which neighborhood best suits their needs. They typically rely on forums like Reddit or word-of-mouth, which can be subjective, inconsistent, and time-consuming. Our project proposes a machine learning system that provides insights into the long-term appeal of different neighborhoods for people that are navigating the apartment hunt process.
We will leverage time series models to project neighborhood-relevant trends, helping users make informed decisions about where to live based on future conditions rather than just the present snapshot.

To improve decision-making, our system will include:
Time Series Forecasting for Key Neighborhood Metrics:
Rent Trends: Predicting future rental prices to help users gauge affordability over time.
Demographic Shifts: Forecasting changes in demographic distributions to provide insights into neighborhood evolution.
Safety Trends: Predicting trends in vehicle collisions and shootings to assess the potential long-term safety of an area.


CitiBike Accessibility Clustering:
Using a clustering model to identify neighborhoods with high CitiBike accessibility, using the number of CitiBike stations as a proxy for CitiBike infrastructure.


Status Quo & Business Metric:
Current Approach: People rely on Reddit, personal recommendations, or scattered online sources. These methods are subjective, inconsistent, and do not account for future trends.


ML Advantage: Our system provides a data-driven, forward-looking alternative, enabling users to make more strategic, long-term decisions about where to live.


Business Metrics for Success:
User satisfaction: Measured by follow-up surveys asking users if they found the system useful.
User Retention: How often people return to the tool for future searches.
Model Performance: Forecasting accuracy of rent, safety, and demographic trends.


By focusing on future projections, this system enhances decision-making for new residents while improving efficiency compared to the status quo.

### Contributors

|----------------------------------------------------------------------------------------|
| Name                            | Responsible for | Link to their commits in this repo |
|---------------------------------|-----------------|------------------------------------|
| All team members                | Unit 3, value proposition, business metrics,         |
| Haris Naveed                    | Units 4 & 5     |                                    |
| Ariel Haberman                  | Units 6 & 7     |                                    |
| Musonda Sinkala                 | Unit 8          |                                    |
|----------------------------------------------------------------------------------------|

### System diagram



### Summary of outside materials

|--------------------------------------------------------------------------------|
| Dataset           | How it was created | Conditions of use | Link              |
|-------------------|--------------------|-------------------|-------------------|
| Average Rent      | StreetEasy Data    | n/a               | *1 below          |
| Demographics      | NYC Open Data      | n/a               | *2 below          |
| Collisions Data   | NYC Open Data      | n/a               | *3 below          |
| Shootings Data    | NYC Open Data      | n/a               | *4 below          |
| Parks Data        | NYC Open Data      | n/a               | *5 below          |
| Restaurant Data   | Public Github      | n/a               | *6 below          |
| CitiBike Data     | Citibike Website   | n/a               | *7 below          |
| Model 1: Arima    | n/a                | n/a               | n/a               |
| Model 2: K Means  | n/a                | n/a               | n/a               |
| Model 3: RNN      | n/a                | n/a               | n/a               |


*1 = https://streeteasy.com/blog/data-dashboard/

*2 = https://data.cityofnewyork.us/Education/2017-18-2021-22-Demographic-Snapshot/c7ru-d68s/about_data 

*3 = https://data.cityofnewyork.us/Public-Safety/Motor-Vehicle-Collisions-Crashes/h9gi-nx95/about_data

*4 = https://data.cityofnewyork.us/Public-Safety/NYPD-Shooting-Incident-Data-Year-To-Date-/5ucz-vwe8/data_preview

*5 = https://data.cityofnewyork.us/Recreation/Parks-Properties/enfh-gkve/about_data

*6 = https://github.com/alysedelaney/how-nyc-eats/tree/main/data/yelp

*7 = https://s3.amazonaws.com/tripdata/index.html

### Summary of infrastructure requirements

|-------------------------------------------------------------------------------------------|
| Requirement     | How many/when                 | Justification                           |
|-----------------|-------------------------------|-----------------------------------------|
| `m1.medium` VMs | 3 for entire project duration | One for model training, one for model   |
|                                                  serving and the last for the dashboard   |
|-----------------|-------------------------------|-----------------------------------------|
|                 |                               | We might use an RNN for the time series |
| 2 A100 GPUs       3 hour block twice a week       data and would need to GPU to speed up  |
|                                                   training                                |
|-----------------|-------------------------------|-----------------------------------------|
|                 | 1 for entire project duration,| We need a floating IP so the VM can     |
| Floating IPs      1 for sporadic use              communicate with our persistent storage |
|                                                   as well as for training and serving     |
|-----------------|-------------------------------|-----------------------------------------|                 
|Persistent       | Unclear as of now             | For model, data and artifact storage for|
|Storage                                            the project duration                    |
|-------------------------------------------------------------------------------------------|

### Detailed design plan

Our project follows a cloud-native (Unit 3) approach using Git to automate provisioning and deployment. Microservices are containerized in Docker and served through Kubernetes for scalability and fault tolerance. The CI/CD pipeline automates model retraining and logs results with MLflow (Unit 5). An ETL pipeline ingests data from NYC Open Data, processes it through data cleaning and transformation steps, and loads it into the data repository for training and inference. Offline data (Unit 8) is stored persistently using Chameleon resources, streaming pipelines (Unit 8) handle real-time updates. Persistent storage (Unit 8) will be used to ensure that trained models, logs, and artifacts persist beyond individual runs. Distributed training is accelerated using Ray Train (Unit 5), with hyperparameter tuning handled by Ray Tune for optimal performance (Unit 5). The infrastructure will ensure fast retraining, scalable deployment, and continuous optimization.
 

#### Model training and training platforms

Unit 4:
|-------------------------------------------------------------------------------------------|
|Req             | How we will satisfy it                                                   |
|----------------|--------------------------------------------------------------------------|
|Train & retrain | Train time-series models on NYC data; re-train safety models once a week |
|----------------|--------------------------------------------------------------------------|
|Modelling       | Choose models based on interpretability, and forecasting accuracy.       |
|-------------------------------------------------------------------------------------------|

Unit 5:
|-------------------------------------------------------------------------------------------|
|Req        | How we will satisfy it                                                        |
|-----------|-------------------------------------------------------------------------------|
|Experiment | Host MLflow on Chameleon to log all training runs, hyperparameters, andmetrics|
|tracking                                                                                   |
|-----------|-------------------------------------------------------------------------------|
|Scheduling | Deploy Ray cluster on Chameleon; submit training jobs via Ray                 |
|training                                                                                   |
|-----------|-------------------------------------------------------------------------------|
|Ray train  | Will use Ray Train’s TorchTrainer for fault tolerance                         |
|-------------------------------------------------------------------------------------------|

#### Model serving and monitoring platforms

We will be integrating our smaller models into one forcast. The projections outputted by this system will then be served to the user at a single API endpoint. We plan on exploring several model optimization techniques like graph optimizations and reduced precision but avoiding ones that require specific hardware backends. For system level required concurrency we plan on trying FastAPI and/or using dynamic batching for regulation. We plan on evaluating our models before joining them together to form the main forecasting system. While we will perform sanity checks on the forecasts is no ground truth so most evaluation will be done on the time series models. We will use canary testing to first open our service just to students moving to NYC before the service is open to the general public. Users will be able to leave feedback about if they thought the projections make sense and align with what they think of neighborhoods.  

#### Data pipeline

|-------------------------------------------------------------------------------------------|
|Req       | How we will satisfy it                                                         |
|----------|--------------------------------------------------------------------------------|
|Persistent| Chameleon persistent storage for models and artefacts, container images, data  |
|Storage                                                                                    |
|----------|--------------------------------------------------------------------------------|
|Offline   | Structured storage of the data described in csv files object store.            |
|data                                                                                       |
|----------|--------------------------------------------------------------------------------|
|Data      | Automated data pipeline Airflow for ingestion, transformation, and storage.    |
|Pipeline                                                                                   |
|----------|--------------------------------------------------------------------------------|
|Online    | Real time ingestion of shooting and collision data as these are updated daily  |
|data                                                                                       |
|-------------------------------------------------------------------------------------------|

We will be attempting the difficulty question for unit 8, i.e., implement an interactive and comprehensive data dashboard, that members of the team can use to get high-level insight into the data and data quality.

#### Continuous X

|-------------------------------------------------------------------------------------------|
|Requirement    | How we will satisfy it                                                    |
|---------------|---------------------------------------------------------------------------|
|Infrastructure | Define infrastructure requirements in yml files stored on Git instead of  |
|   as code       relying on ClickOps                                                       |
|---------------|---------------------------------------------------------------------------|
|Cloud-native   | Use immutable infrastructure, microservices, and containerized workloads  |
|---------------|---------------------------------------------------------------------------|
|CI/CD          | Automated pipeline for retraining, testing, optimization, and deployment  |
|---------------|---------------------------------------------------------------------------|
|Deployment     | Deploy to production with monitoring and auto-rollback mechanisms         |
|-------------------------------------------------------------------------------------------|



