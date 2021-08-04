# Make_MP4_VFR
To make a constant frame rate MP4 video into a variable frame rate.   
# What type of video is available?
Currently, this script is designed for a video generated from OpenCV-Python libraly.  So, you need some modification to use it for other MP4.
# How to use?
At first, you need to prepare `timecodes.txt`, which has time-stamp data for each frame in timecodes_v2 format.  
Here is an example;  
```
0
20
50
70
100
...
```  
In this case, each frame will be played like 1st frame at 0 ms, 2nd frame at 20 ms, 3rd frame at 50 ms, ... .  And, the gap between 2 frames will be the displayed duration for the first one.


Next, please edit first 3 lines accorfing to your files.  These lines are like below;  
```
videoFilename = './video.mp4'
outputFilename = './testVFR.mp4'
timecodesFilename = './timecodes.txt'
```  
, where `videoFilename` is a path to MP4 video, `outputFilename` is a path for result MP4, and `timecodesFilename` is the one you made. Please note the number of timecodes in `timecodes.txt` has to be same as frames in your video.


Finally, you can run this script! Run `python EditMP4.py`, you will get result!

# Tested situation
I used `https://github.com/AiueoABC/CompressedVideoGenerationExample` to generate video for this.
