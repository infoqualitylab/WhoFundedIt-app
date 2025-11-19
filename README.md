# WhoFundedIt app

## Description
This app retrieves funder names and other funder information (grant, country, funding body type) for a list of 
publications based on their Digital Object Identifiers (DOIs) using the Crossref API. It also retrieves sponsor name and class
for a list of publications based on their National Clinical Trial Identifiers (NCTIDs) using the ClinicalTrials.gov API.
The input can be either a text box entry or a .txt file. To view the live website version of this app, go to:
https://corinnemc-whofundedit-app.share.connect.posit.cloud/

## Setup
Follow these steps to set up the code
1. Install required packages listed in requirements.txt into your environment
2. Open folder in Visual Studio Code (currently using the November 2024 version 1.96)
3. Run app.py

## Contributors
- Deyuan Yang (@Doreenyang) drafted initial code for the app
- Corinne McCumber (@corinnemc) refactored code to address speed issues, updated layout, and deployed app.
- Colby Vorland provided base code that was refactored to query ClinicalTrials.gov
