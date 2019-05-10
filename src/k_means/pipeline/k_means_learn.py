import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from scipy import signal
from scipy import constants
import os
import glob
from matplotlib import rc
from sklearn.metrics import mean_squared_error
from InfluxData import InfluxData

def InitDB():
    client = InfluxData()
    client.set_client('155.230.28.170',8086,'sslab','1231',database='kmaeq')
    device_ids = client.get_device()
    pass


