#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 24 14:23:42 2022

@author: karl
"""

import sys
from align_utils import getSubjWalkList, getMeshroomData, applyOptimalRotation, alignPupilShadowMesh, computeGazeXYZ, saveMatFile, proc_this_walk

this_subj_name = sys.argv[1]
#this_subj_name = 'JAC'

subjWalkList = getSubjWalkList(this_subj_name)


for subjWalkDir in subjWalkList:

    skip_rest=False
    if proc_this_walk(subjWalkDir):
        try:
            points,cens,rotms = getMeshroomData(subjWalkDir)
        except:
            skip_rest=True
        
        if not skip_rest:
            try:
                points,cens,orig2alignedMat = applyOptimalRotation(points,cens,rotms,subjWalkDir)
                pupilShadowMeshMat_dict = alignPupilShadowMesh(points,cens,rotms,subjWalkDir,orig2alignedMat)
                pupilShadowMeshMat_dict = computeGazeXYZ(pupilShadowMeshMat_dict,subjWalkDir)

                saveMatFile(pupilShadowMeshMat_dict,subjWalkDir)
            except:
                pass
