import logging
import random
import string
import os
import math
import binascii
import multiprocessing
import leangle
import bcrypt
import boto3
from datetime import date, datetime, time, timedelta
from multiprocessing import Process, Manager
from chalice import Blueprint, Response
from ..authorizer import token_auth
from ..constants import *

logs_routes = Blueprint('logs')
logger = logging.getLogger(__name__)

def get_timestamps_index(timestamp): #helper function to get 15 minute interval 
    time = timestamp%86400
    index = int(time/900)
    return index


def log_action(logFiles, grouping): #this is the threads job
    s3 = boto3.client('s3')

    timestamps = [None]*96 #make an 96 arrays of nones, incase one is not filled it will not be included in the response

    for logFile in logFiles: #itterate the jobs which the thread has to handle
        try:
            data = s3.get_object(Bucket="mina-parallelprocessing-bucket", Key=logFile)['Body'].read().decode("utf-8").split("\n")
        except BaseException as ex:
            return Response("", status_code=400)
        data.pop()

        for line in data: # itterate the lines in a single file
            line = line.replace("\r", "")
            line = line.split(" ")
            ts_index = get_timestamps_index(int(line[1])) #this is the index of the timestamp, e.g. 00:00 - 00:15 is index 0 (first 15 of the day)
            if(timestamps[ts_index]==None):
                timestamps[ts_index] = [0]*6 # [TIMESTAMP, MARKETCOUNT, LIMITCOUNT, STOPLOSSCOUNT, STOPLIMITCOUNT, TRAILINGSTOPCOUNT]
                dt = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
                timestamps[ts_index][0] = str((dt+timedelta(minutes=15*ts_index)).time())+" - "+str((dt+timedelta(minutes=15*(ts_index+1))).time())
            if(line[2]=="market_order"):
                timestamps[ts_index][1]+=1
            elif(line[2]=="limit_order "):
                timestamps[ts_index][2]+=1
            elif(line[2]=="stop_loss_order"):
                timestamps[ts_index][3]+=1
            elif(line[2]=="stop_limit_order"):
                timestamps[ts_index][4]+=1
            elif(line[2]=="trailing_stop_order"):
                timestamps[ts_index][5]+=1

    grouping[f'{os.getpid()}'] = timestamps # put results inside the process ID index of the shared memory dict
    return
    


@leangle.describe.tags(["Logs"])
@leangle.describe.parameter(name='body', _in='body', description='Process Logs')
@leangle.describe.response(200, description='Logs Processed')
@logs_routes.route('/', methods=['POST'], cors=True)
def process_logs():
    threads = []
    logFiles = {}
    timestamps = [None]*96
    body = logs_routes.current_request.json_body
    parallelFileProcessingCount = body['parallelFileProcessingCount']

    if not isinstance(parallelFileProcessingCount, int):
        return Response({"status": "failure", "reason": "Parallel File Processing count must be an integer"}, status_code=400)
    if parallelFileProcessingCount<1:
        return Response({"status": "failure", "reason": "Parallel File Processing count must be greater than zero"}, status_code=400)
    elif parallelFileProcessingCount>15:
        return Response({"status": "failure", "reason": "Parallel File Processing count must not exceed 15"}, status_code=400)

    logFiles = body['logFiles']

    for i, logFile in enumerate(logFiles):
        logFiles[i] = logFile.replace("s3://mina-parallelprocessing-bucket/", "")

    maxJobsPerThread = int(len(logFiles)/parallelFileProcessingCount) #e.g for 30 files and we have 15 threads, then max jobs/thread =2
    if maxJobsPerThread==0:
        maxJobsPerThread=1
    fileIndex = 0

    grouping = Manager().dict() #shared memory in the form of a dict

    while fileIndex < len(logFiles): #this is where I distribute the files to the threads 
        if(len(logFiles)-fileIndex-1 >= maxJobsPerThread): # assigns the files in even groups
            for x in range(maxJobsPerThread):
                inputs = logFiles[fileIndex : fileIndex+maxJobsPerThread]
                threads.append(Process(target=log_action, args=(inputs, grouping))) # appending a new process to the array of threads
                threads[len(threads)-1].start()
                fileIndex+=maxJobsPerThread
        else: # assigns to the final thread the rest of the jobs
            inputs = logFiles[fileIndex : fileIndex+len(logFiles)-fileIndex]
            threads.append(Process(target=log_action, args=(inputs, grouping))) # appending a new process to the array of threads
            threads[len(threads)-1].start()
            fileIndex+=len(logFiles)-fileIndex-1
            break

    for thread in threads:
        thread.join()

    for k, v in grouping.items(): #merging all results between the processes
        for i in range(len(timestamps)):
            if(v[i]==None):
                continue
            elif(timestamps[i]==None):
                timestamps[i] = [0]*6
                dt = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
                timestamps[i][0] = str((dt+timedelta(minutes=15*i)).time())+" - "+str((dt+timedelta(minutes=15*(i+1))).time())
                timestamps[i][1] = v[i][1]
                timestamps[i][2] = v[i][2]
                timestamps[i][3] = v[i][3]
                timestamps[i][4] = v[i][4]
                timestamps[i][5] = v[i][5]
            else:
                timestamps[i][1] = timestamps[i][1] + v[i][1]
                timestamps[i][2] = timestamps[i][2] + v[i][2]
                timestamps[i][3] = timestamps[i][3] + v[i][3]
                timestamps[i][4] = timestamps[i][4] + v[i][4]
                timestamps[i][5] = timestamps[i][5] + v[i][5]

# [TIMESTAMP, MARKETCOUNT, LIMITCOUNT, STOPLOSSCOUNT, STOPLIMITCOUNT, TRAILINGSTOPCOUNT] x 96

    return_obj = []
    for timestamp in timestamps:  # Formatting the final response according to the assignment doc
        if(timestamp==None):
            continue
        logs=[]
        if(timestamp[1]>0):
            logs.append({"order": "market_order", "count": timestamp[1]})
        if(timestamp[2]>0):
            logs.append({"order": "limit_order", "count": timestamp[2]})
        if(timestamp[3]>0):
            logs.append({"order": "stop_loss_order", "count": timestamp[3]})
        if(timestamp[4]>0):
            logs.append({"order": "stop_limit_order", "count": timestamp[4]})
        if(timestamp[5]>0):
            logs.append({"order": "trailing_stop_order", "count": timestamp[5]})
        return_obj.append({"timestamp": timestamp[0], "logs": logs})

    return Response({"response": return_obj},status_code=200)