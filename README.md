## Identifying player similarities in Football

Value Proposition:
Football clubs and scouting agencies, such as Burnley FC, need ways to identify affordable and tactically appropriate player alternatives when replacing retired/sold players. Current methods rely heavily on manual filtering of stats and extensive video analysis through platforms such as WyScout, which is time-consuming and subject to human bias. Our tool offers a scalable, automated solution that surfaces similar players by analyzing both event metrics (e.g., goals, assists) and spatial behavior on the pitch. This gives clubs and analysts deeper tactical insights and dramatically cuts down scouting time. The aim is therefore to present this tool in collaboration with WyScout’s player scouting video-based platform by rapidly detailing alternative players to look into when player information is shared.


Status Quo & Business Metric:
Current Approach: People rely on scouting reports and video analyses that can be subjective and time consuming. 

Proposal Advantage: Our system provides a data-driven, spatial-centric tool, enabling users to make more strategic, long-term decisions about which players to scout further and eventually purchase.


Business Metrics for Success:
Precision/purity of Player Similarity: Proportion of top-N retrieved players who match in refined roles (from Transfermarkt-enhanced WyScout data).
Action Consistency Evaluation: Holdout test—split each player into two time-based subsets (Player A and Player B). Measure how often Player B is returned as the most similar to Player A.
Engagement Rate (for Wyscout scenario): Number of users who interact with the “similar player” recommendations.
By focusing on the spatial behaviour of players, this system transfers video analysis-dependent information into a dashboard that is numerically and heatmap-based.

### Contributors

| Name                            | Responsible for | Link to their commits in this repo |
|---------------------------------|-----------------|------------------------------------|
| All team members                | Unit 3, value proposition, business metrics,         |
| Haris Naveed                    | Units 4 & 5     |                                    |
| Ariel Haberman                  | Units 6 & 7     |                                    |
| Musonda Sinkala                 | Unit 8          |                                    |

### System diagram

![System Diagram](https://github.com/HarisNaveed17/mlops_project/blob/main/new_diagram.jpeg?raw=true)


### Summary of outside materials

| Dataset           | How it was created | Conditions of use | Link              |
|-------------------|--------------------|-------------------|-------------------|
| WyScout Data      |                    | n/a               | *1 below          |
| Statsbomb Data    |                    | n/a               | *2 below          |
| Transfermarkt Data|                    | n/a               | *3 below          |
| Model 1: K-means <br> Clustering | n/a                | n/a               | n/a               |
| Model 2: Random Forest Classifier | n/a                | n/a               | n/a               |


*1 = https://figshare.com/collections/_/4415000

*2 = https://github.com/statsbomb/open-data

*3 = https://data.world/dcereijo/player-scores

### Infrastructure Used


| Requirement     | How many/when                 | Justification                           |
|-----------------|-------------------------------|-----------------------------------------|
| `m1.medium` VMs | 1 for entire project duration | Used for Model Training and Experiment Tracking                    
| Floating IPs    | 1 for entire project duration|  Since we used only one server and used a docker volume as persistent storage  |          
|Persistent <br> Storage | 3 Volumes  | For data and artifact storage for <br>  the project duration |


### Detailed design plan

Our project follows a cloud-native (Unit 3) approach using Git to automate provisioning and deployment. Microservices are containerized in Docker and served through Kubernetes for scalability and fault tolerance. The CI/CD pipeline automates model retraining and logs results with MLflow (Unit 5). An ETL pipeline ingests data from the US grid data (and can work on other sources) , processes it through data cleaning and transformation steps, and loads it into the data repository for training and inference. Offline data (Unit 8) is stored persistently using Chameleon resources, streaming pipelines (Unit 8) handle real-time updates. Persistent storage (Unit 8) will be used to ensure that trained models, logs, and artifacts persist beyond individual runs. Distributed training is accelerated using Ray Train (Unit 5), with hyperparameter tuning handled by Ray Tune for optimal performance (Unit 5). The infrastructure will ensure fast retraining, scalable deployment, and continuous optimization.
 

#### Model training and training platforms

Unit 4:
|Req             | How we will satisfy it                                                   |
|----------------|--------------------------------------------------------------------------|
|Train & retrain | Train the model on the processed data and predict the cluster to which an incoming player belongs. |
|Modelling       | NA     |


Unit 5:

|Req        | How we will satisfy it                                                         |
|-----------|--------------------------------------------------------------------------------|
|Experiment <br> tracking | Host MLflow on Chameleon to log all training runs, hyperparameters, and metrics|



#### Model serving and monitoring platforms

This project will be focusing on training on large time model. The projections output by this system will then be served to the user at a single API endpoint. We plan on exploring several model optimization techniques like graph optimizations and reduced precision but avoiding ones that require specific hardware backends. For system level required concurrency we plan on trying FastAPI and/or using dynamic batching for regulation. We plan on evaluating our models. While we will perform sanity checks on the forecasts there is no ground truth so most evaluation will be done on the time series models. We will use canary testing to first check if the system is ready to go live and later allow user feedback. 

#### Data pipeline


|Req       | How we will satisfy it                                                         |
|----------|--------------------------------------------------------------------------------|
|Persistent <br> Storage| Chameleon persistent storage for models and artefacts, container images, data  |
|Offline <br> data| Structured storage of the data described in csv files object store.            |
|Data <br> Pipeline| Automated data pipeline Airflow for ingestion, transformation, and storage.    |
|Online <br> data  | Real time ingestion of grid data  |

We will be attempting the difficulty question for unit 8, i.e., implement an interactive and comprehensive data dashboard, that members of the team can use to get high-level insight into the data and data quality.

#### Continuous X


|Requirement    | How we will satisfy it                                                    |
|---------------|---------------------------------------------------------------------------|
|Infrastructure <br> as code | Define infrastructure requirements in yml files stored on Git instead of <br>  relying on ClickOps |
|Cloud-native   | Use immutable infrastructure, microservices, and containerized workloads  |
|CI/CD          | Automated pipeline for retraining, testing, optimization, and deployment  |
|Deployment     | Deploy to production with monitoring and auto-rollback mechanisms         |
