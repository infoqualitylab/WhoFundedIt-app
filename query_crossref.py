import string
import time
import requests
import re
import numpy as np
import pandas as pd
from collections import Counter, OrderedDict
from matplotlib import pyplot as plt, ticker


def crossref_read_input_file(filename: str):
    """
    Reads an input text file and returns it as a list.

    :param filename: path to the input file
    :return: file contents as a list
    """
    print(filename)
    file = open(filename, "r")
    input_data = file.read()
    input_list = input_data.split("\n")
    file.close()
    return input_list


def crossref_clean_input_list(input_list: list):
    """
    Cleans common errors in input list to get DOIs in format "https://doi.org/10.XXX/XXX" or "doi:10.XXXX/XXX",
    removing duplicates.

    :param input_list: list of DOIs
    :return: cleaned list of DOIs
    """
    cleaned_input_list = []
    for item in input_list:
        if item == '':
            continue
        elif re.search(r'^10\.', item):
            search_item = item
        elif re.search(r'^DOI:', item):
            new_item = re.sub(r'DOI:', '', item, 1)
            search_item = new_item
        elif re.search(r'^DOI: ', item):
            new_item = re.sub(r'DOI: ', '', item, 1)
            search_item = new_item
        elif re.search(r'^doi.org', item):
            new_item = re.sub(r'doi.org/', '', item, 1)
            search_item = new_item
        else:
            search_item = item
        cleaned_input_list.append(search_item.strip())
        cleaned_input_list = list(set(cleaned_input_list))
    return cleaned_input_list


def retrieve_broader_data(funder_identifier):
    """
    Retrieves broader data from Crossref for a specific funder identifier, providing greater detail.
    :param funder_identifier: Identifier of a given funder in Crossref
    :return: list of funders (largest to smallest) under a given identifier
    """
    url = f"https://data.crossref.org/fundingdata/funder/{funder_identifier}"
    response = requests.get(url)

    funders = []
    cycles = 0
    funders_name_dictionary = {}
    funding_body_type_dictionary = {}
    country_dictionary = {}

    while response.status_code == 200:
        cycles += 1
        result = response.json()
        funder_name = result["prefLabel"]["Label"]["literalForm"]["content"]
        funders.append(funder_name)
        while cycles == 1:
            try:
                funding_body = result["fundingBodySubType"]
            except Exception:
                funding_body = None
            funding_body_type_dictionary[funder_identifier] = [funding_body]

            try:
                funding_country = result["address"]["postalAddress"]["addressCountry"]
            except Exception:
                funding_country = None
            country_dictionary[funder_identifier] = [funding_country]

            cycles += 1

        broader_data = result.get("broader", {})
        if broader_data:
            url = broader_data["resource"]
            # print("Broader Funding Data:", url)
            time.sleep(0.02)
            response = requests.get(url)
        else:
            # print("No further broader data found.")
            break

    funders_name_dictionary[funder_identifier] = funders[::-1]

    return funders_name_dictionary, funding_body_type_dictionary, country_dictionary


