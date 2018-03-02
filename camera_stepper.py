"""
camera_stepper.py

Raspberry Pi code to run picamera and stepper motor for taking automated z-stacks on
a compoound fluorescence microscope.

Matt Rich, 03/2018

"""


import RPi.GPIO as GPIO
from picamera import Picamera

from argparse import ArgumentParser
import os, time


GPIO.setmode(GPIO.BOARD)

def step(clockwise, direction = 16, step = 12):
    
    #set pins to expect outputs from controller
    GPIO.setup(direction, GPIO.OUT)
    GPIO.setup(step, GPIO.OUT) 

    #set direction
    #clockwise = HIGH
    #counter-clockwise = LOW
    if clockwise:
        GPIO.output(direction, GPIO.HIGH)
    else:
        GPIO.output(direction, GPIO.LOW)

    #take step
    GPIO.output(step, GPIO.HIGH)
    GPIO.output(step, GPIO.LOW)

def image(camera, out_name):
	camera.capture(out_name, 'rgb')

def zstack(camera, prefix, steps):
	for i in range(steps):
		image(picam, "{1}_{2}.data".format(prefix, str(i)))
		step(True)
		
		#wait for step
		time.sleep(0.5)
	
if __name__ == "__main__":
    
	parser = ArgumentParser()
	##stepper arguments
	parser.add_argument("-s", "--steps", action = 'store', type = int, 
					dest = 'steps', help = "number of z-slices",
					default=20)
	parser.add_argument("-d", "--dir", action = "store", type = str, 
					dest = "direction", default = "up", 
					help = "direction of steps, up or down")

	#camera arguments
	parser.add_argument("-o", "--output", action = 'store', type = str,
					dest = "prefix", help = "prefix for image file naming")
	parser.add_argument("-f", "--output_folder", action = 'store', type = str,
					dest = "folder", help = "output folder to store image data", 
					default = "./")
	parser.add_argument("--ss", action = 'store', type = int, dest = "shutter",
					default = 400000, 
					help = "shutter speed in microseconds (def=400K)")
	parser.add_argument("--iso", action = 'store', type = int, dest = "iso",
					default = 800, help = "camera iso (def=800)")

	#other modes
	parser.add_argument("--set_focus", action - 'store_true', dest = "set_focus", 
					default = False, help = "set focus mode")

	args = parser.parse_args()

	#setup output folder
	try:
		os.mkdir(args.folder)
	except OSError:
		pass

	#initialize and set camera settings
	picam = Picamera()
	picam.iso = args.iso
	picam.shutter_speed = args.shutter

	###set gains/awb
	#sleep for 2 seconds to allow camera to warmup
	time.sleep(2)

#	picam.awb_mode = "off"	###manually set gains
#	picam.awb_gains = (1,1)	###set gains to red=1, blue=1 (this might need changing)

	#run mode
	if not set_focus:
		zstack(picam, args.prefix, s)

	picam.close()
