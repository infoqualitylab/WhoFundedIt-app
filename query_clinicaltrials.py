import string
import time
import requests
import re
import numpy as np
import pandas as pd
from collections import Counter, OrderedDict
from matplotlib import pyplot as plt, ticker

def clinicaltrials_read_input_file(filename: str):
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


def clinicaltrials_clean_input_list(input_list: list):
    """
    Cleans common errors in input list to get NCTIDs in format "NCT########" or "nct########",
    removing duplicates.

    :param input_list: list of NCTIDs
    :return: cleaned list of NCTIDs
    """
    cleaned_input_list = []
    for item in input_list:
        if item == '':
            continue
        elif re.search(r'^[Nn][Cc][Tt]0*[1-9]\d{0,7}$', item):
            search_item = item
        elif re.search(r'^NCTID: ', item):
            new_item = re.sub(r'NCTID: ', '', item, 1)
            search_item = new_item
        else:
            search_item = item
        cleaned_input_list.append(search_item.strip())
        cleaned_input_list = list(set(cleaned_input_list))
    return cleaned_input_list


def query_clinicaltrials(cleaned_input_list: list):
    """
    Queries ClinicalTrials.gov for funders of items with specific NCTIDs. See ClinicalTrials.gov documentation for more
    details: https://clinicaltrials.gov/data-api/api

    :param cleaned_input_list: input list of NCTIDs in format "NCT########" or "nct########"
    :return: list of dictionaries with attributes from returned queries in ClinicalTrials.gov
    """
    identifier_with_error_list = []
    identifier_with_no_funder_list = []

    bottom_level_funder_dictionary = {}
    lead_sponsor_dictionary = {}
    lead_sponsor_class_dictionary = {}
    all_collaborators_dictionary = {}
    collaborator_class_dictionary = {}

    for identifier in cleaned_input_list:
        try:
            work_url = f'https://clinicaltrials.gov/api/v2/studies/{identifier}'
            response = requests.get(work_url)
            result = response.json()
            protocol_section = result['protocolSection']

            if "sponsorCollaboratorsModule" in protocol_section:
                bottom_level_funder_dictionary[identifier] = protocol_section['sponsorCollaboratorsModule']
            else:
                identifier_with_no_funder_list.append(identifier)
            time.sleep(0.02)  # Could not find a given request limit on ClinicalTrials.gov.

        except Exception:
            identifier_with_error_list.append(identifier)
            continue

        for original_work, sponsor_and_collaborator_info in bottom_level_funder_dictionary.items():
            lead_sponsor = sponsor_and_collaborator_info['leadSponsor']['name']
            lead_sponsor_class = sponsor_and_collaborator_info['leadSponsor']['class']
            lead_sponsor_dictionary[identifier] = lead_sponsor
            lead_sponsor_class_dictionary[identifier] = lead_sponsor_class

            if 'collaborators' in sponsor_and_collaborator_info:
                collaborator_list_of_dictionaries = sponsor_and_collaborator_info['collaborators']
                collaborator_temp_list = []
                collaborator_class_temp_list = []
                for item in collaborator_list_of_dictionaries:
                    collaborator = item['name']
                    collaborator_temp_list.append(collaborator)

                    collaborator_class = item['class']
                    collaborator_class_temp_list.append(collaborator_class)

                all_collaborators_dictionary[identifier] = collaborator_temp_list
                collaborator_class_dictionary[identifier] = collaborator_class_temp_list
            else:
                all_collaborators_dictionary[identifier] = ['NA']
                collaborator_class_dictionary[identifier] = ['NA']


    print(f"error: {identifier_with_error_list}")
    print(f"no funder: {identifier_with_no_funder_list}")
    print(f"bottom level funder: {bottom_level_funder_dictionary}")
    print(f"lead sponsor: {lead_sponsor_dictionary}")
    print(f"lead sponsor class: {lead_sponsor_class_dictionary}")
    print(f"all collaborators: {all_collaborators_dictionary}")
    print(f"collaborator class: {collaborator_class_dictionary}")

    return (identifier_with_error_list,
            identifier_with_no_funder_list,
            bottom_level_funder_dictionary,
            lead_sponsor_dictionary,
            lead_sponsor_class_dictionary,
            all_collaborators_dictionary,
            collaborator_class_dictionary)


