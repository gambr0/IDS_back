from sqlalchemy import create_engine
import pandas as pd
import numpy as np
from sklearn.preprocessing import OneHotEncoder, StandardScaler
import pickle
import json
import requests

class Analyzer:
    def __init__(self, model_url):
        self.model_url = model_url
        self.db_info = {
            'user': 'labeler',
            'pwd': '2020labeler',
            'host': 'localhost',
            'port': 3306,
            'database': 'network'
        }
        self.process_point = 0
        self.left_rows = 0
        with open('../encoders/protocols_enc.pkl','rb') as f:
            self.protocols_enc = pickle.load(f)

        with open('../encoders/scaler.pkl','rb') as f:
            self.scaler = pickle.load(f)
        
        with open('../encoders/enc.pkl','rb') as f:
            self.enc = pickle.load(f)
        self.headers = {"content-type": "application/json"}
    
    def reconData(self, X, timestep):
        X_time = []
        y_process_points = []
        for i in range(X.shape[0] - timestep):
            window = X[i:i+timestep]
            X_time.append(window)
            y_process_point = i + (timestep // 2)
            y_process_points.append(y_process_point)
        self.process_point += X.shape[0] - timestep
        X_time = np.array(X_time)
        data = json.dumps({"signature_name": "serving_default", "instances": X_time.tolist()})
        return data, y_process_points

    def req_model(self, data):
        json_response = requests.post(self.model_url, data=data, headers=self.headers)
        y_pred = np.array(json.loads(json_response.text)['predictions'])

        labels = np.argmax(y_pred,axis=-1)
        for i in range(labels.shape[0]):
            y_pred[i,:] = 0
            y_pred[i,labels[i]] = 1
            y_pred_label = self.enc.inverse_transform(y_pred)
        return y_pred_label

    def analyze(self):
        engine = create_engine(f"mysql+pymysql://{self.db_info['user']}:{self.db_info['pwd']}@{self.db_info['host']}:{self.db_info['port']}/{self.db_info['database']}")
        engine.connect()
        while 1:
            rows_count = engine.execute('SELECT count(`index`) from network_features').first()[0]
            left_rows = rows_count - self.process_point
            if left_rows > 25:
                sql = f'SELECT * from network_features LIMIT {self.process_point},{left_rows}'
                data = pd.read_sql(sql, con=engine)
                data = data.fillna(0.0)
                info = data.iloc[:,[5]+list(range(7,73))]
                ifwb_avb = (info['FWD Init Win Bytes'] != -1).apply(lambda x: float(x))
                ibwb_avb = (info['Bwd Init Win Bytes'] != -1).apply(lambda x: float(x))
                info.loc[info['FWD Init Win Bytes'] == -1, 'FWD Init Win Bytes'] = 0
                info.loc[info['Bwd Init Win Bytes'] == -1, 'Bwd Init Win Bytes'] = 0
                info['FWD Init Win Bytes Available'] = ifwb_avb 
                info['Bwd Init Win Bytes Available'] = ibwb_avb
                info = info.values
                protocol_cols = self.protocols_enc.transform((info[:,0]).reshape((-1,1)))
                info = np.delete(info, 0, axis=1)
                info = np.append(info, protocol_cols, axis=1)
                info = self.scaler.transform(info)
                info, y_process_points = self.reconData(info, 25)
                
                result = self.req_model(info)
                final_data = data.iloc[y_process_points,list(range(5))+[6]]
                final_data['Class'] = result
                pd.io.sql.to_sql(final_data,'network_class', con=engine, if_exists='append', index=False)
                

if __name__ == '__main__':
    a = Analyzer('http://localhost:8051/v1/models/RealTimeBiLSTM:predict')
    a.analyze()