import pandas as pd
import json

# load the JSON data
with open('data/human_rrna_unformatted.json', 'r') as file:
    data = json.load(file)

# flatten the results field
results_df = pd.json_normalize(data, 'results', ['job', 'rnacentral_version', 'download_date'], record_prefix='result_')

# Step 4: Save the DataFrame to a CSV file
results_df.to_csv('data/human_rrna.csv', index=False)
