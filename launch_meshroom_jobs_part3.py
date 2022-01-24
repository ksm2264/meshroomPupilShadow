import glob
import sys
import os

scratch_dir = os.popen('echo $SCRATCH').read()[:-1]

fileList = glob.glob(scratch_dir+os.sep+'MonocularProject'+os.sep+sys.argv[1]+os.sep+'subclips'+os.sep+'*.mp4')

fileNames = [fileName.split(os.sep)[-1].split('.')[0] for fileName in fileList]

scratch_pref = scratch_dir+os.sep+'MonocularProject'+os.sep

exclude_list = []                                                                                     
                                                                                                      
has_mesh_list = glob.glob(scratch_pref+sys.argv[1]+os.sep+'meshroom_output'+os.sep+'*'+os.sep+'Texturing'+os.sep+'*')                                                                                       
                                                                                                      
has_mesh_list = [this_item.split(os.sep)[7] for this_item in has_mesh_list]                           
                                                                                                      
for fileName in fileNames:                                                                            
    if fileName in has_mesh_list:                                                                     
        exclude_list.append(fileName)                                                                 
                                                                                                      
                                                                                                      
fileNames = [fileName for fileName in fileNames if fileName not in exclude_list]
for fileName in fileNames:
    this_js = sys.argv[1]+'_'+fileName+'_p3_js'
    os.system('cp pattern_jobscripts/part3_js all_jobscripts/{JS}'.format(JS=this_js))
    os.system('sed -i "s/SUBJ/{SUBJ}/g" all_jobscripts/{JS}'.format(SUBJ=sys.argv[1],JS=this_js))
    os.system('sed -i "s/WALKNUM/{WALKNUM}/g" all_jobscripts/{JS}'.format(WALKNUM=fileName,JS=this_js))
    os.system('sbatch all_jobscripts/{JS}'.format(JS=this_js))
