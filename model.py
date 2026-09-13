import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, classification_report
import xgboost as xgb
import pickle

print('???? ????? ????????...')
df = pd.read_csv('UNSW_NB15_training-set.csv')

if 'id' in df.columns:
    df = df.drop(columns=['id'])
if 'attack_cat' in df.columns:
    df = df.drop(columns=['attack_cat'])

print('???? ?????? ???????? ??????...')
categorical_cols = df.select_dtypes(include=['object', 'string']).columns
encoder = LabelEncoder()
for col in categorical_cols:
    df[col] = encoder.fit_transform(df[col].astype(str))

X = df.drop(columns=['label'])
y = df['label']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

print('???? ????? ??????? ????? (XGBoost)...')
model = xgb.XGBClassifier(eval_metric='logloss')
model.fit(X_train, y_train)

print('???? ???? ??? ??????...')
predictions = model.predict(X_test)
accuracy = accuracy_score(y_test, predictions)
print(f'\n??? ???????: {accuracy * 100:.2f}%')
print('\n????? ??????:')
print(classification_report(y_test, predictions))

with open('xgb_model.pkl', 'wb') as f:
    pickle.dump(model, f)
print('\n?? ??? ??????? ????? ???? xgb_model.pkl!')
