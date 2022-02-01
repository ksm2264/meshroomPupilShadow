#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 24 14:23:50 2022

@author: karl
"""

import glob
import os
import open3d as o3d
import numpy as np
import json
import scipy.io as sio
import pandas as pd
from scipy.spatial.transform import Rotation as R
from scipy.optimize import minimize
from sklearn.neighbors import KDTree

scratch_dir = os.popen('echo $SCRATCH').read()[:-1]
work_dir = os.popen('echo $WORK').read()[:-1]

#base_dir = '/home/karl/meshroomPupilShadow_on_TACC/dev_mesh_align_step/data/'
base_dir = scratch_dir+os.sep+'MonocularProject'+os.sep
blend_base_dir = work_dir+'/meshroomPupilShadow/'
blender_exec_path = 'flatpak run --user --env=QT_QPA_PLATFORM=offscreen org.blender.Blender'

FL = 2100/2.3232
head_marker_idx = 26
l_foot_idx = 6
r_foot_idx = 11
n_scale_factors = 100

def proc_this_walk(subjWalkDir):
    
    return not os.path.exists(subjWalkDir+os.sep+'pupilShadowMesh.mat') and len(glob.glob(subjWalkDir+os.sep+'Texturing'+os.sep+'*'+os.sep+'texturedMesh.ply'))>0

def accumarray(index,value,agg_func):
    

    df = pd.DataFrame({"y":value,"x":index})
    new_val=pd.pivot_table(df,values='y',index='x',aggfunc=agg_func)
    
    return np.array(new_val)[:,0]

def normr(n_by_m):
    
    return n_by_m/np.linalg.norm(n_by_m,ord=2,axis=1)[:,None]
    

def rotErrorMats(euls,mat_A,mat_B):
    
    r = R.from_euler('XYZ',euls).as_matrix()

    mat_A = np.stack([np.matmul(mat,r) for mat in list(mat_A)])
    
    return np.linalg.norm(mat_A-mat_B)

    
def rotErrorVecs(euls,mat_A,mat_B):
    
    r = R.from_euler('XYZ',euls).as_matrix()
    
    mat_A = np.matmul(mat_A,r)
    
    return np.linalg.norm(mat_A-mat_B)

def getOptimRotation(mat_A,mat_B):
    
    if len(mat_A.shape)==3:
        euls = minimize(rotErrorMats,[0,0,0],args=(mat_A,mat_B)).x
    else:
        euls = minimize(rotErrorVecs,[0,0,0],args=(mat_A,mat_B)).x

    
    return R.from_euler('XYZ',euls).as_matrix()
    

def getSubjWalkList(subj_name):
    subjWalkList=glob.glob(base_dir+subj_name+os.sep+'meshroom_output'+os.sep+'*'+os.sep+'Texturing/')
    
    subjWalkList = ['/'.join(thisVal.split('/')[:-2]) for thisVal in subjWalkList]
    
    return subjWalkList

def getCensRotms(json_path):
    
    with open(json_path) as f:
        data = json.load(f)
        
    poses = data['poses']
    views = data['views']
    
    frame_nums = [view['path'].split(os.sep)[-1].split('.')[0] for view in views]
    frame_nums = [int(fr) for fr in frame_nums]
    order_idx = np.argsort(frame_nums)
    
    cens = [pose['pose']['transform']['center'] for pose in poses]
    cens = np.stack([np.stack([np.float(val) for val in cen]) for cen in cens])
    
    rotms = [pose['pose']['transform']['rotation'] for pose in poses]
    rotms = np.stack([np.reshape(np.stack([np.float(val) for val in rotm]),(3,3)) for rotm in rotms])
    rotms = np.stack([np.transpose(rotm) for rotm in list(rotms)])

    cens = cens[order_idx]
    rotms = rotms[order_idx]

    return cens,rotms

def getMeshroomData(subjWalkDir):
    print(subjWalkDir)
    ply_path = glob.glob(subjWalkDir+os.sep+'Texturing'+os.sep+'*'+os.sep+'texturedMesh.ply')[0]
    sfm_path = glob.glob(subjWalkDir+os.sep+'StructureFromMotion'+os.sep+'*'+os.sep+'cameras.sfm')[0]
    
    pc_array =np.asarray(o3d.io.read_point_cloud(ply_path).points)
    cens,rotms = getCensRotms(sfm_path)
    
    return pc_array,cens,rotms

def applyOptimalRotation(pc_array,cens,rotms,subjWalkDir):
    
    
    allWalks = sio.loadmat(subjWalkDir+'/../../Monocular_allWalks.mat',struct_as_record=False,squeeze_me=True)['allWalks']
    walkNum = int(subjWalkDir.split(os.sep)[-1])
    thisWalk = allWalks[walkNum]
    
    hx = thisWalk.headVecX_fr_xyz
    hy = thisWalk.headVecY_fr_xyz
    hz = thisWalk.headVecZ_fr_xyz
    
    index = thisWalk.worldFrameIndex
    index = index-index[0]
    
    hx_ds = np.zeros((index[-1]+1,3))
    hy_ds = np.zeros((index[-1]+1,3))
    hz_ds = np.zeros((index[-1]+1,3))
    
    for dim in range(3):
        hx_ds[:,dim] = accumarray(index,hx[:,dim],np.mean)
        hy_ds[:,dim] = accumarray(index,hy[:,dim],np.mean)
        hz_ds[:,dim] = accumarray(index,hz[:,dim],np.mean)
        
    if len(cens)<len(hx_ds):
        hx_ds = hx_ds[:-1]
        hy_ds = hy_ds[:-1]
        hz_ds = hz_ds[:-1]
        
    shadow_rotms = np.zeros((cens.shape[0],3,3))
    shadow_rotms[:,0,:] = hx_ds
    shadow_rotms[:,1,:] = hy_ds
    shadow_rotms[:,2,:] = hz_ds
    
    
    
    porX = thisWalk.gaze_norm_pos_x*1920
    porY = (1-thisWalk.gaze_norm_pos_y)*1080


    imageBasedEyeVec = np.transpose(np.array((FL*np.ones(porX.shape[0]),porY-1080/2,porX-1920/2)));
    imageBasedEyeVec[:,1] = -imageBasedEyeVec[:,1];
    imageBasedEyeVec = normr(imageBasedEyeVec)
    
    
      
    
    try:
        shadow_coord_eyeVec=normr(thisWalk.lGazeXYZ-thisWalk.lEyeballCenterXYZ)
    except:
        shadow_coord_eyeVec=normr(thisWalk.rGazeXYZ-thisWalk.rEyeballCenterXYZ)
    
    #shadow_coord_eyeVec = np.mean(np.stack([lGaze,rGaze],axis=2),axis=2)
    #shadow_coord_eyeVec = normr(shadow_coord_eyeVec)
    
    shadow_coord_eyeVec_ds = np.zeros((index[-1]+1,3))
    
    for dim in range(3):
        shadow_coord_eyeVec_ds[:,dim] = accumarray(index,shadow_coord_eyeVec[:,dim],np.mean)
    
    if len(cens)<len(imageBasedEyeVec):
        imageBasedEyeVec = imageBasedEyeVec[:-1]
        shadow_coord_eyeVec_ds = shadow_coord_eyeVec_ds[:-1]
    
    rotms[:,(0,2),:] = rotms[:,(2,0),:]
    rotms[:,1,:] = -rotms[:,1,:]    
    
    shadow_head_2_meshroom_head_rotm = getOptimRotation(shadow_rotms,rotms)
    
    meshroomEyeVec = np.zeros((rotms.shape[0],3))
    
    for idx in range(meshroomEyeVec.shape[0]):
        meshroomEyeVec[idx] =np.matmul(imageBasedEyeVec[idx],rotms[idx])
    


    almostMeshroom=np.matmul(shadow_coord_eyeVec_ds,np.transpose(shadow_head_2_meshroom_head_rotm))

    rotm_additional = getOptimRotation(almostMeshroom,meshroomEyeVec)

    orig2alignedMat = np.matmul(np.transpose(rotm_additional),shadow_head_2_meshroom_head_rotm)

    pc_array = np.matmul(pc_array,orig2alignedMat)
    cens = np.matmul(cens,orig2alignedMat)
    
    return pc_array,cens,orig2alignedMat



def alignPupilShadowMesh(pc_array,cens,rotms,subjWalkDir,orig2alignedMat):
    
    tree_XYZ = KDTree(pc_array)
    tree_XZ = KDTree(pc_array[:,(0,2)])
    allWalks = sio.loadmat(subjWalkDir+'/../../Monocular_allWalks.mat',struct_as_record=False,squeeze_me=True)['allWalks']
    walkNum = int(subjWalkDir.split(os.sep)[-1])
    thisWalk = allWalks[walkNum]
    wfi = thisWalk.worldFrameIndex
    wfi = wfi - wfi[0]
    steps = thisWalk.steps_HS_TO_StanceLeg_XYZ
    
    shadow = thisWalk.shadow_fr_mar_dim
    
    
    
    shadow_ds = np.zeros((wfi[-1]+1,shadow.shape[1],shadow.shape[2]))

    for dim_marker in range(shadow.shape[1]):
        for dim in range(3):
            shadow_ds[:,dim_marker,dim] = accumarray(wfi,shadow[:,dim_marker,dim],np.mean)

    if len(shadow_ds)>len(cens):
        shadow_ds = shadow_ds[:-1]
            

    for dim_marker in range(shadow.shape[1]):
        shadow_ds[:,dim_marker,:] = shadow_ds[:,dim_marker,:] - shadow_ds[:,head_marker_idx,:] + cens
        

    l_contact_idx = steps[steps[:,2]==2,0].astype(int)
    l_contact_idx_ds = wfi[l_contact_idx]
    
    r_contact_idx = steps[steps[:,2]==1,0].astype(int)
    r_contact_idx_ds = wfi[r_contact_idx]

    l_foot_contacts = shadow_ds[l_contact_idx_ds,l_foot_idx,:]
    r_foot_contacts = shadow_ds[r_contact_idx_ds,r_foot_idx,:]
    
    cen_at_planted = np.concatenate((cens[l_contact_idx_ds],cens[r_contact_idx_ds]),axis=0)

    footLocs = np.concatenate((l_foot_contacts,r_foot_contacts))
    
    
    feetLoc_left =  shadow_ds[:,l_foot_idx,:]
    feetLoc_right =  shadow_ds[:,r_foot_idx,:]
    
    left_height = feetLoc_left[:,1]
    right_height = feetLoc_right[:,1]
    
    shadow_height = np.max(np.concatenate(((cens[:,1]-left_height)[:,None],(cens[:,1]-right_height)[:,None]),axis=1),axis=1)
    _,cam_nearest_idx = tree_XZ.query(cens[:,(0,2)])
    camCenHeight = cens[:,1][:,None]-pc_array[cam_nearest_idx,1]
    
    
    scaleFac_init = np.mean(np.divide(camCenHeight,shadow_height))
    
    
    scaleFacs = np.linspace(0.8*scaleFac_init,1.2*scaleFac_init,n_scale_factors)
    summed_dists=[]
    for s_idx,scaleFac in enumerate(list(scaleFacs)):
       	
        D,kidx= tree_XYZ.query((footLocs-cen_at_planted)*scaleFac+cen_at_planted)
        
        summed_dists.append(np.sum(D))
        
    
    mindex= np.argmin(summed_dists)
    scaleFac = scaleFacs[mindex]
    
    shadow_out = np.zeros((cens.shape[0],shadow.shape[1],shadow.shape[2]))
    
    for dim_marker in range(shadow.shape[1]):
        shadow_out[:,dim_marker,:] = (shadow_ds[:,dim_marker,:]-cens)*scaleFac+cens
    
    shadow = shadow_out
    
    footLocs = np.zeros((steps.shape[0],3))
    _,l_foot_kidx = tree_XYZ.query(shadow[l_contact_idx_ds,l_foot_idx,:])
    _,r_foot_kidx = tree_XYZ.query(shadow[r_contact_idx_ds,r_foot_idx,:])
    footLocs[steps[:,2]==2] = pc_array[l_foot_kidx][:,0,:]
    footLocs[steps[:,2]==1] = pc_array[r_foot_kidx][:,0,:]

    step_frame_plantfoot_xyz = np.zeros((footLocs.shape[0],5))
    step_frame_plantfoot_xyz[steps[:,2]==2,0] = l_contact_idx_ds
    step_frame_plantfoot_xyz[steps[:,2]==1,0] = r_contact_idx_ds
    step_frame_plantfoot_xyz[steps[:,2]==2,1] = 1
    step_frame_plantfoot_xyz[steps[:,2]==1,1] = 2
    step_frame_plantfoot_xyz[:,2:] = footLocs
    
    return {'shadow':shadow,'step_frame_plantfoot_xyz':step_frame_plantfoot_xyz,'cens':cens,'orig2alignedMat':orig2alignedMat}


def getGazeFromBlender(pack_path):
    dummy_blend_file = blend_base_dir+'foo.blend'
    py_script_file = blend_base_dir+'intersectGazeBlender.py'
    os.system('{blender_exec} {dummy_blend_file} --background --python {py_script_file} {pack_path}'
              .format(blender_exec=blender_exec_path, dummy_blend_file=dummy_blend_file,
              py_script_file=py_script_file,pack_path=pack_path))
    gazeXYZ = np.load(pack_path.split('.npy')[0]+'_out.npy')
    
    return gazeXYZ

def computeGazeXYZ(pupilShadowMeshMat_dict,subjWalkDir):
    allWalks = sio.loadmat(subjWalkDir+'/../../Monocular_allWalks.mat',struct_as_record=False,squeeze_me=True)['allWalks']
    walkNum = int(subjWalkDir.split(os.sep)[-1])
    thisWalk = allWalks[walkNum]
    index = thisWalk.worldFrameIndex
    index = index-index[0]
    
    try:
        shadow_coord_eyeVec=normr(thisWalk.lGazeXYZ-thisWalk.lEyeballCenterXYZ)
    except:
        shadow_coord_eyeVec=normr(thisWalk.rGazeXYZ-thisWalk.rEyeballCenterXYZ)
    
    #shadow_coord_eyeVec = np.mean(np.stack([lGaze,rGaze],axis=2),axis=2)
    #shadow_coord_eyeVec = normr(shadow_coord_eyeVec)
    
    shadow_coord_eyeVec_ds = np.zeros((index[-1]+1,3))
    
    for dim in range(3):
        shadow_coord_eyeVec_ds[:,dim] = accumarray(index,shadow_coord_eyeVec[:,dim],np.mean)
        
    
        
    
    
    objPath = glob.glob(subjWalkDir+os.sep+'Texturing'+os.sep+'*'+os.sep+'texturedMesh.obj')[0]
    orig2alignedMat = pupilShadowMeshMat_dict['orig2alignedMat']
    cens = pupilShadowMeshMat_dict['cens']
    
    if len(cens)<len(shadow_coord_eyeVec_ds):
        shadow_coord_eyeVec_ds = shadow_coord_eyeVec_ds[:-1]
    gazeVec = normr(shadow_coord_eyeVec_ds)
    
    np.save(subjWalkDir+os.sep+'blender_pack.npy',{'cens':cens,'gazeVec':gazeVec,'objPath':objPath,'orig2alignedMat':orig2alignedMat})
    pack_path = subjWalkDir+os.sep+'blender_pack.npy'
    
    gazeXYZ = getGazeFromBlender(pack_path)
    
    
    pupilShadowMeshMat_dict['gazeXYZ']=gazeXYZ
    pupilShadowMeshMat_dict['gazeVec']=gazeVec
    
    return pupilShadowMeshMat_dict
    
        
def saveMatFile(pupilShadowMeshMat_dict,subjWalkDir):
    sio.savemat(subjWalkDir+os.sep+'pupilShadowMesh.mat',pupilShadowMeshMat_dict)
    
    return None

