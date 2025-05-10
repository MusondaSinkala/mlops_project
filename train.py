import pandas as pd
import re
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix
import matplotlib.pyplot as plt
import mlflow
from mlflow.models import infer_signature

mlflow.set_tracking_uri(uri="http://127.0.0.1:8080")


def is_percentage_string(val):
        if not isinstance(val, str):
            return False
        # Matches strings like "10%", "10.5%", etc.
        return bool(re.match(r'^\s*-?\d+\.?\d*\s*%\s*$', val))
    
    # Function to convert percentage string to float
def convert_to_float(val):
    if isinstance(val, str):
        # Remove % sign and whitespace, then divide by 100
        try:
            return round(float(val.strip().rstrip('%').strip()) / 100, 2)
        except ValueError:
            return val
    return val



data = pd.read_parquet('final_player_df.parquet')
final_data = data.drop(columns=data.loc[:, 'id':'image_url'])
final_data = final_data.drop(['clearances', 'top_knn_ids'], axis=1)

for col in final_data.columns:
    if is_percentage_string(final_data[col].iloc[0]):
        final_data[col] = final_data[col].apply(convert_to_float)

X = final_data.iloc[:, :-1]  
y = final_data.iloc[:, -1]   

# If your target column has a specific name, use this instead:
# X = data.drop('target_column_name', axis=1)
# y = data['target_column_name']

# Split data into training and testing sets
X_train, X_val, y_train, y_val = train_test_split(
    X, y, test_size=0.2, random_state=42
)
# Split the validation set into validation and test sets
X_val, X_test, y_val, y_test = train_test_split(
    X_val, y_val, test_size=0.5, random_state=42
)
# Print the sizes of the datasets
print("Dataset sizes:")
print(f"Total dataset size: {X.shape[0]} samples") 
print(f"Training set size: {X_train.shape[0]} samples")
print(f"Validation set size: {X_val.shape[0]} samples")
print(f"Test set size: {X_test.shape[0]} samples")

# Initialize and train the Random Forest Classifier
# You can adjust these hyperparameters based on your needs

rf_params = {
    'n_estimators': 100,  # Number of trees
    'max_depth': None,    # Maximum depth of trees (None means unlimited)
    'min_samples_split': 2,
    'min_samples_leaf': 1,
    'random_state': 42,
    'n_jobs': -1  # Use all available cores
}

rf_classifier = RandomForestClassifier(**rf_params)

# Train the model
print("\nTraining Random Forest Classifier...")
rf_classifier.fit(X_train, y_train)

# Make predictions on the test set
y_pred = rf_classifier.predict(X_test)

# Evaluate the model
acc = accuracy_score(y_test, y_pred)
print("\nModel Evaluation:")
print(f"Accuracy: {acc:.4f}")
print("\nClassification Report:")
print(classification_report(y_test, y_pred))


# Feature importance
feature_importance = pd.DataFrame({
    'Feature': X.columns,
    'Importance': rf_classifier.feature_importances_
}).sort_values('Importance', ascending=False)

print("\nFeature Importance:")
print(feature_importance)

print(-1)


# Create a new MLflow Experiment
mlflow.set_experiment("MLflow Quickstart")

# Start an MLflow run
with mlflow.start_run(log_system_metrics=True):
    # Log the hyperparameters
    mlflow.log_params(rf_params)

    # Log the loss metric
    mlflow.log_metric("accuracy", acc)

    # Set a tag that we can use to remind ourselves what this run was for
    mlflow.set_tag("Training Info", "Basic RF Classifier model for football data")

    # Infer the model signature
    signature = infer_signature(X_train, rf_classifier.predict(X_train))

    # Log the model
    model_info = mlflow.sklearn.log_model(
        sk_model=rf_classifier,
        artifact_path="football_model",
        signature=signature,
        input_example=X_train,
        registered_model_name="tracking-quickstart",
    )