import os
import pickle
import glob
import re
import importlib

import numpy as np
import pandas as pd
import seaborn as sns

import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.patches import Patch
import matplotlib.colors as mcolors
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.lines import Line2D

from scipy.stats import shapiro, ttest_rel, wilcoxon

#####

DATASET_DIR = "../Dataset/"
# ^^^ UNZIP DATASET ITEMS AND INSERT CORRECT DATASET DIRECTORY HERE ^^^
METADATA_DIR = DATASET_DIR + "Metadata/Demographics.csv"
MID_QUESTIONNAIRE_DIR = DATASET_DIR + "Questionnaire/mid.csv"
FINAL_QUESTIONNAIRE_DIR = DATASET_DIR + "Questionnaire/final.csv"
RECORDINGS_DIR = DATASET_DIR + "Recordings/"

#####

ASPECT_RATIO = 1.8
FIG_HEIGHT = 5

plt.rcParams['font.family'] = 'Times New Roman'
plt.rcParams['font.size'] = 13
plt.rcParams['savefig.pad_inches'] = 0.05

FONTSIZE = 13

AXIS_LINEWIDTH = 1.5
GRID_ALPHA = 0.5
GRID_LINESTYLE = '--'

BOX_WIDTH = 0.3
BOX_LINEWIDTH = 1
BOX_COLOR = "#4472C4"
MEAN_LINEWIDTH = 2
MEAN_COLOR = 'black'

BAR_WIDTH = 0.2
BAR_COLOR = "#6D8EC7"
BAR_EDGECOLOR = 'black'
BAR_LINEWIDTH = 1
BAR_ALPHA = 1

HIST_HUE_COLORS_DIVERSE = ['#FF8000', '#FFBF80', '#FF2B00', '#FF9580',  '#993300', '#BF8060',]
HIST_HUE_COLORS_SPECTRUM = ["#A8C4E6", "#7DA6D9", "#2F5597", "#1E3A6B", "#0F2345"]