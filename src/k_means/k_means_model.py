import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from concurrent.futures import ProcessPoolExecutor, as_completed, wait
from .InfluxData import InfluxData
from . import k_means_learn as kl
import logging
import config

import os, sys

#TODO
# Load Model config 
# New Query and get the data
# 

EXPECT_DATASET_SIZE = 60000 # 10min data
CLUSTER_CENTER_FILEPATH='PSD_k-means_center.npy'
K=4

def InitDB():
    ''' Check Influxdb connection
    if connection success, return device ids
    '''
    client = InfluxData()
    client.set_client(config.INFLUXDB_HOST,
                        config.INFLUXDB_PORT,
                        config.INFLUXDB_ID,
                        config.INFLUXDB_PASSWORD,
                        database=config.INFLUXDB_DATABASE)
    try:
        logging.info("[K_MEANS] InfluxDB Client Check...")
        client._cli.ping()
    except:
        logging.error("[K_MEANS] InfluxDB Connect failed")
        raise
        return None
    device_ids = client.get_device()
    return device_ids

def loadClusterCenter():
    ''' Read cluster center file, and return
    '''
    dir_path = os.path.dirname(os.path.realpath(__file__))
    os.chdir(dir_path)
    try:
        cluster_centers = np.load(CLUSTER_CENTER_FILEPATH)
    except IOError as e:
        logging.error(f"[PIPELINE] There is no file: {CLUSTER_CENTER_FILEPATH}")
        raise
    except:
        raise
    return cluster_centers

def model_loading():
    k_means = KMeans(n_clusters=K)
    k_means.cluster_centers_ = loadClusterCenter()
    return k_means

def HowToUse():
    device_ids = kl.InitDB()
    k_means = model_loading()
    raw_data = {'dev_id':[],
            'Mean_PSD_x':[],
            'Mean_PSD_y':[],
            'Mean_PSD_z':[],
            'MAX_PSD_x': [],
            'MAX_PSD_y': [],
            'MAX_PSD_z': [],
            'MIN_PSD_x': [],
            'MIN_PSD_y': [],
            'MIN_PSD_z': []
            }
    new_df = pd.DataFrame(raw_data)
    new_df = kl.run_query(new_df)
    dev_id, Feature = kl.FeatureProcessing(new_df)
    labels = k_means.predict(Feature)
    result = pd.concat([dev_id, pd.DataFrame(labels.reshape(-1,1),columns=['prediction'])],axis=1)
    outliers = result.loc[result['prediction'] != 0]
    print(outliers)