from loctext.learning.annotators import StringTagger
from loctext.learning.train import read_corpus
from loctext.util import PRO_ID, LOC_ID, ORG_ID, UNIPROT_NORM_ID, GO_NORM_ID, TAXONOMY_NORM_ID


TAGGER_SEND_PARTS = StringTagger(PRO_ID, LOC_ID, ORG_ID, UNIPROT_NORM_ID, GO_NORM_ID, TAXONOMY_NORM_ID, send_whole_once=False, tagger_entity_types="-22,-3,9606,3702,4932,10090,4896,511145,6239,7227,7955")
TAGGER_SEND_WHOLE = StringTagger(PRO_ID, LOC_ID, ORG_ID, UNIPROT_NORM_ID, GO_NORM_ID, TAXONOMY_NORM_ID, send_whole_once=True, tagger_entity_types="-22,-3,9606,3702,4932,10090,4896,511145,6239,7227,7955")
TAGGER_SEND_EGAL = TAGGER_SEND_PARTS


run_tests = TAGGER_SEND_PARTS.is_server_running("http://localhost:5000/")


# get the number of annotated entities in a dataset
def num_predicted_entities(corpus):
    return len(list(corpus.predicted_entities()))


# test if number of annotations of parts is less than or equal to the number of annotations of the whole content
def test_number_of_tagged_entities():
    if run_tests:
        dataset_parts = read_corpus("LocText", corpus_percentage=1.0)
        dataset_whole = read_corpus("LocText", corpus_percentage=1.0)
        assert 0 == num_predicted_entities(dataset_parts) == num_predicted_entities(dataset_whole)

        TAGGER_SEND_PARTS.annotate(dataset_parts)
        TAGGER_SEND_WHOLE.annotate(dataset_whole)

        for docid, document in dataset_parts.documents.items():
            if docid in [
                "23543752",  # Special analysis as it contains unicode chracters (μ)
                "23150645"  # also unicode and annotation of reductase where reductase as string alone is not tagged
            ]:
                for e in document.predicted_entities():
                    print(e)
                print()

        num_preds_with_parts = num_predicted_entities(dataset_parts)
        num_preds_with_whole = num_predicted_entities(dataset_whole)

        print("Numbers, real:", len(list(dataset_parts.entities())), "vs. pred: ", num_preds_with_parts, num_preds_with_whole)

        # Equality holds if all tagger entity types are explicitly given, otherwise the tagging with parts yield less predicted entities
        assert num_preds_with_parts == num_preds_with_whole

        for pred_part, pred_whole in zip(dataset_parts.predicted_entities(), dataset_whole.predicted_entities()):
            assert(pred_part == pred_whole)


def test_basic_json_responses():
    if run_tests:

        assert TAGGER_SEND_EGAL.get_string_tagger_json_response("simple text") == []
        assert TAGGER_SEND_EGAL.get_string_tagger_json_response("p53") != []
