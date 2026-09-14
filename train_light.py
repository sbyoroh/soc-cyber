import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import xgboost as xgb
import pickle

print("Loading dataset...")
df = pd.read_csv('UNSW_NB15_training-set.csv')

# Select only 3 features that the sensor can read live from the network
features_to_use = ['spkts', 'sbytes', 'rate']
X = df[features_to_use]
y = df['label']

print("Splitting data into training and testing sets...")
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

print("Training the lightweight XGBoost model...")
model = xgb.XGBClassifier(eval_metric='logloss')
model.fit(X_train, y_train)

print("Calculating model accuracy...")
accuracy = accuracy_score(y_test, model.predict(X_test))
print(f"Model Accuracy: {accuracy * 100:.2f}%")

# Save the new model
with open('xgb_model_light.pkl', 'wb') as f:
    pickle.dump(model, f)

print("Model successfully saved as 'xgb_model_light.pkl'!")