import glob
import sys
import os

scratch_dir = os.popen('echo $SCRATCH').read()[:-1]

fileList = glob.glob(scratch_dir+os.sep+'MonocularProject'+os.sep+sys.argv[1]+os.sep+'subclips'+os.sep+'*.mp4')

fileNames = [fileName.split(os.sep)[-1].split('.')[0] for fileName in fileList]

scratch_pref = scratch_dir+os.sep+'MonocularProject'+os.sep

for fileName in fileNames:
    this_js = sys.argv[1]+'_'+fileName+'_js'
    os.system('cp pattern_jobscripts/part1_js all_jobscripts/{JS}'.format(JS=this_js))
    os.system('sed -i "s/SUBJ/{SUBJ}/g" all_jobscripts/{JS}'.format(SUBJ=sys.argv[1],JS=this_js))
    os.system('sed -i "s/WALKNUM/{WALKNUM}/g" all_jobscripts/{JS}'.format(WALKNUM=fileName,JS=this_js))
    os.system('sbatch all_jobscripts/{JS}'.format(JS=this_js))
