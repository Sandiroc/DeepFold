from bs4 import BeautifulSoup as bs
import requests
import pandas as pd

def fetch_structures(url):

    try:
        response = requests.get(url)
        response.raise_for_status()
        bs_obj = bs(response.text, 'html.parser')


        pre_elements = bs_obj.find_all('pre')
        for pre in pre_elements:
            print(pre)
            # Look for span with potential dot-bracket content
            structure_element = pre.find('span', class_='notation-font')
            if structure_element:
                return structure_element.get_text(strip=True)
            
        
        print(structure_element)
        if structure_element:
            print(structure_element.text.strip())
            return structure_element.text.strip()
        else:
            print(f"No secondary structure found on page: {url}")
            return None
    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return None


if __name__ == "__main__":
    df = pd.read_csv('data/homo_sapiens_rrna_data.csv')
    df['Structure'] = df['URL'].apply(fetch_structures)
    df.to_csv("asdf")
    print(df.head())