def query_crossref(cleaned_input_list: list):
    """
    Queries Crossref for funders of items with specific DOIs. See Crossref documentation for more
    details: https://www.crossref.org/documentation/retrieve-metadata/rest-api/ and
    https://api.crossref.org/swagger-ui/index.html#/.

    :param cleaned_input_list: input list of DOIs in format "10.XXX/XXXX"
    :return: list of dictionaries with attributes for Work objects from returned queries in Crossref.
    """
    identifier_with_error_list = []
    identifier_with_no_funder_list = []

    bottom_level_funder_dictionary = {}
    nested_detailed_funder_dictionary = {}
    nested_funding_body_type_dictionary = {}
    nested_countries_dictionary = {}
    nested_grant_dictionary = {}

    for identifier in cleaned_input_list:
        try:
            work_url = f"https://api.crossref.org/works/{identifier}"
            response = requests.get(work_url)
            result = response.json()
            metadata = result['message']

            if "funder" in metadata:
                bottom_level_funder_dictionary[identifier] = metadata['funder']
            else:
                identifier_with_no_funder_list.append(identifier)
            time.sleep(0.02)  # Crossref has a limit of max 50 requests per second.

        except Exception:
            identifier_with_error_list.append(identifier)
            continue

    no_funder_doi_count = 0
    for original_work, funders_list in bottom_level_funder_dictionary.items():
        nested_list_of_funders = []
        nested_list_of_grants = []
        nested_list_of_funding_body_type = []
        nested_list_of_countries = []

        for funder in funders_list:
            funder_doi = funder.get("DOI")
            if funder_doi:
                detailed_funder_dictionary, funding_body_type_dictionary, country_dictionary \
                    = retrieve_broader_data(funder_doi)
            else:
                no_funder_doi_count += 1
                detailed_funder_dictionary, funding_body_type_dictionary, country_dictionary \
                    = ({f'No funder DOI {no_funder_doi_count}': [funder["name"]]},
                       {f'No funder DOI {no_funder_doi_count}': ['NA']},
                       {f'No funder DOI {no_funder_doi_count}': ['NA']})

            nested_list_of_funders.append(detailed_funder_dictionary)
            nested_list_of_funding_body_type.append(funding_body_type_dictionary)
            nested_list_of_countries.append(country_dictionary)

            grant_dictionary = {}
            grant = funder.get("award")
            if funder_doi and grant:
                grant_dictionary[funder_doi] = [grant]
            elif funder_doi and not grant:
                grant_dictionary[funder_doi] = ['NA']
            elif not funder_doi and grant:
                grant_dictionary[f'No funder DOI {no_funder_doi_count}'] = [grant]
            else:
                grant_dictionary[f'No funder DOI {no_funder_doi_count}'] = ['NA']
            nested_list_of_grants.append(grant_dictionary)

        nested_detailed_funder_dictionary[original_work] = nested_list_of_funders
        nested_funding_body_type_dictionary[original_work] = nested_list_of_funding_body_type
        nested_countries_dictionary[original_work] = nested_list_of_countries
        nested_grant_dictionary[original_work] = nested_list_of_grants

    print(f"error: {identifier_with_error_list}")
    print(f"no funder: {identifier_with_no_funder_list}")
    print(f"bottom level funder: {bottom_level_funder_dictionary}")
    print(f"detailed name: {nested_detailed_funder_dictionary}")
    print(f"body type: {nested_funding_body_type_dictionary}")
    print(f"country: {nested_countries_dictionary}")
    print(f"grant: {nested_grant_dictionary}")

    return (identifier_with_error_list,
            identifier_with_no_funder_list,
            bottom_level_funder_dictionary,
            nested_detailed_funder_dictionary,
            nested_funding_body_type_dictionary,
            nested_countries_dictionary,
            nested_grant_dictionary)


def create_alphabet_tick_labels():
    alphabet = string.ascii_letters
    alphabet_tick_labels_list = []
    for i in range(len(alphabet)):
        alphabet_tick_labels_list.append(alphabet[i])
    for j in range(len(alphabet)):
        for k in range(len(alphabet)):
            alphabet_tick_labels_list.append(alphabet[j] + alphabet[k])
    return alphabet_tick_labels_list


def create_name_list(nested_detailed_funder_dictionary: dict):
    """
    Creates a list of detailed funder names, broad funder names, and funders with no name listed
    :param nested_detailed_funder_dictionary: nested dictionaries containing detailed funder names
    :return: detailed name list, broad name list, and list of funder DOIs with "None" for name.
    """
    detailed_name_list = []
    broad_name_list = []
    name_none_list = []
    for doi_key, response_value in nested_detailed_funder_dictionary.items():
        if response_value is None:
            name_none_list.append(doi_key)
        else:
            for nested_dictionary_item in response_value:
                for funder_doi, specific_name_list in nested_dictionary_item.items():
                    flattened_name_list = ', '.join(specific_name_list)
                    detailed_name_list.append(flattened_name_list)
                    broad_name_list.append(specific_name_list[0])

    detailed_name_list = sorted(detailed_name_list)
    broad_name_list = sorted(broad_name_list)

    return detailed_name_list, broad_name_list, name_none_list


