# First visualizations with Data

#%matplotlib inline
from matplotlib.colors import ListedColormap, BoundaryNorm
from sklearn.cluster import KMeans
import copy as copy
import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd
import random as rm
import click


def get_threading_matrix(threading):

    num_columns = len(np.unique(threading))
    num_rows = len(threading)
    threading_matrix = np.zeros((num_rows, num_columns))

    for idx, val in enumerate(threading):
        column = val - 1
        row = idx
        threading_matrix[row, column] = 1

    return threading_matrix


def get_treadling_matrix(treadling):

    num_columns = len(treadling)
    num_rows = len(np.unique(treadling))
    treadling_matrix = np.zeros((num_rows, num_columns))

    for idx, val in enumerate(treadling):
        column = idx
        row = val - 1
        treadling_matrix[row, column] = 1

    return treadling_matrix


def get_draft(treadling, threading, tieup):
    # create draft
    treadling_len = len(treadling)
    threading_len = len(threading)
    matrix = np.zeros((treadling_len, threading_len))

    for i in range(treadling_len):
        y_th = treadling[i % treadling_len]
        for j in range(threading_len):
            x_th = threading[j % threading_len]
            #         print("i", i+1, "j", j+1, "x_th", x_th, "y_th", y_th, "treadling.length", treadling_len, "threading.length", threading_len)

            # choose color
            if tieup[x_th - 1][y_th - 1] == 1:
                matrix[i, j] = 1
    #             print("i", i+1, "j", j+1, "x_th", x_th, "y_th", y_th, "treadling.length", treadling_len, "threading.length", threading_len)

    return matrix


def load_data(filename):

    df = pd.read_csv(filename)

    return df


def sample_data(df, sample_size=1000, random_seed=10):

    rm.seed(random_seed)
    nrows = df.shape[0]
    sample = rm.sample(range(nrows), sample_size)
    df_sample = copy.deepcopy(df.iloc[sample])

    return df_sample


def extract_data_from_df(df):

    df = df.drop(["x", "y"], axis=1)
    X = df.to_numpy()

    return X


def normalize_matrix(X):

    X = X - X.mean(axis=0)
    X = X / X.std(axis=0)

    return X


def get_clusters(X, n_clusters, random_state):

    kmeans = KMeans(n_clusters=n_clusters, random_state=random_state).fit(X)
    labels = kmeans.labels_
    labels = labels + 1

    return labels


def save_matrix_as_csv(
    filename, matrix, type=int, delimiter=",", newline="\n", fmt="%i"
):

    np.savetxt(
        filename, matrix.astype(type), delimiter=delimiter, newline=newline, fmt=fmt
    )


def save_matrices_as_csv(
    subdir_output, threading_matrix, tieup, treadling_matrix, draft_matrix
):

    filename_threading = os.path.join(subdir_output, "threading" + ".csv")
    filename_tieup = os.path.join(subdir_output, "tieup" + ".csv")
    filename_treadling = os.path.join(subdir_output, "treadling" + ".csv")
    filename_draft = os.path.join(subdir_output, "draft" + ".csv")

    save_matrix_as_csv(filename_threading, threading_matrix)
    save_matrix_as_csv(filename_tieup, tieup)
    save_matrix_as_csv(filename_treadling, treadling_matrix)
    save_matrix_as_csv(filename_draft, draft_matrix)


@click.command()
@click.option("--filename", default="../data/20210108_tejidos_testdata2.csv", show_default=True)
@click.option("--dir_output", default="../generated_textile_matrices", show_default=True)
@click.option("--n_clusters", default=20, show_default=True)
@click.option("--sample_size", default=1000, show_default=True)
@click.option("--random_seed", default=10, show_default=True)
@click.option("--random_state", default=0, show_default=True)
def generate_textile_matrices_from_data(
    filename,
    dir_output,
    n_clusters,
    sample_size,
    random_seed,
    random_state,
):
    # def generate_textile_matrices_from_data(
    #     filename="../data/20210108_tejidos_testdata2.csv",
    #     dir_output="2021-01-11",
    #     n_clusters=20,
    #     sample_size=1000,
    #     random_seed=10,
    #     random_state=0,
    # ):

    if not os.path.exists(dir_output):
        os.mkdir(dir_output)

    subdir_output = os.path.join(dir_output, "n_clusters=" + str(n_clusters))
    if not os.path.exists(subdir_output):
        os.mkdir(subdir_output)

    df = load_data(filename)
    df = sample_data(df, sample_size=sample_size, random_seed=random_seed)
    X = extract_data_from_df(df)
    X = normalize_matrix(X)

    labels = get_clusters(X, n_clusters, random_state)

    threading = copy.deepcopy(labels)
    treadling = copy.deepcopy(labels)
    tieup = np.eye(n_clusters)

    draft_matrix = get_draft(treadling, threading, tieup)
    treadling_matrix = get_treadling_matrix(treadling)
    threading_matrix = get_threading_matrix(threading)

    save_matrices_as_csv(
        subdir_output, threading_matrix, tieup, treadling_matrix, draft_matrix
    )


if __name__ == "__main__":
    generate_textile_matrices_from_data()
