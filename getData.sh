#!/bin/bash

mkdir $SCRATCH/MonocularProject/${1}
$WORK/rclone-*/rclone copy remote:BerkeleyDataBackup/${1}/Monocular/Pupil/world_undistorted.mp4 $SCRATCH/MonocularProject/${1}/ --progress --drive-shared-with-me
mv $SCRATCH/MonocularProject/${1}/world_undistorted.mp4 $SCRATCH/MonocularProject/${1}/world.mp4
$WORK/rclone-*/rclone copy remote:BerkeleyDataBackup/${1}/OutputFiles/Monocular_allWalks.mat $SCRATCH/MonocularProject/${1}/ --progress --drive-shared-with-me
mkdir $SCRATCH/MonocularProject/${1}/subclips
mkdir $SCRATCH/MonocularProject/${1}/subclip_frames
mkdir error_logs all_jobscripts output_logs overrides
