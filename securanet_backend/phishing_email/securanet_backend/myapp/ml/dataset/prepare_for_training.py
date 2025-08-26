import pandas as pd

# Load your merged file
df = pd.read_csv('headers.csv')  # Change to your actual merged file name

# 1. Remove duplicate headers (keep only unique)
df = df.drop_duplicates(subset='text')

# 2. Standardize labels
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

# 3. Balance the dataset (equal number of phishing and legit)
min_count = min(df['label'].value_counts().values)
df_balanced = pd.concat([
    df[df['label'] == 'phishing'].sample(min_count, random_state=42),
    df[df['label'] == 'legit'].sample(min_count, random_state=42)
])

# 4. Save the cleaned, balanced dataset
df_balanced[['text', 'label']].to_csv('clean_balanced_headers.csv', index=False)
print(f"Saved {len(df_balanced)} rows to clean_balanced_headers.csv")