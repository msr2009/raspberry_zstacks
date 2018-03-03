"""
camera_stepper-stream.py

Raspberry Pi code to run picamera and stepper motor for taking automated z-stacks on
a compoound fluorescence microscope.

version for streaming to numpy array, then saving, rather than saving data
individually.

Matt Rich, 03/2018

"""


import RPi.GPIO as GPIO
from picamera import PiCamera
import numpy as np

from argparse import ArgumentParser
import os, time


GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)

def step(clockwise, n=1, direction = 16, step = 12):
    
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
    for i in range(n):   
        GPIO.output(step, GPIO.HIGH)
        GPIO.output(step, GPIO.LOW)
        time.sleep(.02)

def image(camera, out_name, data_mode, width=None, height=None):
	if not datamode: 
		camera.capture(out_name+".jpg")
		return None
	else:
		#make empty ndarray
		output = np.empty((res_x%32*32 * res_y%32*32 * 3,), dtype=np.uint8)
		camera.capture(output, "rgb")
		output = output.reshape((res_x%32*32, res_y%32*32, 3))
		return output[:res_x, :res_y, :]

def zstack(camera, prefix, folder, steps, data_mode):
	(res_x, res_y) = camera.resolution
	output_array = []

    for i in range(steps):
        output_array.append(image(
				picam, 
				"{0}{1}_{2}".format(folder, prefix, str(i+1)), 
				data_mode, 
				res_x, res_y))
        step(False)

	#save ndarray
	for arr in output_array:
		arr.tofile("{0}{1}_{2}.data".format(folder, prefix, str(i+1), "\t")
    	

if __name__ == "__main__":
    
    parser = ArgumentParser()
    ##stepper arguments
    parser.add_argument("-s", "--steps", action = 'store', type = int, 
                    dest = 'steps', help = "number of z-slices",
                    default=40)
    parser.add_argument("-d", "--dir", action = "store", type = str, 
                    dest = "direction", default = "up", 
                    help = "direction of steps, up or down")

    #camera arguments
    parser.add_argument("-o", "--output", action = 'store', type = str,
                    dest = "prefix", help = "prefix for image file naming")
    parser.add_argument("-f", "--output_folder", action = 'store', type = str,
                    dest = "folder", help = "output folder to store image data", 
                    default = "./tmp/")
    parser.add_argument("--ss", action = 'store', type = int, dest = "shutter",
                    default = 200000, 
                    help = "shutter speed in microseconds (def=400K)")
    parser.add_argument("--iso", action = 'store', type = int, dest = "iso",
                    default = 800, help = "camera iso (def=800)")

    #other modes
    parser.add_argument("--set_focus", action = 'store_true', dest = "set_focus", 
                    default = False, help = "set focus mode")
	parser.add_argument("--data", action = "store_true", dest = "datamode", 
					default = False, help = "save data instead of jpeg")

    args = parser.parse_args()

    #setup output folder
    try:
        os.mkdir(args.folder)
    except OSError:
        pass
        
    #initialize and set camera settings
    picam = PiCamera(framerate=10)
    picam.iso = args.iso

    ###set gains/awb
    #sleep for 2 seconds to allow camera to warmup
    #picam.start_preview(fullscreen=False, window=(100,200,640,480))
    picam.shutter_speed = args.shutter
    time.sleep(2)

    picam.exposure_mode = "off"

    picam.awb_mode = "off"  ###manually set gains
    picam.awb_gains = ((1.414,1.414))

    #run mode
    if not args.set_focus:
		zstack(picam, args.prefix, args.folder, args.steps, args.datamode)

    picam.close()
