from keras.models import Sequential
from keras.layers import Dense, Activation
from keras.utils import to_categorical
from db import createDatasetsDocument, createNeuralNetsDocument, createExperimentsDocument
import GaussianBoundary as gb
import numpy as np
import keras
from Utils import iterate,plotData
from generateNN import make
import matplotlib.pyplot as plt

# Continuously runs epochs on neural net with given data points until error is minimized
# nn: compiled neural net
# tdata = training data
# vdata = validation data

def test(nn, tdata, vdata):
    tCoords = tdata[:, [0,1]]
    tLabels = tdata[:, [2]]
    #tLabels = to_categorical(tLabels, num_classes=None)

    # print(tLabels)

    vCoords = vdata[:, [0,1]]
    vLabels = tdata[:, [2]]

    vErrorConsec = 0
    cont = True
    tError = []
    vError = []
    tAcc = []
    vAcc = [];
    epoch = 0
    lowestVError = 1
    statsAtLowestVError = []
    # stopping criterion
    stopC = {
        "Every 5 epochs":[],
        "Validation error increases for 5 consec epochs":[], #0
        "Validation error increases for 10 consec epochs":[], #1
        "Validation error increases for 15 consec epochs":[], #2
        "Decrease in training error from 1 epoch to next is below %1":[], #3
        "Training error below 15%":[], #4
        "Training error below 10%":[], #5
        "Training error below 5%":[], #6
        "Lowest validation error":[] #7
    }
    #indicates if stopping criterion has been completed
    comp = [False, False, False, False, False, False, False, False]

    while(all(value for value in comp)):
        #train (1) epochs
        nn.fit(x=tCoords, y=tLabels, batch_size=100, epochs=1, verbose=1)
        # call evaluate - record test & validation error
        stats = nn.evaluate(x=vCoords, y=vLabels, batch_size=100, verbose=1)
        epoch += 1

        print(stats)

        # record training error & accuracy
        tError.append(stats[0]) # training error
        tAcc.append(stats[1]) # training accuracy
        # record validation error & accuracy
        vError.append(stats[0]) # validation error
        vAcc.append(stats[1]) # validation accuracy

        # final training error, final validation error, final weights if needed for stopC
        # get_weights returns a list of numpy arrays
        finalStats = {
            "Final validation error":stats[2],
            "Final training error":stats[0], #0
            "Final weights":nn.get_weights() #1
        }

        # finalStats = [stats[0], stats[2], nn.get_weights()]
        if( vError[len(vError)-1] < lowestVError ):
            lowestVError = vError[len(vError)-1]
            statsAtLowestVError = finalStats
        if( epoch % 5 == 0 ):
            stopC["Every 5 epochs"].append(finalStats)
        # if validation error this epoch increases from val error from the previous epoch
        if(len(vError) > 1 and vError[len(vError)-1] > vError[len(vError)-2] and not comp[0]):
            vErrorConsec += 1
            comp[0] = True
        if(vErrorConsec > 5 and not comp[1]):
            stopC["Validation error increases for 5 consec epochs"].append(finalStats)
            comp[1] = True
        if(vErrorConsec > 10 and not comp[2]):
            stopC["Validation error increases for 10 consec epochs"].append(finalStats)
            comp[2] = True
        if(vErrorConsec > 15 and not comp[3]):
            stopC["Validation error increases for 15 consec epochs"].append(finalStats)
            comp[3] = True
        if( tError[len(tError)-1] < 0.15 and not comp[4]):
            stopC["Training error below 15%"].append(finalStats)
            comp[4] = True
        if( tError[len(tError)-1] < 0.10 and not comp[5]):
            stopC["Training error below 10%"].append(finalStats)
            comp[5] = True
        if( tError[len(tError)-1] < 0.05 and not comp[6]):
            stopC["Training error below 5%"].append(finalStats)
            comp[6] = True
        if(len(vError) > 1 and ( vError[len(vError)-2] - vError[len(vError)-1] ) < 0.01 ):
            stopC["Decrease in training error from 1 epoch to next is below %1"].append(finalStats)
            comp[7] = True
    stopC["Lowest validation error"] = statsAtLowestVError
    return tAcc, vAcc, stopC

#
MAX_NODES = 6
MAX_LAYERS = 4

IN_SHAPE = (2,)
OUT_SHAPE = (1,)

NODES_INLAYER = 2
NODES_OUTLAYER = 1

# create ids in list form
ids = []
id = iterate([1], MAX_LAYERS, MAX_NODES)
newid = 0
while(id != -1):
    ids.append(id)
    newid = iterate(id, MAX_LAYERS, MAX_NODES)
    id = newid

# create data points
coVec = gb.genFunctionUniform(3, 0, 4)
# print(coVec)
coVec = [1, 1, 1]

tdata = np.array( gb.getPoints(coVec, 1000, 0, 0, -10, 10, -10, 10) )
vdata = np.array( gb.getPoints(coVec, 1000, 0, 0, -10, 10, -10, 10) )

# plotting the normal dataset, no noise
# plot the dataset, with noise
# use a parabola, not too wide

# print(tdata)

# plotData(tdata)
# plotData(vdata)

createDatasetsDocument(coVec, [3, 7], [-100, 100, -100, 100], tdata.tolist(), vdata.tolist())

# iterates through all ids and creates neural nets
nets = []
for struct in ids:
    layers = []
    for i in struct:
        layers.append(int(i))
    # the shape wasn't working, so I took out the list dependency
    nets.append(make(NODES_INLAYER, layers, NODES_OUTLAYER, IN_SHAPE, 'tanh'))

    # change the np arrays of weights to lists of lists
    # https://stackoverflow.com/questions/46817085/keras-interpreting-the-output-of-get-weights

    weights = list(map(np.ndarray.tolist, nets[len(nets)-1].get_weights()))
    createNeuralNetsDocument(layers, IN_SHAPE, OUT_SHAPE, weights, 'glorot', 'sigmoid')

# runs test for each neural net
for index,nn in enumerate(nets):
    # what is the dataset ID? for now, I'm just setting it to 1
    tAcc, vAcc, stoppingCriterionDictionary = test(nn, tdata, vdata)
    createExperimentsDocument(ids[index], layerSizes, IN_SHAPE, OUT_SHAPE, 1, tAcc, vAcc, stoppingCriterionDictionary)