def create_name_chart(detailed_name_list: list, broad_name_list: list, name_none_list: list):
    """
    Creates frequency chart and pie chart of broad funder names
    :param detailed_name_list: list of detailed funder names
    :param broad_name_list: list of broad funder names
    :param name_none_list: list of funder DOIs with "None" for name.
    :return: frequency chart and pie chart of funder names, sorted frequency dictionary,
    and list of funders with None for name
    """
    # detailed_name_frequency = Counter(detailed_name_list)
    # sorted_detailed_name_frequency = dict(sorted(
    #   detailed_name_frequency.items(), key=lambda x: (x[1], x[0]), reverse=True)
    # )

    broad_name_frequency = Counter(broad_name_list)
    sorted_broad_name_frequency = (sorted(broad_name_frequency.items(), key=lambda x: (x[1], x[0]), reverse=True))
    sorted_broad_name_frequency = OrderedDict(sorted_broad_name_frequency)

    label_list = []
    alphabet_list = []
    alphabet = create_alphabet_tick_labels()
    count = 0
    for key in sorted_broad_name_frequency.keys():
        label = f"{alphabet[count]} {key}"
        label_list.append(label)
        alphabet_list.append(alphabet[count])
        count += 1

    fig_width = max(6.0, len(sorted_broad_name_frequency) * 0.5)
    fig_height = fig_width

    fig1, ax1 = plt.subplots(figsize=(fig_width, fig_height), layout="tight")
    ax1.barh(list(reversed(sorted_broad_name_frequency.keys())),
             list(reversed(sorted_broad_name_frequency.values())),
             color=plt.cm.viridis(np.linspace(0, 1, len(sorted_broad_name_frequency.values()))),
             label=label_list[::-1],
             tick_label=alphabet_list[::-1]
             )
    ax1.set_title("Frequency of Funders (Broad)")
    ax1.set_ylabel("Broad Funder Name")
    ax1.set_xlabel("Frequency")
    ax1.xaxis.set_major_locator(ticker.MaxNLocator(integer=True))
    ax1.legend(reverse=True, bbox_to_anchor=(1, 1), loc="upper left", framealpha=1, fontsize='x-small')
    # ax1.tick_params(axis='x', labelrotation=45)
    ax1.bar_label(ax1.containers[0], label_type='edge', padding=0.5)
    # plt.show()

    fig2, ax2 = plt.subplots(figsize=(fig_width, fig_height), layout="tight")
    ax2.set_title("Frequency of Funders (Broad)")
    ax2.pie(sorted_broad_name_frequency.values(), labels=alphabet_list, autopct='%1.1f%%')
    plt.legend(labels=label_list, bbox_to_anchor=(1, 1), loc="upper left", fontsize='x-small')
    # plt.show()

    return fig1, fig2, sorted_broad_name_frequency, name_none_list


def create_country_list(nested_countries_dictionary: dict):
    """
    Creates a list of funder countries and funders with no country listed
    :param nested_countries_dictionary: nested dictionaries containing funder countries
    :return: detailed country list and list of funder DOIs with "None" for country.
    """
    country_list = []
    country_none_list = []
    for doi_key, response_value in nested_countries_dictionary.items():
        if response_value is None:
            country_none_list.append(doi_key)
        else:
            for nested_dictionary_item in response_value:
                for funder_doi, specific_country_list in nested_dictionary_item.items():
                    for country in specific_country_list:
                        if country == 'NA':
                            country_none_list.append(funder_doi)
                        else:
                            country_list.append(country)

    return country_list, country_none_list


