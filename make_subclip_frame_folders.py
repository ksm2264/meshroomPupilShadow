import glob
import sys
import os

scratch_dir = os.popen('echo $SCRATCH').read()[:-1]

fileList = glob.glob(scratch_dir+os.sep+'MonocularProject'+os.sep+sys.argv[1]+os.sep+'subclips'+os.sep+'*.mp4')

fileNames = [fileName.split(os.sep)[-1].split('.')[0] for fileName in fileList]

scratch_pref = scratch_dir+os.sep+'MonocularProject'+os.sep

for fileName in fileNames:
    os.mkdir(scratch_pref+sys.argv[1]+os.sep+'subclip_frames'+os.sep+fileName)
    clip_str_in = scratch_pref+sys.argv[1]+os.sep+'subclips'+os.sep+fileName+'.mp4'
    dest_folder = scratch_pref+sys.argv[1]+os.sep+'subclip_frames'+os.sep+fileName
    os.system('$WORK/ffmpeg -i {clip_in} {clip_out}/%00d.png'.format(clip_in=clip_str_in, clip_out = dest_folder))

