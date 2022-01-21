import scipy.io as sio
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
from moviepy.editor import VideoFileClip
import sys
import os


scratch_dir = os.popen('echo $SCRATCH').read()[:-1]

mat = sio.loadmat(scratch_dir+os.sep+'MonocularProject'+os.sep+sys.argv[1]+os.sep+'allWalks_n.mat',squeeze_me=True,struct_as_record=False)

vid_str_in = scratch_dir+os.sep+'MonocularProject'+os.sep+sys.argv[1]+os.sep+'world.mp4'

vid_dir_out = scratch_dir+os.sep+'MonocularProject'+os.sep+sys.argv[1]+os.sep+'subclips'


clip = VideoFileClip(vid_str_in)

rate = clip.subclip(0,7).fps

for idx,walk in enumerate(list(mat['allWalks'])):
    
    frame_start = walk.worldFrameIndex[0]/rate
    frame_end = walk.worldFrameIndex[-1]/rate
    
    ffmpeg_extract_subclip(vid_str_in,frame_start,frame_end,vid_dir_out+os.sep+str(idx)+'.mp4')
    
    