def create_country_chart(country_list: list, country_none_list: list):
    """
    Creates frequency chart and pie chart of funder countries
    :param country_list: list of countries
    :param country_none_list: list of funder DOIs with "None" for country
    :return: frequency chart and pie chart of funder countries, sorted frequency dictionary,
    and list of items with type none
    """
    country_frequency = Counter(country_list)
    sorted_country_frequency = sorted(country_frequency.items(), key=lambda x: (x[1], x[0]), reverse=True)
    sorted_country_frequency = OrderedDict(sorted_country_frequency)

    label_list = []
    alphabet_list = []
    alphabet = create_alphabet_tick_labels()
    count = 0
    for key in sorted_country_frequency.keys():
        label = f"{alphabet[count]} {key}"
        label_list.append(label)
        alphabet_list.append(alphabet[count])
        count += 1

    fig_width = max(6.0, len(sorted_country_frequency) * 0.5)
    fig_height = fig_width

    fig3, ax3 = plt.subplots(figsize=(fig_width, fig_height), layout="tight")
    ax3.barh(list(reversed(sorted_country_frequency.keys())),
             list(reversed(sorted_country_frequency.values())),
             color=plt.cm.viridis(np.linspace(0, 1, len(sorted_country_frequency.values()))),
             label=label_list[::-1],
             tick_label=alphabet_list[::-1]
             )
    ax3.set_title("Funder Countries")
    plt.figtext(0.01,
                0.01,
                f'Excludes {len(country_none_list)} funders with None value '
                f'out of {len(country_none_list) + len(country_list)} total funders',
                horizontalalignment='left',
                size='x-small')
    ax3.set_ylabel("Funder Country")
    ax3.set_xlabel("Frequency")
    ax3.xaxis.set_major_locator(ticker.MaxNLocator(integer=True))
    ax3.legend(reverse=True, bbox_to_anchor=(1, 1), loc="upper left", framealpha=1, fontsize='x-small')
    # ax1.tick_params(axis='x', labelrotation=45)
    ax3.bar_label(ax3.containers[0], label_type='edge', padding=0.5)
    # plt.show()

    fig4, ax4 = plt.subplots(figsize=(fig_width, fig_height), layout="tight")
    ax4.set_title("Funder Countries")
    plt.figtext(0.01,
                0.01,
                f'Excludes {len(country_none_list)} funders with None value '
                f'out of {len(country_none_list) + len(country_list)} total funders',
                horizontalalignment='left',
                size='x-small')
    ax4.pie(sorted_country_frequency.values(), labels=alphabet_list, autopct='%1.1f%%')
    plt.legend(labels=label_list, bbox_to_anchor=(1, 1), loc="upper left")
    # plt.show()

    return fig3, fig4, sorted_country_frequency, country_none_list


def create_funding_type_list(nested_funding_body_type_dictionary: dict):
    """
    :param nested_funding_body_type_dictionary: nested dictionary of funder types
    :return: funding body type list and list of funder DOIs with "None" for funding body type
    """
    type_list = []
    type_none_list = []
    for doi_key, response_value in nested_funding_body_type_dictionary.items():
        if response_value is None:
            type_none_list.append(doi_key)
        else:
            for nested_dictionary_item in response_value:
                for funder_doi, specific_funder_type_list in nested_dictionary_item.items():
                    for funder_type in specific_funder_type_list:
                        if funder_type == 'NA':
                            type_none_list.append(funder_doi)
                        else:
                            type_list.append(funder_type)

    return type_list, type_none_list


def create_funding_type_chart(type_list: list, type_none_list: list):
    """
    Creates frequency chart and pie chart of funder types
    :param type_list: list of funding body types
    :param type_none_list: list of funder DOIs with "None" for funding body type
    :return: frequency chart and pie chart of funder types, sorted frequency dictionary,
    and list of items with type none
    """
    type_frequency = Counter(type_list)
    sorted_type_frequency = dict(sorted(type_frequency.items(), key=lambda x: (x[1], x[0]), reverse=True))
    sorted_type_frequency = OrderedDict(sorted_type_frequency)

    label_list = []
    alphabet_list = []
    alphabet = create_alphabet_tick_labels()
    count = 0
    for key in sorted_type_frequency.keys():
        label = f"{alphabet[count]} {key}"
        label_list.append(label)
        alphabet_list.append(alphabet[count])
        count += 1

    fig_width = max(6.0, len(sorted_type_frequency) * 0.5)
    fig_height = fig_width

    fig5, ax5 = plt.subplots(figsize=(fig_width, fig_height), layout="tight")
    ax5.barh(list(reversed(sorted_type_frequency.keys())),
             list(reversed(sorted_type_frequency.values())),
             color=plt.cm.viridis(np.linspace(0, 1, len(sorted_type_frequency.values()))),
             label=label_list[::-1],
             tick_label=alphabet_list[::-1]
             )
    ax5.set_title("Types of Funding Bodies")
    plt.figtext(0.01,
                0.01,
                f'Excludes {len(type_none_list)} funders with None value '
                f'out of {len(type_none_list) + len(type_list)} total funders',
                horizontalalignment='left',
                size='x-small')
    ax5.set_ylabel("Funder Type")
    ax5.set_xlabel("Frequency")
    ax5.xaxis.set_major_locator(ticker.MaxNLocator(integer=True))
    ax5.legend(reverse=True, bbox_to_anchor=(1, 1), loc="upper left", framealpha=1, fontsize='x-small')
    # ax1.tick_params(axis='x', labelrotation=45)
    ax5.bar_label(ax5.containers[0], label_type='edge', padding=0.5)
    # plt.show()

    fig6, ax6 = plt.subplots(figsize=(fig_width, fig_height), layout="tight")
    ax6.set_title("Types of Funding Bodies")
    plt.figtext(0.01,
                0.01,
                f'Excludes {len(type_none_list)} funders with None value '
                f'out of {len(type_none_list) + len(type_list)} total funders',
                horizontalalignment='left',
                size='x-small')
    ax6.pie(sorted_type_frequency.values(), labels=alphabet_list, autopct='%1.1f%%')
    plt.legend(labels=label_list, bbox_to_anchor=(1, 1), loc="upper left",)
    # plt.show()

    return fig5, fig6, sorted_type_frequency, type_none_list


