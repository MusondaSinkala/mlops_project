import pandas as pd
import re
import mlflow.sklearn
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix
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
final_data = data.drop(columns=data.loc[:, 'id':'image_url'])
final_data = final_data.drop(['clearances', 'top_knn_ids'], axis=1)

for col in final_data.columns:
    if is_percentage_string(final_data[col].iloc[0]):
        final_data[col] = final_data[col].apply(convert_to_float)

X = final_data.iloc[:, :-1]
y = final_data.iloc[:, -1]

# Use only the test split (same random split method as in train.py)
from sklearn.model_selection import train_test_split
_, X_val, _, y_val = train_test_split(X, y, test_size=0.2, random_state=42)
X_val, X_test, y_val, y_test = train_test_split(X_val, y_val, test_size=0.5, random_state=42)

# Load the model
model_uri = "runs:/e423875c582a4ef996eb58b8f47071e6/football_model"
model = mlflow.sklearn.load_model(model_uri)

# Predict and evaluate
y_pred = model.predict(X_test)

print("Evaluation Metrics:")
print(f"Accuracy: {accuracy_score(y_test, y_pred):.4f}")
print("\nClassification Report:")
print(classification_report(y_test, y_pred))
print("Confusion Matrix:")
print(confusion_matrix(y_test, y_pred))
