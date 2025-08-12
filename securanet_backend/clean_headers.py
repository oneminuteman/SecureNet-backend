import pandas as pd

# Load your merged file
df = pd.read_csv('all_email_headers.csv')

# Remove duplicate headers (keep only unique)
df = df.drop_duplicates(subset='text')

# Standardize and filter labels
def map_label(label):
    label = str(label).lower()
    if label in ['spam', 'phishing', '1', 'malicious']:
        return 'phishing'
    elif label in ['ham', 'legit', '0', 'benign']:
        return 'legit'
    else:
        return None

df['label'] = df['label'].apply(map_label)
df = df[df['label'].isin(['phishing', 'legit'])]

# Save the cleaned dataset
df[['text', 'label']].to_csv('unique_labeled_headers.csv', index=False)
print(f"Saved {len(df)} unique, labeled headers to unique_labeled_headers.csv")