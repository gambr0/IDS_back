from __future__ import absolute_import, unicode_literals

from celery import shared_task
from .capturer import Capturer
from .analyzer import Analyzer

@shared_task
def sniff_extract():
    cap = Capturer()
    cap.sniff_and_extract_features()

@shared_task
def analyze_label():
    a = Analyzer('http://localhost:8051/v1/models/RealTimeBiLSTM:predict')
    a.analyze()
