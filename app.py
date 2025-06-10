from shiny import App, ui
import shinyswatch
from server import *


def ui_card(title, *args):
    return (
        ui.div(
            {"class": "card mb-4"},
            ui.div(title, class_="card-header"),
            ui.div({"class": "card-body"}, *args),
        ),
    )


home_page = ui.page_fluid(
    ui.markdown(
        """
        ### What this application does:
          This application queries [Crossref](https://www.crossref.org/) for funder information tied to a given list of
          Digital Object Indentifiers (DOIs) for different publications. It then returns table and text versions of the information
          retrieved and visualizations comparing the publications in aggregate. See the "How to use this app" and "Example usage" 
          pages for more information.
        """
    ),

    ui.panel_well(
        ui.h3("Test a single DOI:"),
        ui.input_text_area("single_doi",
                           "DOI in format https://doi.org/10.XXXX/XXXX or 10.XXXX/XXXX",
                           placeholder="Enter DOI here"),
    ),

    ui.panel_well(
        ui.h3("Upload a DOI file:"),

        ui.input_file("user_file", "Choose a file to upload:", multiple=False),
        ui.input_radio_buttons("type", "Type:", ["Text", "Other"]),
    ),

    ui.panel_well(
        ui.h3("Input data"),
        ui.output_text_verbatim("app_clean_input_list"),
        ui.h3("Query Crossref"),
        ui.input_action_button("query_button", "Query Crossref")
    ),

    ui.panel_well(
        ui.h3("Query results"),

        ui_card(
            ui.h4("Work identifiers with errors:"),
            ui.output_text_verbatim("app_query_errors")
        ),

        ui_card(
            ui.h4("Work identifiers without listed funders:"),
            ui.output_text_verbatim(f"app_query_no_funders")
        ),

        ui_card(
            ui.h4("Funder information in table form:"),
            ui.output_table("summary_table")
        ),

        ui_card(
            ui.h4("Nested dictionaries\n"),
            ui.markdown(
                """
                ##### Format:
                ```
                {'Work DOI 1': [
                       {'Funder DOI 1': 'specific funder information'},
                       {'Funder DOI 2': 'specific funder information'}
                       ],
                  'Work DOI 2': [...]
                 }
                ```
                """
            ),
            ui.output_text_verbatim("app_query_result")
        ),
    ),

    ui.panel_well(
        ui.h3("Plots"),
        ui.output_plot("funder_name", height='90vh', width='90vw'),
        ui.output_plot("funder_name_pie", height='90vh', width='90vw'),
        ui.output_plot("funding_body_type", height='90vh', width='90vw'),
        ui.output_plot("funding_body_type_pie", height='90vh', width='90vw'),
        ui.output_plot("country", height='90vh', width='90vw'),
        ui.output_plot("country_pie", height='90vh', width='90vw'),
    ),
)

with open('how_to_instructions.md', 'r') as file:
    how_to_markdown_file = file.read()

how_to_page = ui.markdown(how_to_markdown_file)

with open('example_page.md', 'r') as file:
    example_markdown_file = file.read()

example_page = ui.page_fluid(
    ui.markdown(example_markdown_file)
)

app_ui = ui.page_navbar(
    ui.nav_spacer(),
    ui.nav_panel("Home", home_page),
    ui.nav_panel("How to use this app", how_to_page),
    ui.nav_panel("Example usage", example_page),
    title=ui.TagList(
            ui.h1("WhoFundedIt"),
            ui.a(f"Created by the Information Quality Lab", href="https://infoqualitylab.org/")
        ),
    window_title="WhoFundedIt"
)

# app_ui = ui.page_fluid(
#
#     ui.panel_well(
#         ui.h2("Test a single DOI:"),
#         # ui code for inputting single DOI in text box
#         ui.input_text_area("single_doi", "DOI Input", placeholder="Enter text"),
#         # ui code to display funder list from single DOI
#         ui.output_text_verbatim("single_doi_funder_list")
#     ),
#
#     ui.panel_well(
#         ui.h2("Upload a DOI file:"),
#
#         # ui code for uploading file
#         ui.input_file("user_file", "Choose a file to upload:", multiple=False),
#         ui.input_radio_buttons("type", "Type:", ["Text", "Other"]),
#
#         # ui code to display file content
#         ui_card(
#             "Uploaded file contents:",
#             ui.output_text_verbatim("user_file_content")
#         ),
#
#         # ui code to display funder information for DOI file
#         ui_card(
#             "Funder list:",
#             ui.output_text_verbatim("user_file_funder_list")
#         ),
#
#         # ui code for download funder list in .txt file
#         ui_card(
#             "Download funder list:",
#             ui.download_button("download_funder_list_file", "Download")
#         )
#     ),
#
#     ui.panel_well(
#         ui.h2("Aggregate outputs:"),
#         ui_card(
#             "Python dictionary count of funders:",
#             # ui code to display funder count dictionary
#             ui.output_text_verbatim("funder_count_dictionary")
#         ),
#
#         ui_card(
#             "Plot of funders:",
#             ui.output_plot("funder_plot", width="100%", height="600px")
#         )
#     ),
#
#     # Available themes:
#     #  cerulean, cosmo, cyborg, darkly, flatly, journal, litera, lumen, lux,
#     #  materia, minty, morph, pulse, quartz, sandstone, simplex, sketchy, slate,
#     #  solar, spacelab, superhero, united, vapor, yeti, zephyr
#     theme=shinyswatch.theme.pulse()
# )


app = App(app_ui, server, debug=False)
