#!/bin/bash

tar -czvf ${1}.tar.gz ${SCRATCH}/MonocularProject/${1}/meshroom_output/*/Texturing/*/* ${SCRATCH}/MonocularProject/${1}/meshroom_output/*/StructureFromMotion/*/cameras.sfm
${WORK}/rclone*/rclone copy ${1}.tar.gz remote:Monocular_Berkeley_Mesh/ --progress
