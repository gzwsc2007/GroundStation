import pickle
import datetime
import time
import csv


f = open("log_2014-07-02_11_55_11.pkl", 'r')
L = pickle.load(f)

csvFile = open("myCSV.csv", "wb")
fieldnames = L[0][1].keys()
#writer = csv.DictWriter(csvFile, fieldnames, extrasaction='ignore')
writer = csv.writer(csvFile, delimiter=',')

tZero = L[0][0]

writer.writerow(["time", "airspeed"])
for item in L:
	time, d = item
	time -= tZero
	writer.writerow([time, d["airspeed"]])