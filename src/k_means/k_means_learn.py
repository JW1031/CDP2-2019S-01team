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
from sklearn.cluster import KMeans
from concurrent.futures import ProcessPoolExecutor, as_completed, wait
from .InfluxData import InfluxData
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm
import logging
import config

EXPECT_DATASET_SIZE = 60000 # 10min data

def InitDB():
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

def psd_processing(dev_id:str):
    cli = InfluxData()
    cli.set_client(config.INFLUXDB_HOST,
                        config.INFLUXDB_PORT,
                        config.INFLUXDB_ID,
                        config.INFLUXDB_PASSWORD,
                        database=config.INFLUXDB_DATABASE)
    rs = cli.query(f"select * from acc_data where dev_id='{dev_id}' and time >= now() -40m AND time <= now() - 30m")
    data = cli.resultSetToDF(rs)
    if type(data['acc_data']) is list: #  it means empty data
        logging.warning('empty data')
        return dev_id
    if len(data['acc_data']) < EXPECT_DATASET_SIZE*0.9: # not enough data size
        logging.warning('not enough data size')
        return dev_id
    data = data['acc_data'] # convert dict_dataframe to dataframe
    x = data['x']*constants.g
    y = data['y']*constants.g
    z = data['z']*constants.g
    offset_x = x - np.mean(x)
    offset_y = y - np.mean(y)
    offset_z = z - np.mean(z)
    Pxx, freqs_x = plt.psd(offset_x,NFFT=200,Fs=100)
    Pyy, freqs_y = plt.psd(offset_y,NFFT=200,Fs=100)
    Pzz, freqs_z = plt.psd(offset_z,NFFT=200,Fs=100)
    row = {'dev_id':dev_id,
            'Mean_PSD_x':np.mean(Pxx),
            'Mean_PSD_y':np.mean(Pyy),
            'Mean_PSD_z':np.mean(Pzz),
            'MAX_PSD_x': np.max(Pxx),
            'MAX_PSD_y': np.max(Pyy),
            'MAX_PSD_z': np.max(Pzz),
            'MIN_PSD_x': np.min(Pxx),
            'MIN_PSD_y': np.min(Pyy),
            'MIN_PSD_z': np.min(Pzz)
            }
    return row

def run_query(new_df):
    try:
        device_ids = InitDB()
    except:
        logging.error("[K_MEANS] Learning failed")
        return
    #pool = ProcessPoolExecutor(len(device_ids))
    pool = ProcessPoolExecutor(os.cpu_count())
    futures = []
    for dev_id in device_ids:
        futures.append(pool.submit(psd_processing,dev_id))

    err_devices = [] 

    for x in as_completed(futures,timeout=120):
        try:
            if type(x.result()) is dict:
                new_df = new_df.append(x.result(),ignore_index=True)
            else:
                err_devices.append(x.result())
        except Exception as err:
            logging.error(err)
    cant_qry = set(device_ids) - set(err_devices) - set(new_df['dev_id'])
    if len(cant_qry) != 0:
        logging.info(f"[K_MEANS] Couldn't processing device: {cant_qry}")
    return new_df
    

def ShowFeature(new_df):
    fig = plt.figure()
    ax = plt.gca(projection='3d')
    ax.scatter(new_df['Mean_PSD_x'],new_df['Mean_PSD_y'],new_df['Mean_PSD_z'])
    ax.set_xlim(-0.005,0.02)
    ax.set_ylim(-0.005,0.02)
    ax.set_zlim(-0.005,0.02)
    plt.show()

from sklearn.preprocessing import StandardScaler, MinMaxScaler, RobustScaler
def FeatureProcessing(new_df):
    dev_id = new_df['dev_id']
    Feature = new_df.loc[:,new_df.columns != 'dev_id']
    ss = RobustScaler()
    ss.fit(Feature)
    Feature = ss.transform(Feature)
    return dev_id,Feature

def k_means_clustering(dev_id,Feature,filesave=False):
    kmeans = KMeans(n_clusters=4).fit(Feature)
    if filesave is True:
        np.save('PSD_k-means_center.npy',kmeans.cluster_centers_)
    kmeans_labels = kmeans.labels_
    kmeans_results = pd.concat([dev_id,pd.DataFrame(kmeans_labels.reshape(-1,1),columns=['prediction'])],axis=1)
    kmeans_outliers = kmeans_results.loc[kmeans_results['prediction'] != 0]
    return kmeans_labels, kmeans_results, kmeans_outliers

def test():
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
    new_df = run_query(new_df)
    dev_id, Feature = FeatureProcessing(new_df)
    labels, results, outliers = k_means_clustering(dev_id,Feature)
    print(outliers)