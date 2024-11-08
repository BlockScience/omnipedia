import requests


def fetch_wikitext(url):
    # Extract the page title from the URL
    title = url.split("/wiki/")[-1]

    # Set up the API request to get the wikitext
    api_url = "https://en.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "prop": "revisions",
        "rvprop": "content",
        "rvslots": "main",
        "titles": title,
        "format": "json",
        "formatversion": "2",
    }

    # Send the request
    response = requests.get(api_url, params=params)
    data = response.json()

    # Extract the wikitext from the response
    try:
        wikitext = data["query"]["pages"][0]["revisions"][0]["slots"]["main"]["content"]
        return wikitext
    except KeyError:
        return "Wikitext not found. Check if the page exists."



url = "https://en.wikipedia.org/wiki/Wikipedia:WikiProject_Molecular_Biology/Style_guide_(gene_and_protein_articles)"
wikitext = fetch_wikitext(url)
print(wikitext)