def crossref_create_item_to_funder_table(nested_detailed_funder_dictionary: dict,
                                nested_funding_body_type_dictionary: dict,
                                nested_countries_dictionary: dict,
                                nested_grant_dictionary: dict):
    """

    :param nested_detailed_funder_dictionary:
    :param nested_funding_body_type_dictionary:
    :param nested_countries_dictionary:
    :param nested_grant_dictionary:
    :return:
    """
    data = {'Funder name': nested_detailed_funder_dictionary,
            'Funding body type': nested_funding_body_type_dictionary,
            'Country': nested_countries_dictionary,
            'Grant': nested_grant_dictionary
            }

    # Flatten the nested dictionary and create a DataFrame
    df = pd.DataFrame.from_dict({(level1, level2, level3, np.random.randint(low=0, high=5000)): value
                                 for level1, level2_dict in data.items()
                                 for level2, level3_dict_list in level2_dict.items()
                                 for level3_dict_item in level3_dict_list
                                 for level3, value in level3_dict_item.items()}, orient='index')

    # Set MultiIndex
    df.index = pd.MultiIndex.from_tuples(df.index)

    # Combine names list across multiple columns into one column
    df['values'] = df.agg(lambda x: ', '.join(x.dropna().astype(str)), axis=1)
    # Drop multiple unneeded columns
    df = df['values']

    # Reset index to flatten indexing levels and rename to legible column names
    df = df.reset_index()
    df.rename(columns={'level_0': 'Available funder information',
                       'level_1': 'Original work identifier',
                       'level_2': 'Funder identifier',
                       'level_3': 'Arbitrary value to prevent overwriting duplicates'}, inplace=True)

    df = pd.pivot(df,
                  index=['Original work identifier',
                         'Funder identifier',
                         'Arbitrary value to prevent overwriting duplicates'],
                  columns='Available funder information',
                  values='values')

    # Reset index again to address duplicate funder DOIs/combine grant information
    df = df.reset_index()

    # Use transform to combine info for duplicated funder DOIs
    df = df.groupby(['Original work identifier', 'Funder identifier'], dropna=True, as_index=True)[[
        'Original work identifier', 'Funder identifier', 'Funder name', 'Grant', 'Funding body type', 'Country'
    ]].transform(lambda x: ', '.join(x.dropna().astype(str))).drop_duplicates()

    # Leave only grant column with additional information
    columns_with_duplicated_info = ['Original work identifier',
                                    'Funder identifier',
                                    'Funding body type',
                                    'Country']
    for column in columns_with_duplicated_info:
        df[column] = df[column].apply(lambda x: x.split(',')[0])

    # reset multiindex
    df.set_index(['Original work identifier', 'Funder identifier'], inplace=True)

    # Display the resulting DataFrame
    # print(df)

    return df


