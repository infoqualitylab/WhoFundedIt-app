from shiny import render, reactive, ui
from shinywidgets import output_widget, render_widget
from query_crossref import *
from query_clinicaltrials import *
import matplotlib.pyplot as plt


def server(input, output, session):
    @reactive.calc
    def app_crossref_read_input_file():
        if (input.crossref_type() == "Text") & (bool(input.crossref_user_file())):
            file = input.crossref_user_file()
            input_list = crossref_read_input_file(file[0]["datapath"])
            cleaned_input_list = crossref_clean_input_list(input_list)
            return {'clean_input_list': cleaned_input_list}
        elif bool(input.single_doi()):
            input_list = [input.single_doi()]
            cleaned_input_list = crossref_clean_input_list(input_list)
            return {'clean_input_list': cleaned_input_list}
        else:
            return {'clean_input_list': 'Input is missing or invalid.'}

    @output
    @render.text
    def app_crossref_clean_input_list():
        return f"{app_crossref_read_input_file()['clean_input_list']}"

    @reactive.calc
    @reactive.event(input.query_crossref_button, ignore_none=False)
    def app_query_crossref():
        p = ui.Progress()
        p.set(message="Computing, please wait...")
        query_crossref_input = app_crossref_read_input_file()['clean_input_list']

        (identifier_with_error_list,
         identifier_with_no_funder_list,
         bottom_level_funder_dictionary,
         nested_detailed_funder_dictionary,
         nested_funding_body_type_dictionary,
         nested_countries_dictionary,
         nested_grant_dictionary) = query_crossref(query_crossref_input)
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
    def app_query_crossref_errors():
        if len(app_query_crossref()['identifier_with_error_list']) != 1:
            return f"{len(app_query_crossref()['identifier_with_error_list'])} DOIs with errors: \n \
                {app_query_crossref()['identifier_with_error_list']}"
        else:
            return f"{len(app_query_crossref()['identifier_with_error_list'])} DOI with errors: \n \
                {app_query_crossref()['identifier_with_error_list']}"

    @output
    @render.text
    def app_query_crossref_no_funders():
        return f"Items with no funder: {app_query_crossref()['identifier_with_no_funder_list']}"

    @output
    @render.text
    def app_query_crossref_result():
        return (f"Most-specific (bottom-level) funders dictionary: {app_query_crossref()['bottom_level_funder_dictionary']} \n"
                f"Complete chain of funders: {app_query_crossref()['nested_detailed_funder_dictionary']} \n"
                f"Funding body type(s): {app_query_crossref()['nested_funding_body_type_dictionary']} \n"
                f"Funder countries: {app_query_crossref()['nested_countries_dictionary']} \n"
                f"Grants by funder: {app_query_crossref()['nested_grant_dictionary']} \n"
                )

    @reactive.calc
    def crossref_table_calculations():
        item_to_funder_df = crossref_create_item_to_funder_table(app_query_crossref()['nested_detailed_funder_dictionary'],
                                                                       app_query_crossref()['nested_funding_body_type_dictionary'],
                                                                       app_query_crossref()['nested_countries_dictionary'],
                                                                       app_query_crossref()['nested_grant_dictionary'])
        (detail_funder_to_item_df, summary_funder_to_item_df) \
            = crossref_create_funder_to_item_table(app_query_crossref()['nested_detailed_funder_dictionary'],
                                          app_query_crossref()['nested_funding_body_type_dictionary'],
                                          app_query_crossref()['nested_countries_dictionary'],
                                          app_query_crossref()['nested_grant_dictionary'])

        return {"item_to_funder_df": item_to_funder_df,
                "summary_funder_to_item_df": summary_funder_to_item_df,
                "detail_funder_to_item_df": detail_funder_to_item_df}

    @output
    @render.table(index=True)
    def crossref_item_to_funder_table():
        df = crossref_table_calculations()['item_to_funder_df']
        return df.style.set_table_attributes(
            'class="dataframe shiny-table table w-auto"'
        ).set_table_styles(
                    [dict(selector="th", props=[("text-align", "left")])]
                )

    @output
    @render.table(index=True)
    def crossref_summary_funder_to_item_table():
        df = crossref_table_calculations()['summary_funder_to_item_df']
        return df.style.set_table_attributes(
            'class="dataframe shiny-table table w-auto"'
        ).set_table_styles(
                    [dict(selector="th", props=[("text-align", "left")])]
                )

    @output
    @render.table(index=True)
    def crossref_detailed_funder_to_item_table():
        df = crossref_table_calculations()['detail_funder_to_item_df']
        return df.style.set_table_attributes(
            'class="dataframe shiny-table table w-auto"'
        ).set_table_styles(
                    [dict(selector="th", props=[("text-align", "left")])]
                )

    @reactive.calc
    def crossref_funder_name_calculations():
        (detailed_name_list,
         broad_name_list,
         name_none_list) = create_name_list(app_query_crossref()["nested_detailed_funder_dictionary"])

        (fig1,
         fig2,
         sorted_broad_name_frequency,
         name_none_list) = create_name_chart(detailed_name_list,
                                                            broad_name_list,
                                                            name_none_list)
        return {"fig1": fig1,
                "fig2": fig2}

    @output
    @render_widget
    def crossref_funder_name():
        return crossref_funder_name_calculations()['fig1']

    @output
    @render_widget
    def crossref_funder_name_pie():
        return crossref_funder_name_calculations()['fig2']

    @reactive.calc
    def crossref_funder_body_type_calculations():
        (type_list,
         type_none_list) = create_funding_type_list(app_query_crossref()["nested_funding_body_type_dictionary"])

        (fig5,
         fig6,
         sorted_type_frequency,
         type_none_list) = create_funding_type_chart(type_list,
                                                     type_none_list)
        return {'fig5': fig5,
                'fig6': fig6}

    @output
    @render_widget
    def crossref_funding_body_type():
        return crossref_funder_body_type_calculations()['fig5']

    @output
    @render_widget
    def crossref_funding_body_type_pie():
        return crossref_funder_body_type_calculations()['fig6']

    @reactive.calc
    def crossref_country_calculations():
        (country_list,
         country_none_list) = create_country_list(app_query_crossref()["nested_countries_dictionary"])

        (fig3,
         fig4,
         sorted_country_frequency,
         country_none_list) = create_country_chart(country_list,
                                                   country_none_list)
        return {'fig3': fig3,
                'fig4': fig4}

    @output
    @render_widget
    def crossref_country():
        return crossref_country_calculations()['fig3']

    @output
    @render_widget
    def crossref_country_pie():
        return crossref_country_calculations()['fig4']

    @reactive.calc
    def app_clinicaltrials_read_input_file():
        if (input.clinicaltrials_type() == "Text") & (bool(input.clinicaltrials_user_file())):
            file = input.clinicaltrials_user_file()
            input_list = clinicaltrials_read_input_file(file[0]["datapath"])
            cleaned_input_list = clinicaltrials_clean_input_list(input_list)
            return {'clean_input_list': cleaned_input_list}
        elif bool(input.single_nctid()):
            input_list = [input.single_nctid()]
            cleaned_input_list = clinicaltrials_clean_input_list(input_list)
            return {'clean_input_list': cleaned_input_list}
        else:
            return {'clean_input_list': 'Input is missing or invalid.'}

    @output
    @render.text
    def app_clinicaltrials_clean_input_list():
        return f"{app_clinicaltrials_read_input_file()['clean_input_list']}"

    @reactive.calc
    @reactive.event(input.query_clinicaltrials_button, ignore_none=False)
    def app_query_clinicaltrials():
        p = ui.Progress()
        p.set(message="Computing, please wait...")
        query_clinicaltrials_input = app_clinicaltrials_read_input_file()['clean_input_list']

        (identifier_with_error_list,
         identifier_with_no_funder_list,
         bottom_level_funder_dictionary,
         lead_sponsor_dictionary,
         lead_sponsor_class_dictionary,
         all_collaborators_dictionary,
         collaborator_class_dictionary) = query_clinicaltrials(query_clinicaltrials_input)
        p.close()

        return {"identifier_with_error_list": identifier_with_error_list,
                "identifier_with_no_funder_list": identifier_with_no_funder_list,
                "bottom_level_funder_dictionary": bottom_level_funder_dictionary,
                "lead_sponsor_dictionary": lead_sponsor_dictionary,
                "lead_sponsor_class_dictionary": lead_sponsor_class_dictionary,
                "all_collaborators_dictionary": all_collaborators_dictionary,
                "collaborator_class_dictionary": collaborator_class_dictionary}

    @output
    @render.text
    def app_query_clinicaltrials_errors():
        if len(app_query_clinicaltrials()['identifier_with_error_list']) != 1:
            return f"{len(app_query_clinicaltrials()['identifier_with_error_list'])} NCTIDs with errors: \n \
                {app_query_clinicaltrials()['identifier_with_error_list']}"
        else:
            return f"{len(app_query_clinicaltrials()['identifier_with_error_list'])} NCTID with errors: \n \
                {app_query_clinicaltrials()['identifier_with_error_list']}"

    @output
    @render.text
    def app_query_clinicaltrials_no_funders():
        return f"Items with no funder: {app_query_clinicaltrials()['identifier_with_no_funder_list']}"

    @output
    @render.text
    def app_query_clinicaltrials_result():
        return (f"Most-specific (bottom-level) sponsors dictionary: {app_query_clinicaltrials()['bottom_level_funder_dictionary']} \n"
                f"Lead sponsor names: {app_query_clinicaltrials()['lead_sponsor_dictionary']} \n"
                f"Lead sponsor classes: {app_query_clinicaltrials()['lead_sponsor_class_dictionary']} \n"
                f"Collaborator names: {app_query_clinicaltrials()['all_collaborators_dictionary']} \n"
                f"Collaborator classes: {app_query_clinicaltrials()['collaborator_class_dictionary']} \n"
                )

    @reactive.calc
    def clinicaltrials_table_calculations():
        item_to_funder_df = clinicaltrials_create_item_to_funder_table(app_query_clinicaltrials()['lead_sponsor_dictionary'],
                                                                       app_query_clinicaltrials()['lead_sponsor_class_dictionary'])

        return {"item_to_funder_df": item_to_funder_df}

    @output
    @render.table(index=True)
    def clinicaltrials_item_to_funder_table():
        df = clinicaltrials_table_calculations()['item_to_funder_df']
        return df.style.set_table_attributes(
            'class="dataframe shiny-table table w-auto"'
        ).set_table_styles(
                    [dict(selector="th", props=[("text-align", "left")])]
                )

    @reactive.calc
    def clinicaltrials_sponsor_name_calculations():
        (fig1, fig2, sorted_lead_sponsor_frequency) \
            = clinicaltrials_create_name_chart(app_query_clinicaltrials()['lead_sponsor_dictionary'])

        (fig3, fig4, sorted_lead_sponsor_class_frequency) \
            = create_lead_sponsor_class_chart(app_query_clinicaltrials()['lead_sponsor_class_dictionary'])
        return {"fig1": fig1,
                "fig2": fig2,
                "fig3": fig3,
                "fig4": fig4,}

    @output
    @render.plot
    def clinicaltrials_sponsor_name():
        return clinicaltrials_sponsor_name_calculations()['fig1']

    @output
    @render.plot
    def clinicaltrials_sponsor_name_pie():
        return clinicaltrials_sponsor_name_calculations()['fig2']


    @output
    @render.plot
    def clinicaltrials_sponsor_class():
        return clinicaltrials_sponsor_name_calculations()['fig3']

    @output
    @render.plot
    def clinicaltrials_sponsor_class_pie():
        return clinicaltrials_sponsor_name_calculations()['fig4']
