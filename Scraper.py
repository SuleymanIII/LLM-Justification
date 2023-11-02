import requests
import json
import csv
from bs4 import BeautifulSoup
import time

query = "drug mechanism of action drug efficacy clinical trials evidence-based medicine"

api_key = "80a14182d2240f849caa221db246275dee08"

pubmed_api_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"

pubmed_fetch_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"

rate_limit = 0.111  # 1 / 9

rate_limit_counter = 0

csv_file = open("pubmed_data.csv", "w", newline="", encoding="utf-8")
csv_writer = csv.writer(csv_file)

csv_writer.writerow(["PubMed ID", "Title", "URL", "Abstract"])

# Step 1: Perform a PubMed search to get a list of article IDs
retmax = 10
page = 1

while True:
    params = {
        "db": "pubmed",
        "term": query,
        "retmax": retmax,
        "retstart": (page - 1) * retmax,
        "retmode": "json",
        "api_key": api_key,
    }

    response = requests.get(pubmed_api_url, params=params)

    if response.status_code == 200:
        data = json.loads(response.text)
        article_ids = data.get("esearchresult", {}).get("idlist", [])
        if not article_ids:
            break  # No more articles found, exit the loop

        # Step 2: Fetch article details for each article ID and write to CSV
        for pmid in article_ids:
            if rate_limit_counter >= 1:
                time.sleep(rate_limit)  #
                rate_limit_counter = 0

            params = {
                "db": "pubmed",
                "id": pmid,
                "rettype": "abstract",
                "retmode": "xml",
                "api_key": api_key,
            }

            response = requests.get(pubmed_fetch_url, params=params)

            if response.status_code == 200:
                soup = BeautifulSoup(response.text, "xml")

                article_title = soup.find("ArticleTitle")
                title = article_title.get_text() if article_title else "No Title Available"

                abstract_text = soup.find("AbstractText")
                abstract = abstract_text.get_text() if abstract_text else "No Abstract Available"

                url = f"https://pubmed.ncbi.nlm.nih.gov/{pmid}"
                csv_writer.writerow([pmid, title, url, abstract])
                rate_limit_counter += 1
            else:
                print(
                    "Error while fetching PubMed article details. Status code:", response.status_code)
        page += 1
    else:
        print("Error while searching PubMed. Status code:", response.status_code)
        break

csv_file.close()
