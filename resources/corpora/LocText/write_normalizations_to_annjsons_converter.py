import json
import os
import csv

from loctext.util import PRO_ID, LOC_ID, ORG_ID, REL_PRO_LOC_ID, UNIPROT_NORM_ID, GO_NORM_ID, TAXONOMY_NORM_ID, repo_path


#
# The script currently converts from the .tsv (prepared by Tanya), not from the PubAnnotation annotations as we found errors in those
#
# See: https://github.com/juanmirocks/LocText/issues/2
#


locText_json_files_path = './LocText_anndoc_original_without_normalizations/LocText_master_json/pool'
pubMed_tsv_file_path = './interFile_modified_by_Tanya.tsv'
output_json_files_path = './LocText_annjson_with_normalizations_latest_5_feb_2017'

"""
Finds the annotated file and uses the information in interFile_modified.tsv file and
fills in the normalizations (UniProt, GO, Taxonomy ID) values into the LocText _annjson_ json file.

Example of how normalizations should look like in annjson format:

normalizations: {
    "n_7":{
        "source":{
            "name":"UniProt",
            "id":"P34972",
            "url":null
        },
        "recName":null,
        "confidence":{
            "state":"",
            "who":[
              "ml:dpeker"
            ],
            "prob":0.8458
        }
    }
}
"""

# Fetch each file one by one from "LocText_anndoc_original_without_normalizations" folder
for file_name in os.listdir(locText_json_files_path):
    with open(locText_json_files_path + "/" + file_name) as locText_data_file:
        start = file_name.find("-") + 1
        end = file_name.find(".ann.json")
        pubMed_id = file_name[start:end]
        counter = 0

        # Check if PubMedID is digit or not.
        if pubMed_id.isdigit():
            with open(pubMed_tsv_file_path) as tsv_file:
                tsv_data = csv.reader(tsv_file, delimiter="\t")
                locText_data = json.load(locText_data_file)
                segregated_rows = []

                # Extract only the required rows based on current PubMedID
                for row in tsv_data:
                    if row[0] == pubMed_id:
                        segregated_rows.append(row)

                # For each entity, add corresponding normalization information from segregated row
                for entity in locText_data['entities']:
                    original_ent_text = entity['offsets'][0]['text']
                    original_start_offset = entity['offsets'][0]['start']

                    for row in segregated_rows:
                        pubMed_id, ent_text, ent_type, norm_text, part_name, start_offset, end_offset = row
                        start_offset = int(start_offset)
                        end_offset = int(end_offset)

                        if str(ent_text) == str(original_ent_text) and str(start_offset) == str(original_start_offset):
                            assert((end_offset - start_offset) == len(original_ent_text) == len(ent_text))

                            obj_type = ""
                            obj_id = ""
                            confidence = entity['confidence']
                            obj = {}

                            if row[2] == "Protein":
                                # If UniProt ID is "Protein", then add empty string instead of text "Protein"
                                if row[3] == "Protein":
                                    obj_id = None
                                else:
                                    # Remove unnecessary spaces between ID's
                                    obj_id = row[3].replace(" ", "")
                                obj_type = UNIPROT_NORM_ID
                                name = "UniProtKB"

                            elif row[2] == "Location":
                                # For GO ID's, try to extract only the GO ID. Strip rest of the content
                                obj_id = row[3]
                                assert obj_id.count("GO:") == 1, obj_id
                                obj_id_splitted = obj_id.split(" ")
                                # assert len(obj_id_splitted) <= 2, pubMed_id + " -- " + obj_id
                                obj_id = obj_id_splitted[0]
                                assert obj_id != "", pubMed_id + " -- " + original + " --- line: " + '\t'.join(row)

                                obj_type = GO_NORM_ID
                                name = "GO"

                            elif row[2] == "Organism":
                                # Remove unnecessary spaces between ID's
                                obj_id = row[3].replace(" ", "")
                                obj_type = TAXONOMY_NORM_ID
                                name = "Taxonomy"

                            normalization_obj = {
                                obj_type: {"source": {"name": name, "id": obj_id, "url": None}, "recName": None,
                                           "confidence": confidence}}
                            entity['normalizations'] = normalization_obj

                with open(output_json_files_path + "/" + file_name, "w") as output_file:
                    json.dump(locText_data, output_file)

        else:
            print("File without pubMed file: " + file_name)
