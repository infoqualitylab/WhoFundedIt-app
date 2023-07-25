from shiny import App, render, ui, Inputs, Outputs, Session
from funderData import retrieve_funder_info, retrieve_broader_data, process_dois,count_funder
import mimetypes
from math import ceil
from typing import List
import asyncio
import io
from datetime import date
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
import shinyswatch


# A card component wrapper.
def ui_card(title, *args):
    return (
        ui.div(
            {"class": "card mb-4"},
            ui.div(title, class_="card-header"),
            ui.div({"class": "card-body"}, *args),
        ),
    )


app_ui = ui.page_fluid(
#app_ui = ui.page_navbar(
    # Available themes:
    #  cerulean, cosmo, cyborg, darkly, flatly, journal, litera, lumen, lux,
    #  materia, minty, morph, pulse, quartz, sandstone, simplex, sketchy, slate,
    #  solar, spacelab, superhero, united, vapor, yeti, zephyr
    shinyswatch.theme.lumen(),
    #ui code for uploading file and display file content
    ui.input_file("file1", "Choose a file to upload:", multiple=False),
    ui.input_radio_buttons("type", "Type:", ["Text", "Other"]),
    ui.output_text_verbatim("file_content"),
    
    #ui code for display funder information for DOI file
    ui.output_text_verbatim("funder_list_text"),


    #ui code for download funder list in .txt file
    ui_card(
        "Download Funder List.",
        ui.download_button("download_funder_file", "Download File"),
    ),

    
    ui.output_text("funder_list", "Funder Names:"),
    ui.output_text_verbatim("funder_names_formatted"),
    ui.output_text_verbatim("funder_names_dic"),

    ui.output_plot("funder_plot",width = "80%",height="600px"),

    #ui code for input one DOI in text box
    ui.input_text_area("x", "DOI Input", placeholder="Enter text"),
    ui.output_text_verbatim("txt"),
    
)


def server(input, output, session):
    MAX_SIZE = 50000
    #code for displaying input file content
    @output
    @render.text
    def file_content():
        file_infos=input.file1()
        if not file_infos:
            return
        out_str=""
        for file_info in file_infos:
            out_str += (
                "=" * 47
                + "\n"
                + file_info["name"]
                + "\nMIME type: "
                + str(mimetypes.guess_type(file_info["name"])[0])
            )
            if file_info["size"] > MAX_SIZE:
                out_str += f"\nTruncating at {MAX_SIZE} bytes."

            out_str += "\n" + "=" * 47 + "\n"

            if input.type() == "Text":
                with open(file_info["datapath"], "r") as f:
                    out_str += f.read(MAX_SIZE)
        return out_str
    
    #code for output funder list in text box
    @output
    @render.text
    def funder_list_text():
        file_infos=input.file1()
        if not file_infos:
            return
        dois=""
        out_str=""
        for file_info in file_infos:
            if file_info["size"] > MAX_SIZE:
                out_str += f"\nTruncating at {MAX_SIZE} bytes."

            #out_str += "\n" + "=" * 47 + "\n"

            if input.type() == "Text":
                out_str=process_dois(file_info["datapath"])
        return out_str
    
    

    #code for output funder list in .txt file
    @session.download(filename="funder_output.txt")
    async def download_funder_file():
        await asyncio.sleep(0.25)
        
        file_infos=input.file1()
        if not file_infos:
            yield
        dois=""
        out_str=""
        for file_info in file_infos:
            if file_info["size"] > MAX_SIZE:
                out_str += f"\nTruncating at {MAX_SIZE} bytes."

            #out_str += "\n" + "=" * 47 + "\n"

            if input.type() == "Text":
                out_str=process_dois(file_info["datapath"])
        yield out_str
        # funder_list = funder_list_text()
        # if funder_list:
        #     out_str = "\n\n".join(funder_list)
        #     yield out_str

    #code for input one DOI in text box.
    @output
    @render.text
    def txt():
        doi=input.x()
        return oneDoiText(doi)
    

    def oneDoiText(doi):
        #start_time = datetime.datetime.now()
        funder_list=[]
        # total=0
        # fail=0

        funder_info = retrieve_funder_info(doi)
            
            #return [f"Funder information for publication with DOI: {doi}\n"]
            
        if funder_info:
            for funder in funder_info:
                funder_doi = funder.get("DOI")
                if funder_doi:
                    funder_name = retrieve_broader_data(funder_doi)
                else:
                    funder_name = funder.get("name")
                grant_ids = funder.get("award")
                    
                    # output.write(f"Funder Name: {funder_name}\n")
                    # output.write(f"Grant IDs: {grant_ids}\n")
                    # output.write("\n")
                funder_list.append(f"Funder Name: {funder_name}")
                funder_list.append(f"Grant Number: {grant_ids}")
            return funder_list
             
        else:
            return [f"No funder information found for publication with DOI: {doi}"]

    # dic for funder data count
    @output
    @render.text 
    def funder_names_dic():
        file_infos=input.file1()
        if not file_infos:
            return {}
        count = {}
        for file_info in file_infos:
            if input.type() == "Text":
                count = count_funder(file_info["datapath"])
        return count
    
    #display formatted funder count data
    @output
    @render.text 
    def funder_names_formatted():
        return
    
    #plot for funder and count
    @output
    @render.plot(alt="A bar plot")
    def funder_plot():
        file_infos = input.file1()
        if not file_infos:
            return {}

        count = {}
        for file_info in file_infos:
            if input.type() == "Text":
                file_count = count_funder(file_info["datapath"])
                for funder_name, funder_count in file_count.items():
                    count[funder_name] = count.get(funder_name, 0) + funder_count

        x = list(count.keys())
        y = list(count.values())

        fig, ax = plt.subplots(figsize=(10, 10))
        ax.bar(x, y)
        plt.xlabel("Funder")
        plt.ylabel("Count")
        plt.title("Funder Information Counts")
        plt.xticks(rotation=45, ha='right', fontsize=8)

        return fig
        
    
        


            
    
        # fig, ax = plt.subplots(figsize=(10, 6))
        # ax.hist(range(len(funder_names)), counts, align='mid')
        # ax.set_xticks(range(len(funder_names)))
        # ax.set_xticklabels(funder_names, rotation=45)
        # plt.xlabel("Funder")
        # plt.ylabel("Count")
        # plt.title("Funder Information Counts")
        # return fig
    

app = App(app_ui, server, debug=True)