def create_alphabet_tick_labels():
    alphabet = string.ascii_letters
    alphabet_tick_labels_list = []
    for i in range(len(alphabet)):
        alphabet_tick_labels_list.append(alphabet[i])
    for j in range(len(alphabet)):
        for k in range(len(alphabet)):
            alphabet_tick_labels_list.append(alphabet[j] + alphabet[k])
    return alphabet_tick_labels_list


def create_aggregated_list(field_dictionary):
    """
    Creates a list by unpacking a dictionary for a given field (e.g. lead sponsor name).
    :param field_dictionary: dictionary containing original work idenifier keys and
    :return: list of desired field values
    """
    field_list = []
    for nctid_key, response_value in field_dictionary.items():
        if isinstance(response_value, list):
            field_list.extend(response_value)
        elif isinstance(response_value, str):
            field_list.append(response_value)

    return field_list


def clinicaltrials_create_name_chart(lead_sponsor_dictionary: dict):
    """
    Creates frequency chart and pie chart of lead sponsor names
    :param lead_sponsor_dictionary: dictionary containing original work identifier keys and list of lead sponsor names
    :return: frequency chart and pie chart of lead sponsor names and sorted frequency dictionary
    """
    lead_sponsor_list = create_aggregated_list(lead_sponsor_dictionary)
    lead_sponsor_frequency = Counter(lead_sponsor_list)
    sorted_lead_sponsor_frequency = (sorted(lead_sponsor_frequency.items(), key=lambda x: (x[1], x[0]), reverse=True))
    sorted_lead_sponsor_frequency = OrderedDict(sorted_lead_sponsor_frequency)

    label_list = []
    alphabet_list = []
    alphabet = create_alphabet_tick_labels()
    count = 0
    for key in sorted_lead_sponsor_frequency.keys():
        label = f"{alphabet[count]} {key}"
        label_list.append(label)
        alphabet_list.append(alphabet[count])
        count += 1

    fig_width = max(6.0, len(sorted_lead_sponsor_frequency) * 0.5)
    fig_height = fig_width

    fig1, ax1 = plt.subplots(figsize=(fig_width, fig_height), layout="tight")
    ax1.barh(list(reversed(sorted_lead_sponsor_frequency.keys())),
             list(reversed(sorted_lead_sponsor_frequency.values())),
             color=plt.cm.viridis(np.linspace(0, 1, len(sorted_lead_sponsor_frequency.values()))),
             label=label_list[::-1],
             tick_label=alphabet_list[::-1]
             )
    ax1.set_title("Frequency of Lead Sponsors")
    ax1.set_ylabel("Lead Sponsor Name")
    ax1.set_xlabel("Frequency")
    ax1.xaxis.set_major_locator(ticker.MaxNLocator(integer=True))
    ax1.legend(reverse=True, bbox_to_anchor=(1, 1), loc="upper left", framealpha=1, fontsize='x-small')
    # ax1.tick_params(axis='x', labelrotation=45)
    ax1.bar_label(ax1.containers[0], label_type='edge', padding=0.5)
    # plt.show()

    fig2, ax2 = plt.subplots(figsize=(fig_width, fig_height), layout="tight")
    ax2.set_title("Frequency of Lead Sponsors")
    ax2.pie(sorted_lead_sponsor_frequency.values(), labels=alphabet_list, autopct='%1.1f%%')
    plt.legend(labels=label_list, bbox_to_anchor=(1, 1), loc="upper left", fontsize='x-small')
    # plt.show()

    return fig1, fig2, sorted_lead_sponsor_frequency


