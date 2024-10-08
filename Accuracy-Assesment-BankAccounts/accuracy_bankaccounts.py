import pandas as pd
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay, classification_report
import matplotlib.pyplot as plt
import numpy as np
import re

# Load the ground truth data
df_gt = pd.read_excel('ground_truth_bankaccounts.xlsx')

# Load the parsed data
df_parsed = pd.read_excel('parser_output_bankaccounts.xlsx')

# Ensure 'photo_id' and 'Account_Number' are of the same type in both DataFrames
df_gt['photo_id'] = df_gt['photo_id'].astype(str)
df_parsed['photo_id'] = df_parsed['photo_id'].astype(str)
df_gt['Account_Number'] = df_gt['Account_Number'].astype(str)
df_parsed['Account_Number'] = df_parsed['Account_Number'].astype(str)

#Data Preprocessing
def clean_text(text):
    """
    Clean and standardize text data.
    """
    if isinstance(text, str):
        text = text.strip().lower()
        text = re.sub(r'\s+', ' ', text)  # Replace multiple spaces with single space
        return text
    else:
        return ''

def clean_amount(amount):
    """
    Clean and standardize amount data.
    """
    if isinstance(amount, str):
        amount = amount.strip()
        amount = re.sub(r'[^\d\.\-]', '', amount)  # Remove all characters except digits, dot, and minus sign
        try:
            return float(amount)
        except ValueError:
            return np.nan
    elif isinstance(amount, (int, float)):
        return float(amount)
    else:
        return np.nan

# Apply cleaning functions to relevant columns in both DataFrames
text_fields = ['Bank_Name', 'Account_Type']
for field in text_fields:
    df_gt[field] = df_gt[field].apply(clean_text)
    df_parsed[field] = df_parsed[field].apply(clean_text)

# Clean 'Amount' field
df_gt['Amount'] = df_gt['Amount'].apply(clean_amount)
df_parsed['Amount'] = df_parsed['Amount'].apply(clean_amount)

# Fill missing values in 'Account_Type' with a placeholder
df_gt['Account_Type'].fillna('unknown', inplace=True)
df_parsed['Account_Type'].fillna('unknown', inplace=True)

# Merge the two dataframes on 'photo_id' and 'Account_Number'
df_merged = pd.merge(
    df_gt,
    df_parsed,
    on=['photo_id', 'Account_Number'],
    how='outer',
    suffixes=('_gt', '_parsed'),
    indicator=True
)


# For field-level accuracy, consider records present in both dataframes
df_both = df_merged[df_merged['_merge'] == 'both'].copy()

fields = ['Bank_Name', 'Account_Type', 'Amount']

field_accuracies = {}

for field in fields:
    if field != 'Amount':
        # Compare text fields
        df_both[field + '_match'] = df_both[field + '_gt'] == df_both[field + '_parsed']
    else:
        # Compare amounts with a tolerance
        df_both[field + '_match'] = np.isclose(
            df_both[field + '_gt'],
            df_both[field + '_parsed'],
            atol=0.01,  # Tolerance of 1 cent
            equal_nan=False
        )
    accuracy = df_both[field + '_match'].mean()
    field_accuracies[field] = accuracy

print("Field-level accuracies:")
for field, accuracy in field_accuracies.items():
    print(f"{field}: {accuracy * 100:.2f}%")

# Record-level accuracy: all fields match
df_both['all_fields_match'] = df_both[[field + '_match' for field in fields]].all(axis=1)
record_accuracy = df_both['all_fields_match'].mean()
print(f"\nRecord-level accuracy: {record_accuracy * 100:.2f}%")

# Compute True Positives (TP), False Positives (FP), and False Negatives (FN)
TP = len(df_both)
FP = len(df_merged[df_merged['_merge'] == 'right_only'])
FN = len(df_merged[df_merged['_merge'] == 'left_only'])

# Calculate Precision, Recall, and F1 Score
precision = TP / (TP + FP) if (TP + FP) > 0 else 0
recall = TP / (TP + FN) if (TP + FN) > 0 else 0
f1_score = (
    2 * (precision * recall) / (precision + recall)
    if (precision + recall) > 0
    else 0
)

print(f"\nPrecision: {precision * 100:.2f}%")
print(f"Recall: {recall * 100:.2f}%")
print(f"F1 Score: {f1_score * 100:.2f}%")

# Filter out records where Account_Type is missing
df_account_type = df_both.dropna(subset=['Account_Type_gt', 'Account_Type_parsed'])

y_true = df_account_type['Account_Type_gt']
y_pred = df_account_type['Account_Type_parsed']

# Define the labels (ensure all unique account types are included)
labels = sorted(df_account_type['Account_Type_gt'].unique().tolist())

# Check if labels list is not empty to avoid ValueError
if len(labels) > 0:
    # Generate confusion matrix
    cm = confusion_matrix(y_true, y_pred, labels=labels)

    # Create a figure with a larger size to accommodate labels
    fig, ax = plt.subplots(figsize=(10, 8))  # Adjust the figure size as needed

    # Create the ConfusionMatrixDisplay
    disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=labels)

    # Plot the confusion matrix on the specified axes
    disp.plot(cmap='Blues', ax=ax)

    # Rotate x-axis labels and adjust alignment
    plt.setp(ax.get_xticklabels(), rotation=45, ha='right', rotation_mode='anchor')

    # Rotate y-axis labels if needed
    plt.setp(ax.get_yticklabels(), rotation=0)

    # Set the title and layout
    plt.title('Confusion Matrix for Account_Type')
    plt.tight_layout()

    # Save the confusion matrix plot
    plt.savefig('confusion_matrix.png')

    # Show the plot
    plt.show()

    # Print classification report for Account_Type
    classification_rep = classification_report(y_true, y_pred, labels=labels, zero_division=0)
    print("\nClassification report for Account_Type:")
    print(classification_rep)

    # Save classification report to a text file
    with open('classification_report.txt', 'w', encoding="utf-8") as f:
        f.write("Classification report for Account_Type:\n")
        f.write(classification_rep)
    print("Classification report saved to 'classification_report.txt'.")
else:
    print("No labels found for Account_Type. Skipping confusion matrix and classification report.")

# Save record-level accuracy and overall metrics to a text file
with open('accuracy_metrics.txt', 'w') as f:
    f.write(f"Field-level accuracies:\n")
    for field, accuracy in field_accuracies.items():
        f.write(f"{field}: {accuracy * 100:.2f}%\n")
    f.write(f"\nRecord-level accuracy: {record_accuracy * 100:.2f}%\n")
    f.write(f"\nPrecision: {precision * 100:.2f}%\n")
    f.write(f"Recall: {recall * 100:.2f}%\n")
    f.write(f"F1 Score: {f1_score * 100:.2f}%\n")
print("Accuracy metrics saved to 'accuracy_metrics.txt'.")

