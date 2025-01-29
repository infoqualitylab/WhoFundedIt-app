from shiny import App, render, ui, reactive
from funderData import retrieve_funder_info, retrieve_broader_data, process_multiple_dois
import mimetypes
import matplotlib.pyplot as plt
import shinyswatch


def ui_card(title, *args):
    return (
        ui.div(
            {"class": "card mb-4"},
            ui.div(title, class_="card-header"),
            ui.div({"class": "card-body"}, *args),
        ),
    )


app_ui = ui.page_fluid(
    ui.panel_title(ui.h1("WhoFundedIt"), window_title="WhoFundedIt"),

    ui.h3("Created by the Information Quality Lab"),

    ui.panel_well(
        ui.h2("Test a single DOI:"),
        # ui code for inputting single DOI in text box
        ui.input_text_area("single_doi", "DOI Input", placeholder="Enter text"),
        # ui code to display funder list from single DOI
        ui.output_text_verbatim("single_doi_funder_list")
    ),

    ui.panel_well(
        ui.h2("Upload a DOI file:"),

        # ui code for uploading file
        ui.input_file("user_file", "Choose a file to upload:", multiple=False),
        ui.input_radio_buttons("type", "Type:", ["Text", "Other"]),

        # ui code to display file content
        ui_card(
            "Uploaded file contents:",
            ui.output_text_verbatim("user_file_content")
        ),

        # ui code to display funder information for DOI file
        ui_card(
            "Funder list:",
            ui.output_text_verbatim("user_file_funder_list")
        ),

        # ui code for download funder list in .txt file
        ui_card(
            "Download funder list:",
            ui.download_button("download_funder_list_file", "Download")
        )
    ),

    ui.panel_well(
        ui.h2("Aggregate outputs:"),
        ui_card(
            "Python dictionary count of funders:",
            # ui code to display funder count dictionary
            ui.output_text_verbatim("funder_count_dictionary")
        ),

        ui_card(
            "Plot of funders:",
            ui.output_plot("funder_plot", width="100%", height="600px")
        )
    ),

    # Available themes:
    #  cerulean, cosmo, cyborg, darkly, flatly, journal, litera, lumen, lux,
    #  materia, minty, morph, pulse, quartz, sandstone, simplex, sketchy, slate,
    #  solar, spacelab, superhero, united, vapor, yeti, zephyr
    theme=shinyswatch.theme.pulse()
)


def server(input, output, session):
    MAX_SIZE = 50000

    # code for input one DOI in text box.
    @reactive.calc
    def processed_funders_from_single_doi():
        funder_list = []
        count = {}
        funder_info = retrieve_funder_info(input.single_doi())

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
                funder_list.append(f"Funder Name: {funder_name}")
                funder_list.append(f"Grant Number: {grant_ids}")
            return {'funder_list': funder_list, 'count': count}
        else:
            return {
                'funder_list': f"No funder information found for publication with DOI: {input.single_doi()}",
                'count': 0
                }

    @output
    @render.text
    def single_doi_funder_list():
        return f"{processed_funders_from_single_doi()['funder_list']}"

    @output
    @render.text
    def user_file_content():
        input_file = input.user_file()
        if not input_file:
            return None
        out_str = ""

        for item in input_file:
            out_str += (
                "=" * 47
                + "\n"
                + item["name"]
                + "\nMIME type: "
                + str(mimetypes.guess_type(item["name"])[0])
            )
            if item["size"] > MAX_SIZE:
                out_str += f"\nTruncating at {MAX_SIZE} bytes."

            out_str += "\n" + "=" * 47 + "\n"

            if input.type() == "Text":
                with open(item["datapath"], "r") as f:
                    out_str += f.read(MAX_SIZE)

        return out_str

    @reactive.calc
    def processed_funders_from_doi_file():
        if (input.type() == "Text") & (bool(input.user_file())):
            file = input.user_file()
            output_string = ""
            count_dictionary = {}
            for file_line in file:
                output_string, count_dictionary = process_multiple_dois(file_line["datapath"])
            return {'funders': output_string, 'funders_count': count_dictionary}
        else:
            return {'funders': "Funder list not generated yet.", 'funders_count': 0}

    @output
    @render.text
    def user_file_funder_list():
        return f"{processed_funders_from_doi_file()['funders']}"

    @render.download()
    def download_funder_list_file():
        with open("WhoFundedIt_output.txt", "w") as f:
            f.write(f"{processed_funders_from_doi_file()['funders']}")
            f.close()

    @output
    @render.text
    def funder_count_dictionary():
        if processed_funders_from_doi_file()['funders_count'] != 0:
            return f"{processed_funders_from_doi_file()['funders_count']}"
        if processed_funders_from_single_doi()['count'] != 0:
            return f"{processed_funders_from_single_doi()['count']}"
        else:
            return "No funder count dictionary generated."

    @output
    @render.plot(alt="A bar plot of funders with the most frequent funders occurring first")
    def funder_plot():
        count = {}
        if processed_funders_from_doi_file()['funders_count'] is not 0:
            count = processed_funders_from_doi_file()['funders_count']

        if count == {}:
            fig, ax = plt.subplots()
            ax.axis('off')
            ax.text(x=0.5, y=0.5, s="No plot generated.")

        else:
            sorted_count = {key: value for key, value in sorted(count.items(), key=lambda item: item[1], reverse=True)}
            x = list(sorted_count.keys())
            y = list(sorted_count.values())

            fig, ax = plt.subplots()
            ax.bar(x, y)
            plt.xlabel("Funder Name")
            plt.ylabel("Frequency")
            plt.title("Funder frequency for provided DOI(s)")
            plt.xticks(rotation=45, ha='right', fontsize=8)
            plt.tight_layout()

        return fig


app = App(app_ui, server, debug=True)