def create_lead_sponsor_class_chart(lead_sponsor_class_dictionary: dict):
    """
    Creates frequency chart and pie chart of lead sponsor classes
    :param lead_sponsor_class_dictionary: dictionary containing original work identifier keys and list of lead sponsor classes
    :return: frequency chart and pie chart of lead sponsor classes and sorted frequency dictionary
    """
    lead_sponsor_class_list = create_aggregated_list(lead_sponsor_class_dictionary)
    lead_sponsor_class_frequency = Counter(lead_sponsor_class_list)
    sorted_lead_sponsor_class_frequency = (sorted(lead_sponsor_class_frequency.items(), key=lambda x: (x[1], x[0]), reverse=True))
    sorted_lead_sponsor_class_frequency = OrderedDict(sorted_lead_sponsor_class_frequency)

    label_list = []
    alphabet_list = []
    alphabet = create_alphabet_tick_labels()
    count = 0
    for key in sorted_lead_sponsor_class_frequency.keys():
        label = f"{alphabet[count]} {key}"
        label_list.append(label)
        alphabet_list.append(alphabet[count])
        count += 1

    fig_width = max(6.0, len(sorted_lead_sponsor_class_frequency) * 0.5)
    fig_height = fig_width

    (fig3, ax3) = plt.subplots(figsize=(fig_width, fig_height), layout="tight")
    ax3.barh(list(reversed(sorted_lead_sponsor_class_frequency.keys())),
             list(reversed(sorted_lead_sponsor_class_frequency.values())),
             color=plt.cm.viridis(np.linspace(0, 1, len(sorted_lead_sponsor_class_frequency.values()))),
             label=label_list[::-1],
             tick_label=alphabet_list[::-1]
             )
    ax3.set_title("Frequency of Lead Sponsor Classes")
    ax3.set_ylabel("Lead Sponsor Class")
    ax3.set_xlabel("Frequency")
    ax3.xaxis.set_major_locator(ticker.MaxNLocator(integer=True))
    ax3.legend(reverse=True, bbox_to_anchor=(1, 1), loc="upper left", framealpha=1, fontsize='x-small')
    # ax1.tick_params(axis='x', labelrotation=45)
    ax3.bar_label(ax3.containers[0], label_type='edge', padding=0.5)
    # plt.show()

    fig4, ax4 = plt.subplots(figsize=(fig_width, fig_height), layout="tight")
    ax4.set_title("Frequency of Lead Sponsor Classes")
    ax4.pie(sorted_lead_sponsor_class_frequency.values(), labels=alphabet_list, autopct='%1.1f%%')
    plt.legend(labels=label_list, bbox_to_anchor=(1, 1), loc="upper left", fontsize='x-small')
    # plt.show()

    return fig3, fig4, sorted_lead_sponsor_class_frequency


def clinicaltrials_create_item_to_funder_table(lead_sponsor_dictionary: dict, lead_sponsor_class_dictionary: dict):
    """

    :param lead_sponsor_dictionary:
    :param lead_sponsor_class_dictionary:
    :return:
    """
    data = {'Lead sponsor name': lead_sponsor_dictionary,
            'Lead sponsor class': lead_sponsor_class_dictionary}

    # Flatten the nested dictionary and create a DataFrame
    df = pd.DataFrame.from_dict({(level1, level2): value
                                for level1, level2_dict in data.items()
                                for level2, value in level2_dict.items()}, orient='index')
    print(df)

    # Set MultiIndex
    df.index = pd.MultiIndex.from_tuples(df.index)

    # Reset index to flatten indexing levels and rename to legible column names
    df = df.reset_index()

    df.rename(columns={'level_0': 'Available sponsor information',
                       'level_1': 'Original work identifier',
                       0: 'values'}, inplace=True)

    # Pivot to bring available funder information into columns
    df = pd.pivot(df,
                  index='Original work identifier',
                  columns='Available sponsor information',
                  values='values'
                  )

    df = df.iloc[:, [1, 0]]

    return df


def main():
    (identifier_with_error_list,
     identifier_with_no_funder_list,
     bottom_level_funder_dictionary,
     lead_sponsor_dictionary,
     lead_sponsor_class_dictionary,
     all_collaborators_dictionary,
     collaborator_class_dictionary) = query_clinicaltrials(['NCT05392712', 'NCT05060562'])

    fig1, fig2, sorted_lead_sponsor_frequency = clinicaltrials_create_name_chart(lead_sponsor_dictionary)

    fig3, fig4, sorted_lead_sponsor_class_frequency = create_lead_sponsor_class_chart(lead_sponsor_class_dictionary)

    fig1.show()
    fig2.show()
    fig3.show()
    fig4.show()

    df = clinicaltrials_create_item_to_funder_table(lead_sponsor_dictionary, lead_sponsor_class_dictionary)


if __name__ == "__main__":
    main()

