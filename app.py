from shiny import App, ui
from server import *


def ui_card(title, *args):
    return (
        ui.div(
            {"class": "card mb-4"},
            ui.div(title, class_="card-header"),
            ui.div({"class": "card-body"}, *args),
        ),
    )


crossref_page = ui.page_fluid(
    ui.markdown(
        """
        # Querying Crossref
        ### What this page does:
          This page queries [Crossref](https://www.crossref.org/) 
          for funder information tied to a given list of identifiers for different publications.
          It then returns table and text versions of the information retrieved and visualizations comparing the 
          publications in aggregate. See the "How to use this app" and "Example usage" pages for more information.
        """
    ),

    ui.panel_well(
        ui.h3("Test a single ", ui.tags.u("Digital Object Identifier (DOI)"), ":"),
        ui.input_text_area("single_doi",
                           "DOI in format https://doi.org/10.XXXX/XXXX or 10.XXXX/XXXX",
                           placeholder="Enter DOI here",
                           value="10.1145/2566486.2568023"),
    ),

    ui.panel_well(
        ui.h3("Upload a ", ui.tags.u("DOI"), " file:"),
        ui.input_file("crossref_user_file", "Choose a file to upload:", multiple=False),
        ui.input_radio_buttons("crossref_type", "Type:", ["Text", "Other"]),
    ),

    ui.panel_well(
        ui.h3("Input data"),
        ui.output_text_verbatim("app_crossref_clean_input_list"),
        ui.h3("Click button to query Crossref"),
        ui.input_action_button("query_crossref_button",
                               "Query Crossref",
                               class_="btn-success btn-lg",)
    ),

    ui.panel_well(
        ui.h3("Results"),
        ui.p('If Crossref metadata is inaccurate or incomplete, the visualizations, tables, and '
             'text returned will also be inaccurate. Further, discrepancies in how funders are listed '
             'can result in different totals for the tables and the plots. For example, if the same funder is listed '
             'multiple times because they provided multiple grants, the total funders listed in the table will be less '
             'than the total funders listed on the plots.'),
        ui.navset_card_tab(
            ui.nav_panel("Item-to-funder table",
                ui_card(
                    ui.h4("Item-to-funder table:"),
                    ui.output_table("crossref_item_to_funder_table"),
                ),
            ),

            ui.nav_spacer(),

            ui.nav_panel("Funder-to-item table",
                ui_card(
                    ui.h4("Summary funder-to-item table:"),
                    ui.output_table("crossref_summary_funder_to_item_table")
                ),

                ui_card(
                    ui.h4("Detailed funder-to-item table:"),
                    ui.output_table("crossref_detailed_funder_to_item_table")
                )
            ),

            ui.nav_spacer(),

            ui.nav_panel("Plots",
                ui.panel_well(
                    ui.h3("Plots"),
                    output_widget("crossref_funder_name", height='85vh', width='85vw'),
                    output_widget("crossref_funder_name_pie", height='85vh', width='85vw'),
                    output_widget("crossref_funding_body_type", height='85vh', width='85vw'),
                    output_widget("crossref_funding_body_type_pie", height='85vh', width='85vw'),
                    output_widget("crossref_country", height='85vh', width='85vw'),
                    output_widget("crossref_country_pie", height='85vh', width='85vw'),
                ),
            ),

            ui.nav_spacer(),

            ui.nav_panel("Query results and errors",
                         ui.h3("Query results and errors"),

                         ui_card(
                             ui.h4("Work identifiers with errors:"),
                             ui.output_text_verbatim("app_query_crossref_errors")
                         ),

                         ui_card(
                             ui.h4("Work identifiers without listed funders:"),
                             ui.output_text_verbatim(f"app_query_crossref_no_funders")
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
                             ui.output_text_verbatim("app_query_crossref_result")
                         ),
                         ),

        ),
        id="tab",
    )
)

