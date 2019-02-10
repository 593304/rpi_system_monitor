#!/usr/bin/env python3

import psutil
import psycopg2

conn = psycopg2.connect("dbname=adam user=adam")
cur = conn.cursor()

# Getting the values in the beginning and in the end to get the average of them
cpuTemp = psutil.sensors_temperatures()['cpu-thermal'][0].current
memUsage = psutil.virtual_memory().used/1024/1024
diskUsage = psutil.disk_usage('/').used/1024/1024/1024
nasUsage = psutil.disk_usage('/mnt/nas').used/1024/1024/1024
devUsage = psutil.disk_usage('/mnt/dev').used/1024/1024/1024
cloudUsage = psutil.disk_usage('/mnt/cloud').used/1024/1024/1024

# Getting the percents first, because it takes multiple seconds to gather the information
cpuPercents = psutil.cpu_percent(interval=5, percpu=True)
cpu0Usage = cpuPercents[0]
cpu1Usage = cpuPercents[1]
cpu2Usage = cpuPercents[2]
cpu3Usage = cpuPercents[3]

# Calculating the values
cpuTemp = (psutil.sensors_temperatures()['cpu-thermal'][0].current + cpuTemp) / 2
memUsage = (psutil.virtual_memory().used/1024/1024 + memUsage) / 2
memTotal = psutil.virtual_memory().total/1024/1024
diskUsage = (psutil.disk_usage('/').used/1024/1024/1024 + diskUsage) / 2
diskTotal = psutil.disk_usage('/').total/1024/1024/1024
nasUsage = (psutil.disk_usage('/mnt/nas').used/1024/1024/1024 + nasUsage) / 2
nasTotal = psutil.disk_usage('/mnt/nas').total/1024/1024/1024
devUsage = (psutil.disk_usage('/mnt/dev').used/1024/1024/1024 + devUsage) / 2
devTotal = psutil.disk_usage('/mnt/dev').total/1024/1024/1024
cloudUsage = (psutil.disk_usage('/mnt/cloud').used/1024/1024/1024 + cloudUsage) / 2
cloudTotal = psutil.disk_usage('/mnt/cloud').total/1024/1024/1024

# For debugging
#print ("cpu temp   : {0: >8.2f}°C".format(cpuTemp))
#print ("cpu0 usage : {0: >8.2f}%".format(cpu0Usage))
#print ("cpu1 usage : {0: >8.2f}%".format(cpu1Usage))
#print ("cpu2 usage : {0: >8.2f}%".format(cpu2Usage))
#print ("cpu3 usage : {0: >8.2f}%".format(cpu3Usage))
#print ("mem usage  : {0: >8.2f}MB".format(memUsage))
#print ("mem total  : {0: >8.2f}MB".format(memTotal))
#print ("disk usage : {0: >8.2f}GB".format(diskUsage))
#print ("disk total : {0: >8.2f}GB".format(diskTotal))
#print ("nas usage  : {0: >8.2f}GB".format(nasUsage))
#print ("nas total  : {0: >8.2f}GB".format(nasTotal))
#print ("dev usage  : {0: >8.2f}GB".format(devUsage))
#print ("dev total  : {0: >8.2f}GB".format(devTotal))
#print ("cloud usage: {0: >8.2f}GB".format(cloudUsage))
#print ("cloud total: {0: >8.2f}GB".format(cloudTotal))

# Saving values to DB
cur.execute('INSERT INTO monitoring.rpi_data(cpu_temp_celsius,cpu0_usage_percent,cpu1_usage_percent,cpu2_usage_percent,cpu3_usage_percent,mem_usage_mb,mem_total_mb,sd_card_usage_gb,sd_card_total_gb,nas_usage_gb,nas_total_gb,dev_usage_gb,dev_total_gb,cloud_usage_gb,cloud_total_gb,timestamp) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,now());', (cpuTemp, cpu0Usage, cpu1Usage, cpu2Usage, cpu3Usage, memUsage, memTotal, diskUsage, diskTotal, nasUsage, nasTotal, devUsage, devTotal, cloudUsage, cloudTotal))
conn.commit()
cur.close()
conn.close()
