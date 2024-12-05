import requests
import pandas as pd
import time

def fetch_all_entries():
    """
    Fetch data from RNACentral API. \n

    Storing ribosomal RNA sequences from Homo Sapiens that have a secondary structure recorded on RNACentral. 
    """
    # fields to fetch from rnacentral api
    fields = [
        'description',
        'rna_type',
        'has_secondary_structure',
        'species',
    ]

    # store secondary structure availability just in case
    query = {
        'query': 'species:"Homo sapiens" AND rna_type:"rRNA" AND has_secondary_structure:"True"',
        'fields': ','.join(fields),
        'format': 'json',
        'size': 100,
    }

    # RNAcentral api url
    url = 'https://www.ebi.ac.uk/ebisearch/ws/rest/rnacentral'

    all_entries = []  # List to store all fetched entries
    start = 0         # Start index for the first page
    total_results = None  # Total number of results, to be fetched from the first API call

    while True:
        # Update the start parameter for pagination
        query['start'] = start
        response = requests.get(url, params=query)
        # print(response.url)
        response.raise_for_status()  # Raise an error if the request fails
        data = response.json()

        # get number of results
        if total_results is None:
            total_results = data.get('hitCount', 0)
            print(f"Total results found: {total_results}")
        
        # get current page
        entries = data.get('entries', [])
        all_entries.extend(entries)

        # udpate start index for pagination
        start += len(entries)

        # if we got all entries
        if start >= total_results:
            break

        
        print("Fetched first " + str(start) + " entries")
        # delay requests to acommodate 50 req/min limit
        time.sleep(1.2)


    return all_entries

def process_entries_to_dataframe(entries):
    # Prepare a list to store processed data
    rna_data = []

    total_entries = len(entries)  # Get the total number of entries for progress tracking

    for index, entry in enumerate(entries, start=1):
        # get fields that we want
        entry_id = entry.get('id', None)  # Get the ID
        description = entry.get('fields', {}).get('description', [None])[0]  # Get the description
        rna_type = entry.get('fields', {}).get('rna_type', [None])[0]  # Get the RNA type
        sec_struct = entry.get('fields', {}).get('has_secondary_structure', [None])[0]  # Mock sequence data

        # get the sequence using the ID (URS part of the ID)
        urs = entry_id.split('_')[0]  # Extract the ID without species part
        seq_response = requests.get(f'https://rnacentral.org/api/v1/rna/{urs}.fasta')
        sequence = seq_response.text if seq_response.status_code == 200 else None

        # append as dict
        rna_data.append({
            'ID': entry_id,
            'Description': description,
            'RNA_Type': rna_type,
            'Has_Secondary_Structure': sec_struct,
            'Sequence': sequence
        })

        # Print progress of fetching sequences
        print(f"Fetching sequence {index}/{total_entries} (ID: {entry_id})")

        # Delay requests to avoid timeout based on 50 req/min limit
        time.sleep(1.2)

    # convert to df
    df = pd.DataFrame(rna_data)

    # add url for secondary structure scraping (optional)
    rcentral_url = 'https://rnacentral.org/rna/'
    df['URL'] = df['ID'].apply(lambda x: rcentral_url + x)

    return df


# Main script
def main():
    print("Fetching RNA data from RNAcentral...")
    entries = fetch_all_entries()
    print("Processing entries into a DataFrame...")
    df = process_entries_to_dataframe(entries)
    output_file = 'data/homo_sapiens_rrna_data.csv'
    df.to_csv(output_file, index=False)
    print(f"Data saved to {output_file}")
    print(df.head())

# Run the script
if __name__ == '__main__':
    main()