python src/training/train.py config/test/1-epoch ~/image-data/training/train_images_small/ ~/models/test-model 310
python src/inference/freeze.py ~/models/test-model
python src/inference/inference_h5.py ~/models/test-model ~/image-data/training/train_images_small/ | tee log/h5-out
python src/inference/inference_pb.py ~/models/test-model-frozen.pb ~/image-data/training/train_images_small/ | tee log/pb-out
