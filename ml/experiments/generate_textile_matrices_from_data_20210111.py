# First visualizations with Data

#%matplotlib inline
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap,BoundaryNorm
import numpy as np
import pandas as pd
import random as rm
import copy as copy
import os
from sklearn.cluster import KMeans


def get_threading_matrix(threading):
    
    num_columns      = len(np.unique(threading))
    num_rows         = len(threading)
    threading_matrix = np.zeros((num_rows, num_columns))
    
    for idx, val in enumerate(threading):
        column = val - 1
        row    = idx
        threading_matrix[row,column] = 1

    return threading_matrix

def get_treadling_matrix(treadling):
    
    num_columns      = len(treadling)
    num_rows         = len(np.unique(treadling))
    treadling_matrix = np.zeros((num_rows, num_columns))
    
    for idx, val in enumerate(treadling):
        column = idx
        row    = val - 1
        treadling_matrix[row,column] = 1

    return treadling_matrix

def get_draft(treadling, threading, tieup):
    # create draft
    treadling_len  = len(treadling)
    threading_len  = len(threading)
    matrix         = np.zeros((treadling_len, threading_len))

    for i in range(treadling_len):
        y_th = treadling[i % treadling_len]
        for j in range(threading_len):
            x_th = threading[j % threading_len]
    #         print("i", i+1, "j", j+1, "x_th", x_th, "y_th", y_th, "treadling.length", treadling_len, "threading.length", threading_len)

            # choose color
            if tieup[x_th-1][y_th-1]==1:
                matrix[i,j]=1
    #             print("i", i+1, "j", j+1, "x_th", x_th, "y_th", y_th, "treadling.length", treadling_len, "threading.length", threading_len)
    
    return matrix

def visualize_matrix(matrix, y_color, x_color, title_str='', figsize=(20, 10), edgecolors='k'):
    
    cmap   = ListedColormap([y_color, x_color])
    bounds =[-1,1,2]
    norm   = BoundaryNorm(bounds, cmap.N)
       
    fig, ax = plt.subplots(figsize=figsize) 
    img = plt.pcolormesh(matrix, cmap=cmap, norm=norm, linewidth=0.1, edgecolors=edgecolors, )
    ax.set_aspect('equal', 'box')
    ax.set_xticks([]) 
    ax.set_yticks([]) 
    plt.title(title_str)
    
#     plt.show()

def get_colors(x_color = [0, 255, 255], y_color = [255,   255, 255]):
    y_color = np.array(y_color)
    x_color = np.array(x_color)

    y_color = y_color/255
    x_color = x_color/255
    
    return {'x_color':x_color, 'y_color':y_color}

def load_data(filename):
    
    df = pd.read_csv(filename)
    
    return df

def sample_data(df, sample_size = 1000, random_seed=10):
    
    rm.seed(random_seed)
    nrows     = df.shape[0]
    sample    = rm.sample(range(nrows),sample_size)
    df_sample = copy.deepcopy(df.iloc[sample])
    
    return df_sample

def extract_data_from_df(df):
    
    df = df.drop(['x', 'y'], axis=1)
    X  = df.to_numpy()
    
    return X

def normalize_matrix(X):
    
    X = X - X.mean(axis=0)
    X = X / X.std(axis=0)
    
    return X

def save_matrix_as_csv(filename, matrix, type=int, delimiter=",", newline='\n', fmt='%i'):

    np.savetxt(filename, matrix.astype(type), delimiter=delimiter, newline=newline, fmt=fmt)


def generate_textile_matrices_from_data(
    filename = 'data/20210108_tejidos_testdata2.csv', 
    dir_output = '2021-01-11', 
    save_plots = False,
    ):


    if not os.path.exists(dir_output):
        os.mkdir(dir_output)

    delimiter = ","
    newline   = '\n'
    fmt = '%i'#'%.10f'

    # colours
    colors = get_colors()
    x_color = colors['x_color']
    y_color = colors['y_color']

    df       = load_data(filename)
    df       = sample_data(df)
    X        = extract_data_from_df(df)
    X        = normalize_matrix(X)

    n_clusters = 20
    kmeans = KMeans(n_clusters=n_clusters, random_state=0).fit(X)
    labels = kmeans.labels_
    labels = labels + 1

    for n_clusters in range(2,50):
        
        print(n_clusters)
        
        kmeans = KMeans(n_clusters=n_clusters, random_state=0).fit(X)
        labels = kmeans.labels_
        labels = labels + 1
        
        threading  = copy.deepcopy(labels)
        treadling  = copy.deepcopy(labels)
        tieup      = np.eye(n_clusters)
            
        subdir_output = os.path.join(dir_output, 'n_clusters='+str(n_clusters))
        if not os.path.exists(subdir_output):
            os.mkdir(subdir_output)
        
        draft_matrix = get_draft(treadling, threading, tieup)
        visualize_matrix(draft_matrix, y_color, x_color, title_str='draft', figsize=(50,50), edgecolors=None)
        if save_plots:
            filename_plot = os.path.join(subdir_output, 'draft'+'.png')
            plt.savefig(filename_plot, bbox_inches='tight')

        plt.close('all')
        
        treadling_matrix = get_treadling_matrix(treadling)
        visualize_matrix(treadling_matrix, y_color, x_color, title_str='treadling', figsize=(50,50), edgecolors=None)
        if save_plots:
            filename_plot = os.path.join(subdir_output, 'treadling'+'.png')
            plt.savefig(filename_plot, bbox_inches='tight')

        plt.close('all')
        
        threading_matrix = get_threading_matrix(threading)
        visualize_matrix(threading_matrix, y_color, x_color, title_str='threading', figsize=(50,50), edgecolors=None)
        if save_plots:
            filename_plot = os.path.join(subdir_output, 'threading'+'.png')
            plt.savefig(filename_plot, bbox_inches='tight')

        plt.close('all')
        
        visualize_matrix(tieup, y_color, x_color, title_str='tieup', figsize=(50,50), edgecolors=None)
        if save_plots:
            filename_plot = os.path.join(subdir_output, 'tieup'+'.png')
            plt.savefig(filename_plot, bbox_inches='tight')

        plt.close('all')
        
        
        filename_threading = os.path.join(subdir_output, 'threading'+'.csv')
        filename_tieup     = os.path.join(subdir_output, 'tieup'+'.csv')
        filename_treadling = os.path.join(subdir_output, 'treadling'+'.csv')
        filename_draft     = os.path.join(subdir_output, 'draft'+'.csv')

        save_matrix_as_csv(filename_threading, threading_matrix)
        save_matrix_as_csv(filename_tieup, tieup)
        save_matrix_as_csv(filename_treadling, treadling_matrix)
        save_matrix_as_csv(filename_draft, draft_matrix)



if __name__ == "__main__":
    generate_textile_matrices_from_data(
    	filename = '../data/20210108_tejidos_testdata2.csv', 
    	dir_output = '2021-01-11', 
    	save_plots = False,
    	)