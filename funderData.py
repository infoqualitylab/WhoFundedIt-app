import requests
import datetime


def retrieve_funder_info(doi):
    url = f"https://api.crossref.org/works/{doi}"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        metadata = data.get("message", {})
        
        if "funder" in metadata:
            return metadata["funder"]
        else:
            return None
    
    return None


def retrieve_broader_data(funder_doi):
    url = f"https://data.crossref.org/fundingdata/funder/{funder_doi}"
    response = requests.get(url)
    
    funders = []

    while response.status_code == 200:
        data = response.json()
        funder = data.get("prefLabel", {}).get("Label", {}).get("literalForm", {}).get("content")
        funders.append(funder)
        broader_data = data.get("broader", {})
        if broader_data:
            url = broader_data["resource"]
            # print("Broader Funding Data:", url)
            response = requests.get(url)
        else:
            # print("No further broader data found.")
            break
        
    if funders:
        broader_data = " : ".join(funders[::-1])
        return broader_data
    else:
        return None


def process_multiple_dois(doi_file):
    start_time = datetime.datetime.now()
    total = 0
    fail = 0
    count = {}
    with open(doi_file, "r") as file:
        doi_list = file.read().splitlines()

    output = ""

    for doi in doi_list:
        funder_info = retrieve_funder_info(doi)

        output += f"Funder information for publication with DOI: {doi}\n"

        if funder_info:
            for funder in funder_info:
                funder_doi = funder.get("DOI")
                if funder_doi:
                    funder_name = retrieve_broader_data(funder_doi)
                else:
                    funder_name = funder.get("name")
                if funder_name in count:
                    count[funder_name] += 1
                else:
                    count[funder_name] = 1

                grant_ids = funder.get("award")
                output += f"Funder Name: {funder_name}\n"
                output += f"Grant IDs: {grant_ids}\n"
                output += "\n"

        else:
            output += f"No funder information found for publication with DOI: {doi}\n"
            fail += 1

        output += "---\n"
        total += 1
    end_time = datetime.datetime.now()
    total_time = (end_time - start_time).total_seconds()
    request_per_second = total/(end_time - start_time).total_seconds()
    success = ((total-fail)/total)*100

    output += f"Total execution time: {total_time}\n"
    output += f"Request per second: {request_per_second}\n"
    output += f"Success rate: {success:.2f}%\n"

    return output, count


# Example 
# doi_file_test = "dois.txt"
# # count_funder(doi_file_test)
# # #output_file = "funder_output.txt"
# # #process_dois(doi_file, output_file)
# x = process_dois_and_count(doi_file_test)
# print(x)
