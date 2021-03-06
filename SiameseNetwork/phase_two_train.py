import pandas as pd
import random

'''
Phase 2 adding Negative Examples from methods of name representation as vectors
'''


def negative(originals, index):
    """
    Create random negative example for the original name at 'index'
    """
    neg = "None"
    # Each name might be in the dataset 10 times in a row (at most)
    if index <= 9:
        neg = originals[random.randint(10, len(originals) - 1)]
    elif index >= len(originals) - 10:
        neg = originals[random.randint(0, len(originals) - 10)]
    else:
        above = originals[random.randint(0, index - 10)]
        below = originals[random.randint(index + 10, len(originals) - 1)]
        neg = random.choice([above, below])
    return neg


def second_phase_negative_examples(short_file_path, dataset, filtered_df):
    """
    The method reads the vector representation csv files and creates a df of the names the
    algorithms' received distance was large as negative examples
    """
    # The three methods to represent the names as vectors
    turicreate_df = pd.read_csv(short_file_path + dataset)
    turicreate_df['Method'] = 'turicreate'
    wav2vec_df = pd.read_csv(short_file_path + "knn_suggestions_according_sound_pandas_imp_wav2vec.csv")
    wav2vec_df['Method'] = 'wav2vec'
    pyAudioAnalysis_df = pd.read_csv(short_file_path + "knn_suggestions_according_sound_pandas_imp_pyAudioAnalysis.csv")
    pyAudioAnalysis_df['Method'] = 'pyAudioAnalysis'
    # add negative examples from vector representation methods
    # turicreate mistakes have larger distance from other methods
    turicreate_df = turicreate_df[turicreate_df['Distance'] >= 4]
    dfs = [turicreate_df, wav2vec_df, pyAudioAnalysis_df]
    methods_df = pd.concat(dfs)
    methods_df = methods_df[methods_df['Distance'] >= 1]
    methods_df = methods_df.rename(columns={'Candidate': 'Negative'})
    filtered_df = filtered_df.rename(columns={'Candidate': 'Positive',
                                              'Distance': 'Distance_Spoken_Name',
                                              'Edit_Distance': 'Edit_Distance_Spoken_Name'})
    # merge the vector representation df with the filtered df
    sn_gt_df = pd.merge(methods_df, filtered_df, how="inner", left_on='Original', right_on='Original')
    # trim the df
    triplets_df = sn_gt_df[['Original', 'Positive', 'Negative']]
    # Drop duplicate (original + positive) pairs
    unique_df = triplets_df.drop_duplicates(subset=['Original', 'Positive'])
    return unique_df


def add_random_negatives_phase_two(unique_df):
    """
    The function creates triplets of data and adds easy negative examples
    """
    originals = unique_df['Original'].tolist()
    positives = unique_df['Positive'].tolist()
    negatives = unique_df['Negative'].tolist()
    trios = []
    for i, org in enumerate(originals):
        trios += [[org, positives[i], negatives[i]]]
        random_negative = negative(originals, i)
        trios += [[originals[i], positives[i], random_negative]]

    random.shuffle(trios)
    return trios


def train_test_split_phase_two(train_data, test_data, trios):
    """
    The function splits the phase two data into train and test
    """
    l = int(0.66 * len(trios))
    train_data += trios[:l]
    test_data += trios[l:]
    return train_data, test_data
