#!/bin/bash

mkdir $SCRATCH/MonocularProject/${1}
$WORK/rclone-*/rclone copy remote:BerkeleyDataBackup/${1}/Monocular/Pupil/world_undistorted.mp4 $SCRATCH/MonocularProject/${1}/ --progress
mv $SCRATCH/MonocularProject/${1}/world_undistorted.mp4 $SCRATCH/MonocularProject/${1}/world.mp4
$WORK/rclone-*/rclone copy remote:BerkeleyDataBackup/${1}/Monocular/allWalks_n.mat $SCRATCH/MonocularProject/${1}/ --progress
mkdir $SCRATCH/MonocularProject/${1}/subclips
mkdir $SCRATCH/MonocularProject/${1}/subclip_frames
mkdir error_logs output_logs overrides all_jobscripts