clinicaltrials_page = ui.page_fluid(
    ui.markdown(
        """
        # Querying <span>ClinicalTrials.gov</span>
        ### What this page does:
          This page queries [ClinicalTrials.gov](https://www.clinicaltrials.gov/) 
          for sponsor and collaborator information tied to a given list of identifiers for different publications.
          It then returns table and text versions of the information retrieved and visualizations comparing the 
          publications in aggregate. See the "How to use this app" and "Example usage" pages for more information.
          Please note that code to query ClinicalTrials.gov was initially developed by Colby Vorland.
        """
    ),

    ui.panel_well(
        ui.h3("Test a single ", ui.tags.u("National Clinical Trial Identification Number (NCTID)"), ":"),
        ui.input_text_area("single_nctid",
                           "NCTID in format NCT######## or nct########",
                           placeholder="Enter NCTID here",
                           value="NCT06745908"),
    ),

    ui.panel_well(
        ui.h3("Upload a ", ui.tags.u("NCTID"), " file:"),
        ui.input_file("clinicaltrials_user_file", "Choose a file to upload:", multiple=False),
        ui.input_radio_buttons("clinicaltrials_type", "Type:", ["Text", "Other"]),
    ),

    ui.panel_well(
        ui.h3("Input data"),
        ui.output_text_verbatim("app_clinicaltrials_clean_input_list"),
        ui.h3("Click the button to query ClinicalTrials.gov"),
        ui.input_action_button("query_clinicaltrials_button",
                               "Query ClinicalTrials.gov",
                               class_="btn-success btn-lg", )
    ),

    ui.panel_well(
        ui.h3("Results"),
        ui.p('If ClinicalTrials.gov metadata is inaccurate or incomplete, the visualizations, tables, and '
             'text returned will also be inaccurate.'),
        ui.navset_card_tab(
            ui.nav_panel("Item-to-funder table",
                ui_card(
                    ui.h4("Item-to-funder table:"),
                    ui.output_table("clinicaltrials_item_to_funder_table"),
                ),
            ),

            ui.nav_spacer(),

            # ui.nav_panel("Funder-to-item table",
            #     ui_card(
            #         ui.h4("Summary funder-to-item table:"),
            #         ui.output_table("clinicaltrials_summary_funder_to_item_table")
            #     ),
            #
            #     ui_card(
            #         ui.h4("Detailed funder-to-item table:"),
            #         ui.output_table("clinicaltrials_detailed_funder_to_item_table")
            #     )
            # ),
            #
            # ui.nav_spacer(),

            ui.nav_panel("Plots",
                ui.panel_well(
                    ui.h3("Plots"),
                    ui.output_plot("clinicaltrials_sponsor_name", height='90vh', width='90vw'),
                    ui.output_plot("clinicaltrials_sponsor_name_pie", height='90vh', width='90vw'),
                    ui.output_plot("clinicaltrials_sponsor_class", height='90vh', width='90vw'),
                    ui.output_plot("clinicaltrials_sponsor_class_pie", height='90vh', width='90vw'),
            ),
        ),

            ui.nav_spacer(),

            ui.nav_panel("Query results and errors",
                         ui.h3("Query results and errors"),

                         ui_card(
                             ui.h4("Work identifiers with errors:"),
                             ui.output_text_verbatim("app_query_clinicaltrials_errors")
                         ),

                         ui_card(
                             ui.h4("Work identifiers without listed funders:"),
                             ui.output_text_verbatim(f"app_query_clinicaltrials_no_funders")
                         ),

                         ui_card(
                             ui.h4("Results dictionaries\n"),
                             ui.markdown(
                                 """
                                 ##### Format:
                                 ```
                                   {'Work NCTID 1': [specific sponsor information],
                                   'Work NCTID 2': [...]
                                     }
                                ```
                                """
                             ),
                             ui.output_text_verbatim("app_query_clinicaltrials_result")
                         ),
                         ),

        ),
        id="tab",
    )
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
    ui.nav_panel("Query Crossref", crossref_page),
    ui.nav_panel("Query ClinicalTrials.gov", clinicaltrials_page),
    ui.nav_panel("How to use this app", how_to_page),
    ui.nav_panel("Example usage", example_page),
    title=ui.TagList(
            ui.h1("WhoFundedIt"),
            ui.a(f"Created by the Information Quality Lab", href="https://infoqualitylab.org/")
        ),
    window_title="WhoFundedIt"
)

app = App(app_ui, server, debug=False)
