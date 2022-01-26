import numpy as np
import bpy
import mathutils
import sys

meshes = bpy.data.meshes
for mesh in meshes:
    meshes.remove(mesh,do_unlink=True)

print(sys.argv)

pack_path = sys.argv[-1]

loadStruct = np.load(pack_path,allow_pickle=True).item()

cens = loadStruct['cens']
eyeVec = loadStruct['gazeVec']
orig2alignMat = loadStruct['orig2alignedMat']
objPath = loadStruct['objPath']

probe = bpy.ops.import_scene.obj(filepath=objPath)
obj = bpy.context.selected_objects[0]


#set_mat = np.array(obj.matrix_world)
#set_mat[:3,:3] = np.transpose(orig2alignMat)
#obj.matrix_world=mathutils.Matrix(set_mat)

intersectPoints = np.zeros(eyeVec.shape)

for idx in range(eyeVec.shape[0]):
    print(idx/eyeVec.shape[0])
    cast = obj.ray_cast(np.matmul(cens[idx],np.transpose(orig2alignMat)),np.matmul(eyeVec[idx],np.transpose(orig2alignMat)))
    coords = cast[1]
    coords = np.matmul(coords,orig2alignMat)
    intersectPoints[idx]=coords
    
np.save(pack_path.split('.npy')[0]+'_out.npy',intersectPoints)