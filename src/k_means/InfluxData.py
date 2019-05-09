from influxdb import InfluxDBClient, DataFrameClient
class InfluxData:
    def __init_(self):
        self._cli = None;
        self._devices = []
        self._rs = None;
    def set_client(self,ip,port:int,ID,pwd,database):
        self._cli = InfluxDBClient(ip,port,ID,pwd,database=database)
        if self._cli is None:
            print("Client Connect fail!")
            return
        return self
    def get_device(self):
        if self._cli is None:
            print("Client Connect fail!")
            return
        self._rs = self._cli.query("show series")
        self._devices = list(map(lambda x: x[0].split('=')[1], self._rs.raw['series'][0]['values']))
        return self._devices
    def query(self,qry:str):
        try:
            self._rs = self._cli.query(qry)
        except:
            print("cannot query to influxDB")
            print("failed qry contents: ",qry)
            raise
        return self._rs
    def resultSetToDF(self,rs=None):
        # Convert query resultset to DataFrame
        if rs is None:
            return DataFrameClient()._to_dataframe(rs=self._rs)
        else:
            return DataFrameClient()._to_dataframe(rs=rs)
        