from email.mime import base
import importlib
from sre_parse import State
from turtle import color
import numpy as np
import qit
from Crypto.Random import random
import math
import matplotlib.pyplot as plt

def drawGraph(x, y, keySize, type):
    plt.clf()
    plt.plot(x, y)
    plt.grid(True)
    plt.savefig(type + str(keySize) + ".png")

def drawComparisonGraphQBER(distances, e91Qbers, bb84Qbers, keySize, type):
    plt.clf()
    plt.plot(distances, e91Qbers)
    plt.plot(distances, bb84Qbers)
    plt.grid(True)
    plt.savefig(type + str(keySize) + ".png")