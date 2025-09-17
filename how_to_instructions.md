# How to use the Computable Bibliography
### What this application does:
This application queries [Crossref](https://www.crossref.org/) or [ClinicalTrials.gov](https://www.clinicaltrials.gov) for funder/sponsor information tied to a given list of Digital Object Indentifiers (DOIs) or National Clinical Trial Identification Numbers (NCTIDs) for different publications. It then returns table and text versions of the information retrieved and visualizations comparing the publications in aggregate. 

##### When querying Crossref:
Specifically it uses the Crossref [Work object](https://api.crossref.org/swagger-ui/index.html#/Works/get_works__doi_),
parsing JSON files for each publication queried.

See Crossref documentation for more details: [Non-technical overview](https://www.crossref.org/documentation/retrieve-metadata/rest-api/) 
and [detailed documentation](https://api.crossref.org/swagger-ui/index.html#/), scroll down to Models > Work to see specific attributes

##### When querying <span>ClinicalTrials.gov</span>:
Specifically it uses the <span>ClinicalTrials.gov</span> [Sponsor/Collaborator module](https://clinicaltrials.gov/policy/protocol-definitions#Sponsors), parsing JSON files for each publication queried. Please note, <span>ClinicalTrials.gov</span> [defines a sponsor](https://clinicaltrials.gov/study-basics/glossary#sponsor) as "The organization or person who initiates the study and who has authority and control over the study" and [a
collaborator](https://clinicaltrials.gov/study-basics/glossary#collaborator) as "An organization other than the sponsor that provides support for a clinical study. This support may include activities related to funding, design, implementation, data analysis, or reporting."

See <span>ClinicalTrials.gov</span> documentation for more details: https://clinicaltrials.gov/data-api/api. Class definitions can be found under [AgencyClass](https://clinicaltrials.gov/data-api/about-api/study-data-structure#enum-AgencyClass)
<hr style="border:2px solid gray">

### How to use this application:

##### 1. Either enter a single identifier or create an identifier file, which is a text file (.txt file) of [Digital Object Identifiers (DOIs)](https://en.wikipedia.org/wiki/Digital_object_identifier) or [National Clinical Trial Identification Numbers (NCTIDs)](https://clinicaltrials.gov/data-api/about-api/study-data-structure#NCTId) for all publications you would like to compare.

*Formatting guidelines:*
  - One identifier per line in the text (.txt) file.
  - DOIs can be in any of the following formats:
    - https://doi.org/10.XXX/XXXX
    - doi:10.XXXX/XXXX
    - 10.XXXX/XXXX
  - NCTIDs can be in any of the following formats:

    - NCT######## 
    - nct########
  - The app will ignore blank/empty lines. 

In a citation manager such as [Zotero](https://www.zotero.org/), you can create a DOI file by:
1. Exporting a library or collection to .csv format.
2. Copying the DOI column of the .csv file.
3. Pasting the DOI column into a text editor such as [Notepad](https://apps.microsoft.com/detail/9msmlrh6lzf3?hl=en-us&gl=US) 
(Windows) or [TextEdit](https://support.apple.com/guide/textedit/welcome/mac) (Mac).
4. Saving the resulting file. Blank lines do not need to be removed.
  
You can also manually copy and paste identifiers into a text file using text editor such as [Notepad](https://apps.microsoft.com/detail/9msmlrh6lzf3?hl=en-us&gl=US) 
(Windows) or [TextEdit](https://support.apple.com/guide/textedit/welcome/mac) (Mac). 

---

##### 2. If using an identifier file, on the webpage, click "Browse..." and select the text file you created.
Functionality for files other than text (.txt) is forthcoming.

---

##### 3. Review information listed under "Input data". 
This will show cleaned and standardized versions of the identifiers you submitted

---

##### 4. Hit the button "Query Crossref" or "Query <span>ClinicalTrials.gov</span>"
This will query the Crossref or <span>ClinicalTrials.gov</span> API for each identifier you submit. Large requests can take some time.

---
  
##### 5. View results
The item-to-funder table, funder-to-item table, plots, base query results, and errors are viewable on different tabs.
You will be able to copy the identifiers that had errors when querying the API and the Python dictionaries used to create 
visualizations shown. Code to query APIs, create the text/tables, and generate visualizations is stored on the [Information Quality Lab GitHub](https://github.com/infoqualitylab/WhoFundedIt-app)

<hr style="border:2px solid gray">

### A note on usage:
  If Crossref or ClinicalTrials.gov metadata is inaccurate or incomplete, the visualizations, tables, and text returned will also be inaccurate. 
  Please also note that discrepancies in how funders are listed for Crossref specifically can result in different totals for the tables and the plots.