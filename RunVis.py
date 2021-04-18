from tensorflow.python.keras.backend import switch
from VisModel import VisualizationModel
from numpy.random import seed as np_seed
import tensorflow as tf
import numpy as np
from Utils import seeding
import os
import math
import matplotlib.pyplot as plt
import matplotlib as mpl
from pathlib import Path
from Datasets import DatasetGenerator as dg
import Vis as vis


"""Gets visualizations for a list of models
:param model_list: the list of models to use
:param dataset_options: ds.DataTypes(.options) - the options for the dataset
"""
def runModelBatch(model_list, dataset_options):
    plotDataset=True
    for model_id in model_list:
        model_path = MODEL_LOAD_PATH.format(exp_num=exp_num, model_id=model_id)
        save_path = VIS_SAVE_PATH.format(exp_num=exp_num, dataset=dataset_options.name, model_id=model_id) 
        model = tf.keras.models.load_model(model_path)
        vis.getVisualizations(model=model, dataset_options=dataset_options, save_path=save_path, name=model_id, plotDataset=plotDataset)
        plotDataset=False

"""Gets visualizations for checkpoints within a list of models
Use useAuto and optionally step_percent, OR checkpoint_list

:param model_list: list - the list of models to get checkpoints from
:param dataset_options: dg.DataTypes(.options) - the options for the dataset
:param checkpoint_list: list - the checkpoints to use for visualizations
:param useAuto: boolean - whether to automatically generate the checkpoints or use the checkpoint_list
:param step_percent: float - if using auto, the percent of the checkpoints to get
(.1 gets 10% of the checkpoints, in a 100 checkpoint list itll get each tenth one + the first and last)
"""
def runCheckpointBatch(model_list:list, dataset_options:dg.DataTypes, checkpoint_list:list=None, useAuto:bool=True, step_percent:float=0.1):
    plotDataset=True
    for model_id in model_list:
        checkpoint_path = CHECKPOINT_LOAD_PATH.format(exp_num=exp_num, model_id=model_id, checkpoint="")
        checkpoint_list = getCheckpoints(model_path=checkpoint_path, step_percent=step_percent) if useAuto else checkpoint_list
        for checkpoint in checkpoint_list:
            model_path = CHECKPOINT_LOAD_PATH.format(exp_num=exp_num, model_id=model_id, checkpoint=checkpoint)
            model = tf.keras.models.load_model(model_path)
            save_path = VIS_SAVE_PATH.format(exp_num=exp_num, dataset=dataset_options.name, model_id=model_id)
            vis.getVisualizations(model=model, dataset_options=dataset_options, save_path=save_path, name=checkpoint, plotDataset=plotDataset)
            plotDataset=False

"""Gets checkpoints from the checkpoint folder of the given model path

:param model_path: str - the path of the model checkpoint folder
:param step_percent: float - the percent of checkpoints to get, and the percent between checkpoints
(.1 gets 10% of the checkpoints, in a 100 checkpoint list itll get each tenth one + the first and last)
:returns: list - the checkpoint ids as a list
"""
def getCheckpoints(model_path:str, step_percent:float=0.2) -> list:
    # sort first by accuracy because epoch isnt zfilled
    all_checkpoints = sorted(os.listdir(model_path), key=lambda dir: dir[-5:])
    checkpoint_list = []
    length = len(all_checkpoints)
    # get files between steps
    step = round(length * step_percent)
    # get checkpoints
    checkpoint_list += all_checkpoints[:length-1:step]
    checkpoint_list.append(all_checkpoints[length-1])
    return checkpoint_list

"""Trains a set of networks for the given layer shape list

:param layer_shape_list: list - the list of shapes for the networks
"""
def createNetworkSet(layer_shape_list:list):
    for shape in layer_shape_list:
        network = VisualizationModel(exp_num, seed)
        network.trainNewNetwork(epochs=epochs, shape=shape, dataset_options=ds_options)
        

MODEL_LOAD_PATH = ".local\\models\\exp-{exp_num}\\model-{model_id}\\model"
CHECKPOINT_LOAD_PATH = ".local\\models\\exp-{exp_num}\\model-{model_id}\\checkpoints\\{checkpoint}"
VIS_SAVE_PATH = ".local\\visualizations\\exp-{exp_num}\\dataset-{dataset}\\model-{model_id}"
DATAPLOT_SAVE_PATH = ".local\\visualizations\\exp-{exp_num}\\dataset-{dataset}"
ds_options = dg.DataTypes.GaussianBoundaryOptions()
ds_options.peak, ds_options.sigma = ds_options.sigma, ds_options.peak
exp_num = 2
seed = 2
seeding.setSeed(seed)
epochs = 4

model_list = ["0000-[4]"]
# runCheckpointBatch(model_list=model_list, dataset_options=dataset_options, useAuto=True)
dataset = dg.getDataset(dataType=ds_options.name, options=ds_options)
data_save_path = DATAPLOT_SAVE_PATH.format(exp_num=exp_num, dataset=ds_options.name)
vis.graphDataset(dataset, data_save_path)

