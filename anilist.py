# Make sure to install gql first
from gql import gql, Client
from gql.transport.aiohttp import AIOHTTPTransport
import json
import csv

def pullData(cli, season, seasonYear):
    MAX_ENTRIES = 100
    PAGE_SIZE = 25
    query = gql( """
    query getShows ($page: Int, $perPage: Int, $season: MediaSeason, $seasonYear: Int) {
    Page(page: $page, perPage: $perPage) {
        pageInfo {
        total
        currentPage
        lastPage
        hasNextPage
        }
        media(season: $season, seasonYear: $seasonYear, type: ANIME, format: TV) {
        id
        source
        description(asHtml: false)
        title {
            romaji
            english
            native
        }
        }
    }
    }
    """ )

    p = 1
    more_data = True
    d = []

    while(more_data):
        params = {"page": p, "perPage": PAGE_SIZE,"season":season, "seasonYear": seasonYear}
        # Execute the query on the transport
        result = cli.execute(query, variable_values=params)
        d.extend(result["Page"]["media"])
        if( len(d) > MAX_ENTRIES ):
            # Exceeded maximum number of results
            return False
        p += 1
        more_data = result["Page"]["pageInfo"]["hasNextPage"]
    return d

def exportToJson(d, file_path):
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(d, file, indent=4, ensure_ascii=False)

    print(f"Data has been written to {file_path}")

def exportToCSV(d, file_path):
    # Fieldnames for the CSV
    fieldnames = ['id', 'source', 'description', 'title_romaji', 'title_english', 'title_native']

    # Writing to CSV
    with open(file_path, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        
        for item in d:
            row = {
                'id': item['id'],
                'source': item['source'],
                'description': item['description'],
                'title_romaji': item['title']['romaji'],
                'title_english': item['title']['english'],
                'title_native': item['title']['native']
            }
            writer.writerow(row)

    print(f"CSV Data has been written to {file_path}")

# ==================== MAIN ====================

# Select your transport with a defined url endpoint
transport = AIOHTTPTransport(url="https://graphql.anilist.co")

# Create a GraphQL client using the defined transport
client = Client(transport=transport, fetch_schema_from_transport=True)

result = pullData(client,"SUMMER", 2024)

exportToCSV(result, "anilist.csv")