#!/bin/bash

tar -czvf ${1}_mesh_data.tar.gz ${SCRATCH}/MonocularProject/${1}/meshroom_output/*/Texturing/*/* ${SCRATCH}/MonocularProject/${1}/meshroom_output/*/StructureFromMotion/*/cameras.sfm
${WORK}/rclone*/rclone copy ${1}_mesh_data.tar.gz  remote:Monocular_Berkeley_Mesh/ --progress --drive-shared-with-me
tar -czvf ${1}_mat_file.tar.gz ${SCRATCH}/MonocularProject/${1}/meshroom_output/*/pupilShadowMesh.mat 
${WORK}/rclone*/rclone copy ${1}_mat_file.tar.gz remote:Monocular_Berkeley_Mesh/ --progress --drive-shared-with-me
