import logging
from typing import Dict

import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap, BoundaryNorm
import numpy as np
import pandas as pd
import random as rm
import copy as copy
import os

from sklearn.cluster import KMeans
import click
from datetime import datetime
import sys

# for convolution
# https://scikit-image.org/docs/dev/auto_examples/filters/plot_rank_mean.html
from skimage import data
from skimage.morphology import disk
from skimage.morphology import square
from skimage.filters import rank
from skimage.util import img_as_ubyte


def get_threading(labels_revisited):
    threading = copy.deepcopy(labels_revisited)

    return threading


def get_treadling(labels_revisited):
    treadling = copy.deepcopy(labels_revisited)

    return treadling


def get_tieup(n_clusters, random_tieup=False):
    if random_tieup is False:
        tieup = np.eye(n_clusters)
    else:
        tieup = np.random.randint(2, size=(n_clusters, n_clusters))

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
        rename_dict = {"4_colonias_id": "coloniaid", "4_alcaldias_id": "alcaldiaid"}
        # rename_dict = {"X4_colonias_id": "coloniaid", "X4_alcaldias_id": "alcaldiaid"}

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
    X = X / (X.std(axis=0) + 0.001)

    return X


def get_clusters(X, n_clusters, random_state=0):
    kmeans = KMeans(n_clusters=n_clusters, random_state=random_state).fit(X)
    labels = kmeans.labels_
    labels = labels + 1

    return labels


def sort_df_by_labels(df_input, labels):
    df = df_input[["alcaldiaid"]].copy()
    df["labels"] = labels
    df_sorted = df.sort_values(by=["labels"])
    labels_revisited = df_sorted["alcaldiaid"]
    labels_revisited = labels_revisited[~pd.isnull(labels_revisited)]
    labels_revisited = list(labels_revisited)
    labels_revisited = [int(i) for i in labels_revisited]

    #     return labels_revisited
    return {"labels_revisited": labels_revisited, "sort_index": df_sorted.index}


def save_matrices_as_csv(
    subdir_output, threading_matrix, tieup, treadling_matrix, draft_matrix = None):
    filenames = ["threading", "tieup", "treadling"]
    for idx, f in enumerate(filenames):
        filenames[idx] = os.path.join(subdir_output, f + ".csv")

    matrices = [threading_matrix, tieup, treadling_matrix]

    for filename, matrix in zip(filenames, matrices):
        save_matrix_as_csv(filename, matrix)

    if draft_matrix is not None:
        draft_filename = os.path.join(subdir_output, f + ".csv")
        save_matrix_as_csv(draft_filename, draft_matrix)



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

    filenames = ["threading", "tieup", "treadling"]
    matrices = [threading_matrix, tieup, treadling_matrix]

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


def convolve_matrix(matrix, convolution_radius, conv_shape):
    if conv_shape == "disk":
        selem = disk(convolution_radius)
    elif conv_shape == "square":
        selem = square(convolution_radius)

    matrix_convoled = rank.mean(img_as_ubyte(matrix), selem=selem)

    matrix_convoled[matrix_convoled > 0] = 1
    matrix_convoled[matrix_convoled == 0] = 0

    return matrix_convoled


def get_labels(X, n_clusters, random_state, df, n_clusters_treadling):
    labels = get_clusters(X, n_clusters, random_state)
    labels_sort_output = sort_df_by_labels(df, labels)
    labels_revisited = labels_sort_output["labels_revisited"]
    labels_revisited_sort_index = labels_sort_output["sort_index"]

    if n_clusters_treadling is None:
        labels_treadling_revisited = labels_revisited.copy()
    else:
        labels_treadling = get_clusters(X, n_clusters_treadling, random_state)
        labels_treadling_revisited = labels_treadling[labels_revisited_sort_index]

    return {
        "labels_threading": labels_revisited,
        "labels_treadling": labels_treadling_revisited,
    }

def generate_textile_matrices_from_data_without_saving(
    filename,
    generate_plots_bool=True,
    random_state=None,
    n_clusters_treadling=None,
    random_tieup=False,
    convolution_radius=None,
    conv_shape="square",
    sample_size=None,
    n_clusters=None,
    random_seed=None,
    include_draft=True
) -> Dict:
    #     ignored parameters: sample_size, n_clusters, random_seed

    if random_state is None:
        random_state = int(datetime.utcnow().timestamp())

    print(f"random_state:{random_state}")

    if convolution_radius is None:
        convolution_radius = rm.randrange(100, 150)

    print(f"convolution_radius:{convolution_radius}")

    if n_clusters_treadling is None:
        n_clusters_treadling = rm.randrange(5, 16)

    print(f"n_clusters_treadling:{n_clusters_treadling}")

    df = load_data(filename)
    df = rename_columns(df)
    df = filter_rows(df)
    n_clusters = len(df["alcaldiaid"].unique())

    X = extract_data_from_df(df)
    X = normalize_matrix(X)

    labels_all = get_labels(X, n_clusters, random_state, df, n_clusters_treadling)
    labels_revisited = labels_all["labels_threading"]
    labels_treadling_revisited = labels_all["labels_treadling"]

    threading = get_threading(labels_revisited)
    treadling = get_treadling(labels_treadling_revisited)
    tieup = get_tieup(n_clusters, random_tieup=random_tieup)

    treadling_matrix = get_treadling_matrix(treadling)
    threading_matrix = get_threading_matrix(threading)

    
    result = {
        "threading_matrix": threading_matrix.tolist(),
        "treadling_matrix": treadling_matrix.tolist(),
        "tieup": tieup.tolist(),
    }

    if include_draft:
        draft_matrix = get_draft(treadling, threading, tieup)
        draft_matrix = convolve_matrix(draft_matrix, convolution_radius, conv_shape)
        result.update({"draft_matrix": draft_matrix.tolist()})

    return result


def generate_weather_from_data_without_saving(filename) -> Dict:
    df = load_data(filename)

    return {"colonias_id": df["4_colonias_id"].to_list(),
            "alcaldias_id": df["4_alcaldias_id"].to_list(),
            "weather_humidity_intensity": df["weather_humidity_intensity"].to_list(),
            "weather_wind_speed_intensity": df["weather_wind_speed_intensity"].to_list(),
            "weather_temp_intensity": df["weather_temp_intensity"].to_list(),
            }


def generate_textile_matrices_from_data(
    filename,
    dir_output,
    generate_plots_bool=True,
    random_state=None,
    n_clusters_treadling=None,
    random_tieup=False,
    convolution_radius=None,
    conv_shape="square",
    sample_size=None,
    n_clusters=None,
    random_seed=None,
    include_draft=True,
) -> None:

    if not os.path.exists(dir_output):
        os.makedirs(dir_output, exist_ok=True)

    result = generate_textile_matrices_from_data_without_saving(
        filename,
        generate_plots_bool,
        random_state,
        n_clusters_treadling,
        random_tieup,
        convolution_radius,
        conv_shape,
        sample_size,
        n_clusters,
        random_seed)

    save_matrices_as_csv(
        dir_output, 
        result.get("threading_matrix"), 
        result.get("tieup"), 
        result.get("treadling_matrix"), 
        result.get("draft_matrix")
    )

    #if generate_plots_bool:
    #    generate_plots(
    #        threading_matrix, tieup, treadling_matrix, draft_matrix, dir_output
    #    )


if __name__ == "__main__":
    generate_textile_matrices_from_data()
