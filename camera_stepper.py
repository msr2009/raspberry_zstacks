"""
camera_stepper.py

Raspberry Pi code to run picamera and stepper motor for taking automated z-stacks on
a compoound fluorescence microscope.

Matt Rich, 03/2018

"""


import RPi.GPIO as GPIO
from picamera import PiCamera

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

def image(camera, out_name):
    #camera.capture(out_name, 'rgb')
    camera.capture(out_name)

def zstack(camera, prefix, folder, steps):

    for i in range(steps):
        image(picam, "{0}{1}_{2}.jpg".format(folder, prefix, str(i)))
        step(False)
    
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
                    default = 400000, 
                    help = "shutter speed in microseconds (def=400K)")
    parser.add_argument("--iso", action = 'store', type = int, dest = "iso",
                    default = 800, help = "camera iso (def=800)")

    #other modes
    parser.add_argument("--set_focus", action = 'store_true', dest = "set_focus", 
                    default = False, help = "set focus mode")

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
    picam.shutter_speed = 200000
    time.sleep(2)

    picam.exposure_mode = "off"

    picam.awb_mode = "off"  ###manually set gains
    picam.awb_gains = ((1.414,1.414))

    #run mode
    if not args.set_focus:
        zstack(picam, args.prefix, args.folder, 30)

    picam.close()