def crossref_create_funder_to_item_table(nested_detailed_funder_dictionary: dict,
                                nested_funding_body_type_dictionary: dict,
                                nested_countries_dictionary: dict,
                                nested_grant_dictionary: dict):
    """

    :param nested_detailed_funder_dictionary:
    :param nested_funding_body_type_dictionary:
    :param nested_countries_dictionary:
    :param nested_grant_dictionary:
    :return:
    """
    data = {'Funder name': nested_detailed_funder_dictionary,
            'Funding body type': nested_funding_body_type_dictionary,
            'Country': nested_countries_dictionary,
            'Grant': nested_grant_dictionary
            }

    # Flatten the nested dictionary and create a DataFrame
    df = pd.DataFrame.from_dict({(level1, level2, level3, np.random.randint(low=0, high=5000)): value
                                 for level1, level2_dict in data.items()
                                 for level2, level3_dict_list in level2_dict.items()
                                 for level3_dict_item in level3_dict_list
                                 for level3, value in level3_dict_item.items()}, orient='index')

    # Set MultiIndex
    df.index = pd.MultiIndex.from_tuples(df.index)

    # Flatten names list across multiple columns into one column
    df['values'] = df.agg(lambda x: ', '.join(x.dropna().astype(str)), axis=1)
    df = df['values']

    # Reset index to flatten indexing levels and rename to legible column names
    df = df.reset_index()

    df.rename(columns={'level_0': 'Available funder information',
                       'level_1': 'Original work identifier',
                       'level_2': 'Funder identifier',
                       'level_3': 'Arbitrary value to prevent overwriting duplicates'}, inplace=True)

    # Pivot to bring available funder information into columns
    df = pd.pivot(df,
                  index=['Funder identifier',
                         'Original work identifier',
                         'Arbitrary value to prevent overwriting duplicates'],
                  columns=['Available funder information'],
                  values='values')

    # Reset index again to address duplicate funder DOIs/combine grant information
    df = df.reset_index()

    # Use transform to combine info for duplicated funder DOIs
    df = df.groupby(['Funder identifier', 'Original work identifier'], dropna=True, as_index=True)[[
        'Original work identifier', 'Funder identifier', 'Funder name', 'Grant', 'Funding body type', 'Country'
    ]].transform(lambda x: ', '.join(x.dropna().astype(str))).drop_duplicates()

    # Leave only grant column with additional information
    columns_with_duplicated_info = ['Original work identifier',
                                    'Funder identifier',
                                    'Funding body type',
                                    'Country']
    for column in columns_with_duplicated_info:
        df[column] = df[column].apply(lambda x: x.split(',')[0])

    # Add overall funder name and rename specific funder name column
    df["Overall funder name"] = df['Funder name'].str.split(',').str[0].str.strip()
    df.rename(columns={'Funder name': 'Specific funder name'}, inplace=True)

    # Add overall funder name to indexing
    df = df.reset_index()
    df.set_index(['Overall funder name', 'Funder identifier', 'Original work identifier'], inplace=True)
    df.sort_index(inplace=True)
    df.drop('index', axis=1, inplace=True)

    # Display the resulting DataFrame
    # print(df)

    # Create summary table of counts
    summary_df = df.groupby(level=[0, 2]).size().to_frame(name="Count of times funder is listed for a work")
    # print(summary_df)

    return df, summary_df


def main():
    # (identifier_with_error_list,
    #  identifier_with_no_funder_list,
    #  bottom_level_funder_dictionary,
    #  nested_detailed_funder_dictionary,
    #  nested_funding_body_type_dictionary,
    #  nested_countries_dictionary,
    #  nested_grant_dictionary) = query_crossref(['10.7554/ELIFE.65902'])

    (identifier_with_error_list,
     identifier_with_no_funder_list,
     bottom_level_funder_dictionary,
     nested_detailed_funder_dictionary,
     nested_funding_body_type_dictionary,
     nested_countries_dictionary,
     nested_grant_dictionary) = query_crossref(crossref_clean_input_list(crossref_read_input_file("data/COVID-WFI-example.txt")))

    detailed_name_list, broad_name_list, name_none_list = create_name_list(nested_detailed_funder_dictionary)
    country_list, country_none_list = create_country_list(nested_countries_dictionary)
    type_list, type_none_list = create_funding_type_list(nested_funding_body_type_dictionary)

    fig1, fig2, sorted_broad_name_frequency, name_none_list = create_name_chart(detailed_name_list,
                                                                                broad_name_list,
                                                                                name_none_list)

    fig3, fig4, sorted_country_frequency, country_none_list = create_country_chart(country_list,
                                                                                   country_none_list)

    fig5, fig6, sorted_type_frequency, type_none_list = create_funding_type_chart(type_list,
                                                                                  type_none_list)

    fig1.show()
    fig2.show()
    fig3.show()
    fig4.show()
    fig5.show()
    fig6.show()

    df = crossref_create_item_to_funder_table(nested_detailed_funder_dictionary,
                                     nested_funding_body_type_dictionary,
                                     nested_countries_dictionary,
                                     nested_grant_dictionary)

    df2 = crossref_create_funder_to_item_table(nested_detailed_funder_dictionary,
                                      nested_funding_body_type_dictionary,
                                      nested_countries_dictionary,
                                      nested_grant_dictionary)


if __name__ == "__main__":
    main()
