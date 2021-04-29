from django.http import HttpResponse
from .tasks import sniff_extract, analyze_label
from celery.task.control import inspect, revoke
from sqlalchemy import create_engine
import os

def start(request):
    sniff_extract.delay()
    analyze_label.delay()
    return HttpResponse("开始入侵监测！")

def stop(request):
    for task in inspect().active()['celery@kali']:
        revoke(task['id'], terminate=True)

    clear_paths = ['../pcap','../features']
    for path in clear_paths:
        files = os.listdir(path)
        for f in files:
            f_path = os.path.join(path,f)
            if os.path.exists(f_path):
                os.remove(f_path)

    engine = create_engine("mysql+pymysql://labeler:2020labeler@localhost:3306/network")
    engine.connect()
    engine.execute("TRUNCATE TABLE network_features")
    engine.execute("TRUNCATE TABLE network_class")
    