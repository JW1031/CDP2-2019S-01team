from influxdb import InfluxDBClient
from concurrent.futures import ProcessPoolExecutor
from multiprocessing import Queue
import os
import time
client: InfluxDBClient = InfluxDBClient('155.230.28.170',8086,'sslab','1231',database='kmaeq')

threads = os.cpu_count()
if threads is None:
    threads = 4
else:
    threads *= 4
tpool = ProcessPoolExecutor(threads)

# show device ids
rs = client.query("show series")
dev_ids = list(map(lambda x: x[0].split('=')[1], rs.raw['series'][0]['values']))

import csv

def qry(dev_id:str):
    rs = client.query(f"select * from acc_data where dev_id='{dev_id}' and time >= '2019-03-26T02:00:00Z' AND time <= '2019-03-26T03:00:00Z'")
    with open(f'{dev_id}_output.csv','w',newline='') as f:
        csv_writer = csv.writer(f)
        for line in rs.raw['series'][0]['values']:
            csv_writer.writerow(line)

start = time.time()

futures = []

for id in dev_ids:
        futures.append(tpool.submit(qry,id))

print("program end")
print("program processing time: ",time.time()-start)
