import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap, BoundaryNorm
import numpy as np
import pandas as pd
import random as rm
import copy as copy
import os
from sklearn.cluster import KMeans
import click


def get_threading(labels_revisited):
    threading = copy.deepcopy(labels_revisited)

    return threading


def get_treadling(labels_revisited):
    treadling = copy.deepcopy(labels_revisited)

    return treadling


def get_tieup(n_clusters):
    tieup = np.eye(n_clusters)

    return tieup


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


def rename_columns(df, rename_dict=None):
    if rename_dict is None:
        rename_dict = {"X4_colonias_id": "coloniaid", "X4_alcaldias_id": "alcaldiaid"}

    df = df.rename(columns=rename_dict)

    return df


def filter_rows(df):
    df = df[df["alcaldiaid"] <= 16].copy()

    return df


def extract_data_from_df(df, columns_to_drop=None):
    if columns_to_drop is None:
        columns_to_drop = ["coloniaid", "alcaldiaid"]

    df = df.drop(columns_to_drop, axis=1)
    X = df.to_numpy()

    return X


def normalize_matrix(X):
    X = X - X.mean(axis=0)
    X = X / X.std(axis=0)

    return X


def get_clusters(X, n_clusters, random_state=0):
    kmeans = KMeans(n_clusters=n_clusters, random_state=random_state).fit(X)
    labels = kmeans.labels_
    labels = labels + 1

    return labels


def sort_df_by_labels(df, labels):
    df["labels"] = labels
    df_sorted = df.sort_values(by=["labels"])
    df_sorted = df_sorted.reindex()
    labels_revisited = df_sorted["alcaldiaid"]
    labels_revisited = labels_revisited[~pd.isnull(labels_revisited)]
    labels_revisited = list(labels_revisited)
    labels_revisited = [int(i) for i in labels_revisited]

    return labels_revisited


def save_matrices_as_csv(
    subdir_output, threading_matrix, tieup, treadling_matrix, draft_matrix
):
    filenames = ["threading", "tieup", "treadling", "draft"]
    for idx, f in enumerate(filenames):
        filenames[idx] = os.path.join(subdir_output, f + ".csv")

    matrices = [threading_matrix, tieup, treadling_matrix, draft_matrix]

    for filename, matrix in zip(filenames, matrices):
        save_matrix_as_csv(filename, matrix)


def save_matrix_as_csv(
    filename, matrix, type=int, delimiter=",", newline="\n", fmt="%i"
):
    np.savetxt(
        filename, matrix.astype(type), delimiter=delimiter, newline=newline, fmt=fmt
    )


def visualize_matrix(
    matrix, y_color, x_color, title_str="", figsize=(20, 10), edgecolors="k"
):
    cmap = ListedColormap([y_color, x_color])
    bounds = [-1, 1, 2]
    norm = BoundaryNorm(bounds, cmap.N)

    fig, ax = plt.subplots(figsize=figsize)
    img = plt.pcolormesh(
        matrix,
        cmap=cmap,
        norm=norm,
        linewidth=0.1,
        edgecolors=edgecolors,
    )
    ax.set_aspect("equal", "box")
    ax.set_xticks([])
    ax.set_yticks([])
    plt.title(title_str)


def get_colors(x_color=None, y_color=None):
    if y_color is None:
        y_color = [255, 255, 255]
    if x_color is None:
        x_color = [0, 255, 255]
    y_color = np.array(y_color)
    x_color = np.array(x_color)

    y_color = y_color / 255
    x_color = x_color / 255

    return {"x_color": x_color, "y_color": y_color}


def generate_plots(
    threading_matrix,
    tieup,
    treadling_matrix,
    draft_matrix,
    subdir_output,
    save_plots=True,
):
    # colours
    colors = get_colors()
    x_color = colors["x_color"]
    y_color = colors["y_color"]

    filenames = ["threading", "tieup", "treadling", "draft"]
    matrices = [threading_matrix, tieup, treadling_matrix, draft_matrix]

    for filename, matrix in zip(filenames, matrices):
        visualize_matrix(
            matrix,
            y_color,
            x_color,
            title_str=filename,
            figsize=(50, 50),
            edgecolors=None,
        )
        if save_plots:
            filename = os.path.join(subdir_output, filename + ".png")
            plt.savefig(filename, bbox_inches="tight")
        plt.close("all")


@click.command()
@click.option(
    "--filename", default="../data/20210206_tejidos_testdata4.csv", show_default=True
)
@click.option(
    "--dir_output",
    default="../generate_textile_matrices/20210206_tejidos_testdata4",
    show_default=True,
)
@click.option("--generate_plots_bool", default=True, show_default=True)
@click.option("--random_state", default=0, show_default=True)
def generate_textile_matrices_from_data(
    filename, dir_output, generate_plots_bool, random_state=0
):
    if not os.path.exists(dir_output):
        os.makedirs(dir_output)

    df = load_data(filename)
    df = rename_columns(df)
    df = filter_rows(df)
    n_clusters = len(df["alcaldiaid"].unique())

    X = extract_data_from_df(df)
    X = normalize_matrix(X)

    labels = get_clusters(X, n_clusters, random_state)
    labels_revisited = sort_df_by_labels(df, labels)

    threading = get_threading(labels_revisited)
    treadling = get_treadling(labels_revisited)
    tieup = get_tieup(n_clusters)

    draft_matrix = get_draft(treadling, threading, tieup)
    treadling_matrix = get_treadling_matrix(treadling)
    threading_matrix = get_threading_matrix(threading)
    save_matrices_as_csv(
        dir_output, threading_matrix, tieup, treadling_matrix, draft_matrix
    )

    if generate_plots_bool:
        generate_plots(
            threading_matrix, tieup, treadling_matrix, draft_matrix, dir_output
        )


if __name__ == "__main__":
    generate_textile_matrices_from_data()
