python src/training/train.py config/test/1-epoch /datasets/BigLearning/ahjiang/image-data/training/pedestrian ~/atrium/0 84
python src/inference/freeze.py ~/atrium/0
python src/inference/inference_h5.py ~/atrium/0 /datasets/BigLearning/ahjiang/image-data/test/pedestrian | tee log/h5-out
python src/inference/inference_pb.py ~/atrium/0/atrium-mobilenets-0.pb ~/image-data/test/pedestrian | tee log/pb-out
