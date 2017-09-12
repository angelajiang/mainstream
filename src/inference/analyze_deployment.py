import sys
import os
sys.path.append('src/inference')
import inference_h5


def analyze_deployment(images_dir, metadata_dir, models_dir, output_file):
    images_dir_full = os.path.join(images_dir, video_id)
    metadata_file = os.path.join(metadata_dir, video_id)

    with open(output_file) as f:
        for line in f:
            vals = line.split(',')
            frame_id = vals[0]
            model_path = vals[1]
            full_model_path = os.path.join(model_dir, models_path)
            predictions = inference_h5.predict(full_model_path, images_dir_full)
            print predictions
            #frame_file = os.path.join(images_dir_full, frame_id + ".jpg")

if __name__ == "__main__":
    video_id = "af1b2e23"
    images_dir = "/Users/angela/src/data/image-data/flowers_video/"
    metadata_dir = "/Users/angela/src/private/mainstream-analysis/output/video/"
    models_dir = "/users/ahjiang/models/nsdi/flowers/inception/"
    output_file = "/Users/angela/src/private/mainstream-analysis/output/streamer/deployment/flowers/deploy-s0-250ms-10apps-mainstream1"
    analyze_deployment(images_dir, metadata_dir, output_file)
