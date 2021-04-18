from random import random, randrange
import numpy as np
from numpy.core.defchararray import array
from numpy.polynomial import Polynomial
import numpy.polynomial.polynomial as ply
import matplotlib.pyplot as plt
from matplotlib import patches
from matplotlib import cm
import sys
import os

path_to_file = os.path.abspath(os.path.dirname(__file__))
index_in_path = path_to_file.rfind("ShallowMind") + len("ShallowMind") # get path after "ShallowMind" (i cant count)
sm_path = path_to_file[:index_in_path]
sys.path.insert(0, sm_path)
from Datasets import ds_utils
import shapely
import shapely.geometry as geom
# coefficients are in ascending order of degree (x, x^2, x^3)
"""Gets points for a polynomial dataset
See DatasetGenerator.DataTypes commend for information on noise generation

:param numPoints: int - the number of points to generate
:param seed: int - the seed for randomization
:param coefficients: array_like - the coefficients for the polynomial IN ASCENDING ORDER BY DEGREE (x, x^2, x^3)
:param noise: tuple (distance, chance) - the noise for the polynomial - see DatasetGenerator.DataTypes commend for information on noise generation
:param vMin: int - the minimum value for the data points
:param vMax: int - the maximum value for the data points
"""
def getPoints(numPoints:int, seed:int, coefficients:list, noise:tuple, vMin:int, vMax:int):
    distance, chance = noise

    # generate random points within vMin, vMax
    data_rng = np.random.default_rng(seed)
    points = data_rng.random(size=(numPoints, 2))
    x_points = points[:,0]
    y_points = points[:,1]
    cMin = 0
    cMax = 1
    for index in range(numPoints):
        x_points[index] = ds_utils.scale(cMin, cMax, vMin, vMax, x_points[index])
        y_points[index] = ds_utils.scale(cMin, cMax, vMin, vMax, y_points[index])
    
    # create a line of points on the polynomial
    polyLinspace = createPolyLinspace(coefficients=coefficients, num=1000, domain=(vMin, vMax))
    polypairs = np.transpose(polyLinspace)
    line = geom.LineString(polypairs)
    distArr = []

    # get distance from each dataset point to the polynomial line
    for x in range(numPoints):
        point = geom.Point(x_points[x], y_points[x])
        length = point.distance(line)
        distArr.append(length)

    # convert to np array (numpy was being weird and appending wasnt working, idk)
    distArr = np.array(distArr)

    # above will be 1, below will be 0 (blue/red)
    # set points below function to 0, above to 1
    labels = np.full(numPoints, 0)
    # see if y value at poly is greater than the y value of the point, pretty much
    labels[np.where(ply.Polynomial._val(x_points, coefficients) > y_points)] = 1

    # range for noise is where the distance to the line is less than the noise distance
    noiseRange = np.where(distArr < distance)

    # see noise generation info for what this is doing
    # basically, chance to coin flip
    def chanceForNoiseUnvectorized(x):
        if (chance + random() >= 1):
            return abs(int(0.5 + random()))
        return labels[x]
    chanceForNoise = np.vectorize(chanceForNoiseUnvectorized)

    # implement noise
    if (len(noiseRange) > 0):
        labels[noiseRange] = chanceForNoise(noiseRange)
    
    # format is [[xy pairs], [labels]]
    dataset = np.array([points, []], dtype=object)
    dataset[1] = labels
    return dataset

"""Plots the polynomial dataset with the actual polynomial line
Coefficient/vMin/vMax should be same as what was inputted for the dataset

:param coefficients: array_like - the coefficients for the polynomial IN ASCENDING ORDER BY DEGREE (x, x^2, x^3)
:param noise: tuple (distance, chance) - the noise for the polynomial - see DatasetGenerator.DataTypes commend for information on noise generation
:param vMin: int - the minimum value for the data points
:param vMax: int - the maximum value for the data points
:param dataset: np.ndarray - the dataset to plot the line with
"""
def plotPolynomial(coefficients, vMin, vMax, dataset=None):
    cmap = cm.get_cmap("coolwarm")
    # data_rng = np.random.default_rng(seed)
    # points = data_rng.normal(size=(2, numPoints))
    fig = plt.figure()
    ax = fig.add_subplot()
    polyLinspace = createPolyLinspace(coefficients=coefficients, num=1000, domain=(vMin, vMax))
    plt.plot(polyLinspace[0], polyLinspace[1])
    # labels = np.array(["#FF0000"] * len(points[0]))
    # for index, point in enumerate(points):
    #     if ellipse.contains_point(point):
    #         labels[index] = "#0000FF"
    points = dataset[0]
    labels = dataset[1]
    plt.scatter(points[:,0], points[:,1], c=labels, zorder=1, cmap=cmap)
    plt.ylim(vMin-1, vMax+1) # LIMIT IT. or y values go c r az y 
    # plt.xlim(-20, 20)
    plt.show()

"""Gets a line of points on the polynomial
:param coefficients: np.ndarray - the polynomial's coefficients
:param num: int - the number of points to generate
:param domain: tuple (xMin, xMax) - the range of points to generate
:returns: np.ndarray - the points of the polynomial, [[x], [y]]
"""
def createPolyLinspace(coefficients, num, domain):
    xMin, xMax = domain
    xvals = np.linspace(xMin, xMax, num)
    # poly.polyval doesnt work so evaluate from base class
    polyLinspace = ply.Polynomial._val(xvals, coefficients)
    polypoints = np.array([xvals, polyLinspace])
    return polypoints

numPoints = 2000
seed = 1
coefficients = [
    -2,
    3,
    2,
    -4,
    0,
    1
]
distance = 1
chance = 0.5
noise = distance, chance
vMin = -10
vMax = 10

dataset = getPoints(numPoints=numPoints, seed=seed, coefficients=coefficients, noise=noise, vMin=vMin, vMax=vMax)
plotPolynomial(coefficients=coefficients, noise=noise, vMin=vMin, vMax=vMax, dataset=dataset)

