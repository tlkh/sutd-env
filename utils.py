import time

def calculate_h_timestamp():
    return int(time.time()//3600)


def calculate_m_timestamp():
    return int(time.time()//60)