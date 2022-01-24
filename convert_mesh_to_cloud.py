import glob
import sys
import os

subj_name = sys.argv[1]
scratch_dir = os.popen('echo $SCRATCH').read()[:-1]


base_dir = scratch_dir+os.sep+'MonocularProject'+os.sep+subj_name+os.sep+'meshroom_output'+os.sep

obj_list = glob.glob(base_dir+'*'+os.sep+'Texturing'+os.sep+'*'+os.sep+'texturedMesh.obj')

ply_list = [obj[:-4]+'.ply' for obj in obj_list]

for ply,obj in zip(ply_list,obj_list):
    if not os.path.exists(ply):
        os.system('flatpak run --user --env=QT_QPA_PLATFORM=offscreen org.cloudcompare.CloudCompare -SILENT -AUTO_SAVE OFF -O {obj_in} -SAMPLE_MESH POINTS 10000000 -C_EXPORT_FMT PLY -SAVE_CLOUDS FILE {ply_out}'.format(obj_in=obj, ply_out=ply))
