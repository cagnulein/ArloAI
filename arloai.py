from influxdb import InfluxDBClient
import os
import re
import datetime
import calendar
import warnings
import logging
from imageai.Detection import VideoObjectDetection
import os
from arlo import Arlo
import pytz
tz = pytz.timezone('Europe/Rome')

from datetime import timedelta, date
import sys

######### Variables ############

influxhost = "$INFLUXHOST"		#CHANGEME
influxport = "$INFLUXPORT"		#CHANGEME
influxuser = "$INFLUXUSER"		#CHANGEME
influxpassword = "$INFLUXPASSWORD"	#CHANGEME
influxdbname = "$DBARLO"		#CHANGEME
USERNAME = '$ARLOUSERNAME'		#CHANGEME
PASSWORD = '$ARLOPASSWORD'		#CHANGEME

fluxdb = InfluxDBClient(influxhost, influxport, influxuser, influxpassword, influxdbname)

videoinfo = None
datevideo = datetime.datetime.now()

def forSeconds(output_arrays, count_arrays, average_output_count):
	global datevideo
	global videoinfo
	try:
		count=0
		for i in average_output_count:
			count+=1
			json_body = [
			{
				"measurement": "motion",
				"time": datevideo,
				"tags": { "camera": videoinfo['deviceId'], "objects": "yes"  },
				"fields": {
					i: "1",
					"videoid": videoinfo['uniqueId']
				}
			}]
			fluxdb.write_points(json_body)
		if(count==0):
			json_body = [
			{
				"measurement": "motion",
				"time": datevideo,
				"tags": { "camera": videoinfo['deviceId'], "objects": "no"  },
				"fields": {
					"videoid": videoinfo['uniqueId']
				}
			}]
			fluxdb.write_points(json_body)

	except Exception as e:
		print(e)


execution_path = os.getcwd()

fluxdb.create_database(influxdbname)

detector = VideoObjectDetection()
#detector.setModelTypeAsRetinaNet()
detector.setModelTypeAsTinyYOLOv3()
#detector.setModelPath( os.path.join(execution_path , "resnet50_coco_best_v2.0.1.h5"))
detector.setModelPath( os.path.join(execution_path , "yolo-tiny.h5"))
detector.loadModel(detection_speed="flash")

try:
	# Instantiating the Arlo object automatically calls Login(), which returns an oAuth token that gets cached.
	# Subsequent successful calls to login will update the oAuth token.
	arlo = Arlo(USERNAME, PASSWORD)
	# At this point you're logged into Arlo.

	today = (date.today()-timedelta(days=0)).strftime("%Y%m%d")
	seven_days_ago = (date.today()-timedelta(days=7)).strftime("%Y%m%d")

	# Get all of the recordings for a date range.
	library = arlo.GetLibrary(today, today)

	# Iterate through the recordings in the library.
	for recording in library:
		videoinfo = recording
		datevideo = datetime.datetime.fromtimestamp(int(recording['name'])//1000, pytz.timezone("UTC")).strftime('%Y-%m-%d %H:%M:%S')
		videofilename = datetime.datetime.fromtimestamp(int(recording['name'])//1000).strftime('%Y-%m-%d %H-%M-%S') + ' ' + recording['uniqueId'] + '.mp4'
		##
		# The videos produced by Arlo are pretty small, even in their longest, best quality settings,
		# but you should probably prefer the chunked stream (see below). 
		###    
		#    # Download the whole video into memory as a single chunk.
		#    video = arlo.GetRecording(recording['presignedContentUrl'])
		#	 with open('videos/'+videofilename, 'wb') as f:
		#        f.write(video)
		#        f.close()
		# Or:
		#
		# Get video as a chunked stream; this function returns a generator.
		if(os.path.isfile('videos/'+videofilename)==False):
			stream = arlo.StreamRecording(recording['presignedContentUrl'])
			with open('videos/'+videofilename, 'wb') as f:
				for chunk in stream:
					f.write(chunk)
				f.close()

			print('Downloaded video '+videofilename+' from '+recording['createdDate']+'.')

			print(os.path.join(execution_path , 'videos/'+videofilename))
			detections = detector.detectObjectsFromVideo(input_file_path=os.path.join(execution_path , 'videos/'+videofilename), frames_per_second=25, minimum_percentage_probability=50, save_detected_video=False, video_complete_function=forSeconds )

#		print(detections)
#		count=0
#		for eachObject in detections[1]:
#		    #print(eachObject["name"] , " : " , eachObject["percentage_probability"] )
#		    count+=1
#		    print("oggetto {0}".format(count))
#		    print(eachObject)

except Exception as e:
    print(e)