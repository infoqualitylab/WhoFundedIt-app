# How to use the Computable Bibliography
### What this application does:
This application queries [Crossref](https://www.crossref.org/) for funder information tied to a given list of
Digital Object Indentifiers (DOIs) for different publications. It then returns table and text versions of the information
retrieved and visualizations comparing the publications in aggregate. Specifically it uses the Crossref [Work object](https://api.crossref.org/swagger-ui/index.html#/Works/get_works__doi_),
parsing JSON files for each publication queried.

See Crossref documentation for more details: [Non-technical overview](https://www.crossref.org/documentation/retrieve-metadata/rest-api/) 
and [detailed documentation](https://api.crossref.org/swagger-ui/index.html#/), scroll down to Models > Work to see specific attributes

<hr style="border:2px solid gray">

### How to use this application:

##### 1. Either enter a single DOI or create a DOI file, which is a text file (.txt file) of [Digital Object Identifiers (DOIs)](https://en.wikipedia.org/wiki/Digital_object_identifier) for all publications you would like to compare.

*Formatting guidelines:*
  - One DOI per line in the text (.txt) file.
  - DOIs can be in any of the following formats:
    - https://doi.org/10.XXX/XXXX
    - doi:10.XXXX/XXXX
    - 10.XXXX/XXXX
  - The app will ignore blank/empty lines. 

In a citation manager such as [Zotero](https://www.zotero.org/), you can create a DOI file by:
1. Exporting a library or collection to .csv format.
2. Copying the DOI column of the .csv file.
3. Pasting the DOI column into a text editor such as [Notepad](https://apps.microsoft.com/detail/9msmlrh6lzf3?hl=en-us&gl=US) 
(Windows) or [TextEdit](https://support.apple.com/guide/textedit/welcome/mac) (Mac).
4. Saving the resulting file. Blank lines do not need to be removed.
  
You can also manually copy and paste DOIs into a text file using text editor such as [Notepad](https://apps.microsoft.com/detail/9msmlrh6lzf3?hl=en-us&gl=US) 
(Windows) or [TextEdit](https://support.apple.com/guide/textedit/welcome/mac) (Mac). 

---

##### 2. If using a DOI file, on the webpage, click "Browse..." and select the text file you created.
Functionality for files other than text (.txt) is forthcoming.

---

##### 3. Review information listed under "Input data". 
This will show cleaned and standardized versions of the DOIs you submitted

---

##### 4. Hit the button "Query Crossref"
This will query the Crossref API for each DOI you submit. Large requests can take some time.

---
  
##### 5. View results
You will be able to copy the identifiers that had errors when querying Crossref and the Python dictionaries used to create 
visualizations shown. Code to query Crossref, create the text/tables, and generate visualizations is stored on the [Information Quality Lab GitHub](https://github.com/infoqualitylab/WhoFundedIt-app)

<hr style="border:2px solid gray">

### A note on usage:
  If Crossref metadata is inaccurate or incomplete, the visualizations, tables, and text returned will also be inaccurate.