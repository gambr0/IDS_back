from scapy.all import get_if_list, sniff, wrpcap, AsyncSniffer
import time
import subprocess
from sqlalchemy import create_engine
import pandas as pd

class Capturer:
    def __init__(self):
        self.pkts = []
        self.filenum = 0
        self.start_time = 0.0
        self.process_point = 0
        self.meter_path = '../CICFlowMeter/CICFlowMeter-4.0/bin/' #Feature extractor
        self.db_info = {
            'user': 'writepcaper',
            'pwd': '2020writer',
            'host': 'localhost',
            'port': 3306,
            'database': 'network'
        }
        self.cols = ['Src IP', 'Src Port', 'Dst IP', 'Dst Port', 'Protocol', 'Timestamp', 'Flow Duration', 
        'Total Fwd Packet', 'Total Bwd packets', 'Total Length of Fwd Packet', 'Total Length of Bwd Packet', 
        'Fwd Packet Length Max', 'Fwd Packet Length Min', 'Fwd Packet Length Mean', 'Fwd Packet Length Std', 'Bwd Packet Length Max',
        'Bwd Packet Length Min', 'Bwd Packet Length Mean', 'Bwd Packet Length Std', 'Flow IAT Mean', 'Flow IAT Std', 'Flow IAT Max',
        'Flow IAT Min', 'Fwd IAT Total', 'Fwd IAT Mean', 'Fwd IAT Std', 'Fwd IAT Max', 'Fwd IAT Min', 'Bwd IAT Total',
        'Bwd IAT Mean', 'Bwd IAT Std', 'Bwd IAT Max', 'Bwd IAT Min', 'Fwd PSH Flags', 'Fwd URG Flags', 'Fwd Header Length',
        'Bwd Header Length', 'Fwd Packets/s', 'Bwd Packets/s', 'Packet Length Min', 'Packet Length Max', 'Packet Length Mean', 
        'Packet Length Std', 'Packet Length Variance', 'FIN Flag Count', 'SYN Flag Count', 'RST Flag Count', 'PSH Flag Count', 
        'ACK Flag Count', 'URG Flag Count', 'CWE Flag Count', 'ECE Flag Count', 'Down/Up Ratio', 'Average Packet Size', 
        'Fwd Segment Size Avg', 'Bwd Segment Size Avg', 'Subflow Fwd Packets', 'Subflow Fwd Bytes',
        'Subflow Bwd Packets', 'Subflow Bwd Bytes', 'FWD Init Win Bytes', 'Bwd Init Win Bytes', 'Fwd Act Data Pkts',
        'Fwd Seg Size Min', 'Active Mean', 'Active Std', 'Active Max', 'Active Min', 'Idle Mean', 'Idle Std',
        'Idle Max', 'Idle Min'] 
        self.process_idx = 0
        self.sniff_filter = "port 443 or port 80 or port 25 or port 110 or port 143 or port 21 or port 20200"
        self.processing = True
        # HTTPS, HTTP, SMTP, POP3, IMAP, SSH, FTP

    def write_pcap(self, pkt):
        current_time = time.time()
        if self.start_time == 0.0:
            self.start_time = time.time()       
            self.pkts.append(pkt)
        elif (current_time - self.start_time) < 5.0:
            self.pkts.append(pkt)
        else:
            pcap_path = f'../pcap/pcap{self.filenum}.pcap'
            wrpcap(pcap_path, self.pkts)
            self.pkts = []
            self.start_time = 0.0
            self.filenum += 1

    def sniff_and_extract_features(self):    
        engine = create_engine(f"mysql+pymysql://{self.db_info['user']}:{self.db_info['pwd']}@{self.db_info['host']}:{self.db_info['port']}/{self.db_info['database']}")
        engine.connect() 
        sniffer = AsyncSniffer(iface = 'eth0', filter = self.sniff_filter, prn=self.write_pcap)
        sniffer.start() #异步嗅探流量，向下继续执行

        while 1:
            if self.process_point < self.filenum: 
                p = subprocess.Popen(['./cfm',f'../../../pcap/pcap{self.process_point}.pcap','../../../features'],cwd=self.meter_path)
                p.wait()
                features = pd.read_csv(f'../features/pcap{self.process_point}.pcap_Flow.csv', usecols=self.cols)
                features.index += self.process_idx

                pd.io.sql.to_sql(features,'network_features', con=engine, if_exists='append')
                self.process_idx += features.shape[0]
                self.process_point += 1

if __name__ == '__main__':
    c = Capturer()
    c.sniff_and_extract_features()



