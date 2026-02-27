import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score
import joblib
import time

start_time = time.time()

# Old Colab paths
features_csv_path = '/content/drive/MyDrive/Phishing_Data/extracted_features.csv'
model_save_path = '/content/drive/MyDrive/Phishing_Data/phishing_sentinel_model.pkl'

# New local paths
features_csv_path = './datasets/extracted_features.csv'
model_save_path = './models/phishing_sentinel_model.pkl'

print("Loading extracted features from Google Drive...")
# Read the CSV we generated in the last step
df = pd.read_csv(features_csv_path)

# Separate features (X) and labels (y)
X = df.drop('label', axis=1)
y = df['label']

print("Splitting dataset into training and testing sets...")
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

print("Training the Random Forest Classifier...")
print("Executing... you can safely step away while this runs.")

# n_jobs=-1 uses all available processor cores in Colab to speed up training
clf = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
clf.fit(X_train, y_train)

print("\n--- Training Complete! ---")
print("Evaluating model...")
y_pred = clf.predict(X_test)
accuracy = accuracy_score(y_test, y_pred) * 100
print(f"Accuracy: {accuracy:.2f}%\n")
print(classification_report(y_test, y_pred))

print(f"Saving the final model directly to Drive...")
joblib.dump(clf, model_save_path)

elapsed_time = (time.time() - start_time) / 60
print(f"All done! Total execution time: {elapsed_time:.2f} minutes.")
print("Model safely saved to your local models folder.")

"""Loading extracted features from Google Drive...
Splitting dataset into training and testing sets...
Training the Random Forest Classifier...
Executing... you can safely step away while this runs.

--- Training Complete! ---
Evaluating model...
Accuracy: 86.78%

              precision    recall  f1-score   support

           0       0.89      0.90      0.89      9910
           1       0.83      0.81      0.82      6042

    accuracy                           0.87     15952
   macro avg       0.86      0.86      0.86     15952
weighted avg       0.87      0.87      0.87     15952

Saving the final model directly to Drive...
All done! Total execution time: 0.19 minutes.
Model safely saved to your Google Drive. Have a good night!"""