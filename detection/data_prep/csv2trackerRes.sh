##instruction:
# $1: the name of the folder; ex:7-2021-07-22-17-26-56-RS-32-Data
# $2: the number of sequence; ex:seq07 note!:must prefix with "seq"
# note!!: if you want to re-run one sequence, you must delete data of this sequence in trackInput!!!!!

# you can change the path below to store in other path 


source /home/lion/anaconda3/etc/profile.d/conda.sh
#from csv to pcd
cd ~/Mylidar
conda activate yyz
python3 loadtypicalCSV.py --seq $1
#from pcd to bin
cd pcd2bin-master/
conda activate pcd2bin2
python pcd2bin.py --pcd_path /media/lion/Elements\ SE/Exp0722/pcd/$2 --bin_path /media/lion/Elements\ SE/Exp0722/bin/$2 --file_name $2
#from bin to 3d detection
conda activate YX
cd ~/Mylidar/OpenPCDet/tools/
python demo.py --cfg_file cfgs/kitti_models/pv_rcnn.yaml --ckpt pv_rcnn_8369.pth --data_path /media/lion/Elements\ SE/Exp0722/bin/$2 --seq $2
#from 3d detection to tracker
cd ~/Mylidar/Tracking/AB3DMOT/
conda activate AB3DMOT
mkdir ~/Mylidar/Tracking/AB3DMOT/data/KITTI/$2
cp /media/lion/Elements\ SE/Exp0722/trackerInput/$2.txt ~/Mylidar/Tracking/AB3DMOT/data/KITTI/$2
python main.py $2
#move result to disk
mkdir /media/lion/Elements\ SE/Exp0722/results/$2
mv ~/Mylidar/Tracking/AB3DMOT/results/$2/* /media/lion/Elements\ SE/Exp0722/results/$2

