import numpy as np
import cv2
from PIL import Image
import tesserocr
from sys import argv

cap = cv2.VideoCapture(argv[1]) #open the video file which is supplied as an arg

last_frameid = 0

def processframe(frame, frameid): #get frame and frameid
    global last_frameid
    image = Image.fromarray(frame) #make image variable so tesserocr can process it
    str_out = tesserocr.image_to_text(image) #extract strings from the image
    if "wins" in str_out: #if string contains wins
        #this function is implemented to avoid printing same map + winner info again. 
        #if current frame id is 500 frames after the last valid frame we examined, then continue
        if (frameid-last_frameid) > 500:
            final_output = "" 
            #cut strings into lines and process each line.
            #First line is always a map. player info is next like or one after that
            for line in str_out.splitlines():
                line = line.strip() #clean up the line
                if len(line) > 3: #if line contains more than 3 chars
                    if ("wins" in line) and ("Player" in line): #if the line contains wins and player
                        #tesserocr does a good job at recognizing MrNFEN but not MrSparkle's name. 
                        #This just looks for 3 chars and replaces the line
                        if "MrN" in line: 
                            line = "MrNFEN"
                        if "MrS" in line:
                            line = "MrSparkles"
                        final_output = final_output + "\t" + line + "\t" + argv[1] #set the final output
                        #Sometimes, map name isn't obtained but information about winner is.
                        #this is implemented so we continue if map name is obtained
                        if len(final_output.split("\t")[0]) > 0:
                            last_frameid = frameid #since this is a valid frame we processed, set the last_frameid to this frame's id
                            print final_output.encode('utf-8')
                            break
                    #if line is more than 3 chars and is not winning line, 
                    #then it's probably the map name or something empty or random
                    if "wins" not in line: 
                        final_output = line #set final_output to whatever the line is

i = 0 #temp frame counter
frameid = 0 #total frame counter
while(cap.isOpened()):
    ret, frame = cap.read() #read a frame
    i = i+1 #count frames
    frameid = frameid + 1 #count total frames
    if (i==100 and ret==True): #if # of frames went by are 50
        i=0 #set frames to 0 again
        #cropping based on input video: 1080p 400x700, 720p 230x400, 480p 150x300
        cropped = frame[0:250, 0:400]
        processframe(cropped,frameid)
    elif (ret==False):
        break

cap.release()
