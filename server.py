from shiny import render, reactive, ui
from query_crossref import *
import matplotlib.pyplot as plt


def server(input, output, session):
    @reactive.calc
    def app_read_input_file():
        if (input.type() == "Text") & (bool(input.user_file())):
            file = input.user_file()
            input_list = read_input_file(file[0]["datapath"])
            cleaned_input_list = clean_input_list(input_list)
            return {'clean_input_list': cleaned_input_list}
        elif bool(input.single_doi()):
            input_list = []
            input_list.append(input.single_doi())
            cleaned_input_list = clean_input_list(input_list)
            return {'clean_input_list': cleaned_input_list}
        else:
            return {'clean_input_list': 'Input is invalid.'}

    @output
    @render.text
    def app_clean_input_list():
        return f"{app_read_input_file()['clean_input_list']}"

    @reactive.calc
    @reactive.event(input.query_button)
    def app_query():
        p = ui.Progress()
        p.set(message="Computing, please wait...")
        query_input = app_read_input_file()['clean_input_list']

        (identifier_with_error_list,
        identifier_with_no_funder_list,
        bottom_level_funder_dictionary,
        nested_detailed_funder_dictionary,
        nested_funding_body_type_dictionary,
        nested_countries_dictionary,
        nested_grant_dictionary) = query_crossref(query_input)
        p.close()

        return {"identifier_with_error_list": identifier_with_error_list,
                "identifier_with_no_funder_list": identifier_with_no_funder_list,
                "bottom_level_funder_dictionary": bottom_level_funder_dictionary,
                "nested_detailed_funder_dictionary": nested_detailed_funder_dictionary,
                "nested_funding_body_type_dictionary": nested_funding_body_type_dictionary,
                "nested_countries_dictionary": nested_countries_dictionary,
                "nested_grant_dictionary": nested_grant_dictionary}

    @output
    @render.text
    def app_query_errors():
        if len(app_query()['identifier_with_error_list']) != 1:
            return f"{len(app_query()['identifier_with_error_list'])} DOIs with errors: \n \
                {app_query()['identifier_with_error_list']}"
        else:
            return f"{len(app_query()['identifier_with_error_list'])} DOI with errors: \n \
                {app_query()['identifier_with_error_list']}"

    @output
    @render.text
    def app_query_no_funders():
        return f"Items with no funder: {app_query()['identifier_with_no_funder_list']}"

    @output
    @render.table(index=True)
    def summary_table():
        df = create_summary_table(app_query()['nested_detailed_funder_dictionary'],
                                  app_query()['nested_funding_body_type_dictionary'],
                                  app_query()['nested_countries_dictionary'],
                                  app_query()['nested_grant_dictionary'])
        return df.style.set_table_attributes(
            'class="dataframe shiny-table table w-auto"'
        ).set_table_styles(
                    [dict(selector="th", props=[("text-align", "left")])]
                )

    @output
    @render.text
    def app_query_result():
        return (f"Most-specific (bottom-level) funders dictionary: {app_query()['bottom_level_funder_dictionary']} \n"
                f"Complete chain of funders: {app_query()['nested_detailed_funder_dictionary']} \n"
                f"Funding body type(s): {app_query()['nested_funding_body_type_dictionary']} \n"
                f"Funder countries: {app_query()['nested_countries_dictionary']} \n"
                f"Grants by funder: {app_query()['nested_grant_dictionary']} \n"
                )

    @output
    @render.plot
    def funder_name():
        (detailed_name_list,
         broad_name_list,
         name_none_list) = create_name_list(app_query()["nested_detailed_funder_dictionary"])

        (fig1,
         fig2,
         sorted_broad_name_frequency,
         name_none_list) = create_name_chart(detailed_name_list,
                                             broad_name_list,
                                             name_none_list)
        return fig1

    @output
    @render.plot
    def funder_name_pie():
        (detailed_name_list,
         broad_name_list,
         name_none_list) = create_name_list(app_query()["nested_detailed_funder_dictionary"])

        (fig1,
         fig2,
         sorted_broad_name_frequency,
         name_none_list) = create_name_chart(detailed_name_list,
                                             broad_name_list,
                                             name_none_list)
        return fig2

    @output
    @render.plot
    def funding_body_type():
        (type_list,
         type_none_list) = create_funding_type_list(app_query()["nested_funding_body_type_dictionary"])

        (fig5,
         fig6,
         sorted_type_frequency,
         type_none_list) = create_funding_type_chart(type_list,
                                                     type_none_list)
        return fig5

    @output
    @render.plot
    def funding_body_type_pie():
        (type_list,
         type_none_list) = create_funding_type_list(app_query()["nested_funding_body_type_dictionary"])

        (fig5,
         fig6,
         sorted_type_frequency,
         type_none_list) = create_funding_type_chart(type_list,
                                                     type_none_list)
        return fig6

    @output
    @render.plot
    def country():
        (country_list,
         country_none_list) = create_country_list(app_query()["nested_countries_dictionary"])

        (fig3,
         fig4,
         sorted_country_frequency,
         country_none_list) = create_country_chart(country_list,
                                                   country_none_list)
        return fig3

    @output
    @render.plot
    def country_pie():
        (country_list,
         country_none_list) = create_country_list(app_query()["nested_countries_dictionary"])

        (fig3,
         fig4,
         sorted_country_frequency,
         country_none_list) = create_country_chart(country_list,
                                                   country_none_list)
        return fig4

