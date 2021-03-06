print(__doc__)

import matplotlib.pyplot as plot
from sklearn.svm import SVC
from sklearn.model_selection import StratifiedKFold
from sklearn.feature_selection import RFECV
from sklearn.datasets import make_classification

from nalaf.learning.lib.sklsvm import SklSVM
from nalaf.structures.data import Dataset
from loctext.learning.train import read_corpus
from loctext.util import PRO_ID, LOC_ID, ORG_ID, REL_PRO_LOC_ID, repo_path
from loctext.learning.annotators import LocTextDXModelRelationExtractor
from util import *
from loctext.util import *
import time

SCORING_NAMES = [
    'f1'
]

def call(annotator, X, y, groups, pre_selected_feature_keys=None):

    if pre_selected_feature_keys is not None:
        my_transformer = select_features_transformer(pre_selected_feature_keys)
        X = my_transformer.fit_transform(X)

    num_instances = len(y)

    for scoring_name in SCORING_NAMES:

        rfecv = RFECV(
            verbose=1,
            n_jobs=-1,
            estimator=annotator.model.model,
            step=1,
            cv=my_cv_generator(groups, num_instances),
            scoring=scoring_name
        )

        start = time.time()
        rfecv.fit(X, y)
        end = time.time()

        print("rfe", "Time for feature selection: ", (end - start))
        print("rfe", "Optimal number of features : {}".format(rfecv.n_features_))

        selected_feature_keys = [index for (index, value) in enumerate(rfecv.support_) if value]

        print()
        print()
        print("rfe", "Max performance for {}: {}".format(scoring_name, rfecv.grid_scores_[rfecv.n_features_ - 1]))
        print()
        print()

        names, fig_file = \
            print_selected_features(selected_feature_keys, annotator.pipeline.feature_set, file_prefix="rfe")

        print()
        print("\n".join([names, fig_file]))
        print()

        plot_recursive_features(scoring_name, rfecv.grid_scores_, save_to=fig_file, show=False)


if __name__ == "__main__":
    import sys

    annotator, X, y, groups = get_model_and_data()
    call(annotator, X, y, groups, pre_selected_feature_keys=None)
