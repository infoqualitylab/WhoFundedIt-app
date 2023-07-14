import requests
import datetime

def retrieve_funder_info(doi):
    url = f"https://api.crossref.org/works/{doi}"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        metadata = data.get("message", {})
        
        if "funder" in metadata:
            #retrieve_broader_data(doi)
            return metadata["funder"]
        else:
            return None
    
    return None

def retrieve_broader_data(funderDoi):
    url=f"http://data.crossref.org/fundingdata/funder/{funderDoi}"
    response = requests.get(url)
    
    funders = []

    while response.status_code == 200:
        data = response.json()
        funder=data.get("prefLabel",{}).get("Label",{}).get("literalForm",{}).get("content")
        funders.append(funder)
        broader_data = data.get("broader",{})
        if broader_data:
            url = broader_data["resource"]
            #print("Broader Funding Data:", url)
            response = requests.get(url)
        else:
            #print("No further broader data found.")
            break
        
    if funders:
        broader_data = " : ".join(funders[::-1])
        return broader_data
    else:
        return None

def process_dois(doi_file, output_file):
    with open(doi_file, "r") as file:
        dois = file.read().splitlines()

    with open(output_file, "w") as output:
        start_time = datetime.datetime.now()

        total=0
        fail=0

        for doi in dois:
            funder_info = retrieve_funder_info(doi)
            
            output.write(f"Funder information for publication with DOI: {doi}\n")
            
            if funder_info:
                for funder in funder_info:
                    funder_doi = funder.get("DOI")
                    if funder_doi:
                        funder_name = retrieve_broader_data(funder_doi)
                    else:
                        funder_name = funder.get("name")
                    grant_ids = funder.get("award")
                    
                    output.write(f"Funder Name: {funder_name}\n")
                    output.write(f"Grant IDs: {grant_ids}\n")
                    output.write("\n")
            
                
            else:
                output.write(f"No funder information found for publication with DOI: {doi}\n")
                fail+=1
            
            output.write("---\n")
            total+=1
        end_time = datetime.datetime.now()
        output.write(f"Total execution time:{(end_time - start_time).total_seconds()} sesconds\n")
        request_per_second = total/(end_time - start_time).total_seconds()
        output.write(f"Request per second: {request_per_second}\n")
        success=((total-fail)/total)*100
        output.write(f"Success rate: {success:.2f}%\n")



# Example 
doi_file = "dois.txt"
output_file = "funder_output.txt"
process_dois(doi_file, output_file)