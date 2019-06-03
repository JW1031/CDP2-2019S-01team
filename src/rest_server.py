from flask import Flask, request, jsonify
from flask_restful import Resource, Api
from flask_restful import reqparse

import matplotlib.pyplot as plt
import matplotlib as mp
mp.use('Agg')
plt.ioff()

from k_means import k_means_model as km
import config

from datetime import datetime
import time
import logging

app = Flask(__name__)
api = Api(app)

class CreateReport(Resource):
    def post(self):
        try:
            req = request.get_json(force=True)
            logging.info(req)
            err = ''
            time_start = time.time()
            time_range = ["now()-40m","now()-30m"]
            try:
                time_range = [float(req['time_range']['gte'])/10e3,
                                float(req['time_range']['lte'])/10e3]
                time_range = list(map(datetime.fromtimestamp,time_range))
                time_range = list(map(lambda x: x.astimezone().isoformat(),time_range))
                result = km.HowToUse(time_range)
            except Exception as e:
                result = km.HowToUse()
                err = str(e)
            duration = time.time() - time_start
            result = list(result['dev_id'])
            return {'response':f'Request accepted!', 
                    'report_id':req["id"],
                    'time_start' : time_range[0],
                    'time_end' : time_range[1],
                    'result':result,
                    'duration' : duration,
                    'error' : err}, 200
        except Exception as e:
            return {'error': str(e)}
    def get(self):
        return {'response': 'test request accepted!'}

api.add_resource(CreateReport,'/request')

if __name__=='__main__':
    app.run(host=config.REST_HOST,port=config.REST_PORT,debug=True)