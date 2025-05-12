import pandas as pd
import re
import mlflow
from mlflow.tracking import MlflowClient
import mlflow.sklearn
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix
from sklearn.model_selection import train_test_split
import ast
#with help from chatgpt 
mlflow.set_tracking_uri(uri="http://129.114.26.77:8000")


def is_percentage_string(val):
    if not isinstance(val, str):
        return False
    return bool(re.match(r'^\s*-?\d+\.?\d*\s*%\s*$', val))

def convert_to_float(val):
    if isinstance(val, str):
        try:
            return round(float(val.strip().rstrip('%').strip()) / 100, 2)
        except ValueError:
            return val
    return val

# Load and preprocess test data
data = pd.read_parquet('final_player_df.parquet')

# Save full copy for cluster/knn role analysis later
raw_data = data.copy()

# Feature preprocessing for model input
final_data = data.drop(columns=data.loc[:, 'id':'image_url'])
final_data = final_data.drop(['clearances', 'top_knn_ids'], axis=1)

for col in final_data.columns:
    if is_percentage_string(final_data[col].iloc[0]):
        final_data[col] = final_data[col].apply(convert_to_float)

X = final_data.iloc[:, :-1]
y = final_data.iloc[:, -1]

# Use only the test split (same random split method as in train.py)
_, X_val, _, y_val = train_test_split(X, y, test_size=0.2, random_state=42)
X_val, X_test, y_val, y_test = train_test_split(X_val, y_val, test_size=0.5, random_state=42)

# Dynamically get the latest model run containing "football_model"
client = MlflowClient()
experiment = client.get_experiment_by_name("MLflow Quickstart")
runs = client.search_runs(experiment.experiment_id, "attributes.status = 'FINISHED'", order_by=["start_time DESC"])

model_uri = None
for run in runs:
    if "football_model" in run.info.artifact_uri:
        model_uri = f"runs:/{run.info.run_id}/football_model"
        break

if model_uri is None:
    raise RuntimeError("No run found with 'football_model' artifact")

# Helper to safely parse KNN ID strings
def parse_knn(knn_str):
    try:
        return ast.literal_eval(knn_str)
    except:
        return []

# Start new MLflow run
with mlflow.start_run(run_name="offline_eval") as run:
    # Predict and evaluate
    y_pred = model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    report = classification_report(y_test, y_pred, output_dict=True)
    conf_matrix = confusion_matrix(y_test, y_pred)

    # Log basic metrics
    mlflow.log_metric("accuracy", acc)
    mlflow.log_metric("precision_avg", report["weighted avg"]["precision"])
    mlflow.log_metric("recall_avg", report["weighted avg"]["recall"])
    mlflow.log_metric("f1_avg", report["weighted avg"]["f1-score"])

    print("Evaluation Metrics:")
    print(f"Accuracy: {acc:.4f}")
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred))
    print("Confusion Matrix:")
    print(conf_matrix)

    # Find misclassified players
    misclassified_indices = y_test.index[y_test != y_pred]
    misclassified_df = raw_data.loc[misclassified_indices]

    print("\nMisclassified Player Analysis:")
    cluster_agreement = []
    knn_agreement = []

    for _, row in misclassified_df.iterrows():
        player_role = row['role']
        cluster = row['cluster']
        knn_ids = parse_knn(row['top_knn_ids'])

        # Cluster role agreement
        cluster_members = raw_data[raw_data['cluster'] == cluster]
        if len(cluster_members) > 0:
            cluster_same_role = (cluster_members['role'] == player_role).sum()
            cluster_agreement.append(cluster_same_role / len(cluster_members))

        # KNN role agreement
        if knn_ids:
            knn_roles = raw_data[raw_data['id'].isin(knn_ids)]['role']
            knn_same_role = (knn_roles == player_role).sum()
            knn_agreement.append(knn_same_role / len(knn_roles))

    if cluster_agreement:
        cluster_score = sum(cluster_agreement)/len(cluster_agreement)
        mlflow.log_metric("avg_cluster_role_agreement", cluster_score)
        print(f"Average cluster role agreement: {cluster_score:.2f}")
    else:
        print("No cluster agreement data available.")

    if knn_agreement:
        knn_score = sum(knn_agreement)/len(knn_agreement)
        mlflow.log_metric("avg_knn_role_agreement", knn_score)
        print(f"Average KNN role agreement: {knn_score:.2f}")
    else:
        print("No KNN agreement data available.")

    print(f"\nResults logged to MLflow run: {run.info.run_id}")
