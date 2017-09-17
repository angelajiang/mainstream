import sys
import os
sys.path.append('src/inference')
import inference_h5


def analyze_deployment(images_dir, metadata_dir, models_dir, streamer_file):
    # Return false negative rate
    # images_dir: Dir with jpegs used to create video. 0.jpg, 1.jpg ...
    # metadata_dir: Dir with images_dir label file
    # models_dir: Dir with .pb models
    # streamer_file: Streawmer output file with "image_id, model_path"
    images_dir_full = os.path.join(images_dir, video_id)
    metadata_file = os.path.join(metadata_dir, video_id)

    with open(streamer_file) as f:

        for line in f:
            pass
        last_line = line
        vals = last_line.split(',')
        model_path = str(vals[1]).rstrip()
        full_model_path = os.path.join(models_dir, model_path)
        predictions = inference_h5.predict_by_tag(full_model_path, images_dir_full, "sunflowers")

    d_predictions = {} #{frame_id: prediction}
    with open(streamer_file) as f:
        for line in f:
            vals = line.split(',')
            frame_id = int(vals[0])
            d_predictions[frame_id] = predictions[frame_id]

    all_event_ids_set = set()
    classified_event_ids_set = set()

    with open(metadata_file) as f:
        for line in f:
            try:
                vals = line.split(',')
                frame_id = int(vals[0])
                event_id = int(vals[1])
                negative = int(vals[2])
                ignore = int(vals[3])
                if ignore or negative:
                    continue
                all_event_ids_set.add(event_id)
                prediction = d_predictions[frame_id]
                if prediction > 0.5:
                    classified_event_ids_set.add(event_id)
            except:
                continue

    fnr = len(classified_event_ids_set) / float(len(all_event_ids_set))
    print streamer_file, round(fnr, 4)
    return fnr

if __name__ == "__main__":
    '''
    video_id = "be406d54"
    images_dir = "/users/ahjiang/image-data/video/flowers_video/"
    metadata_dir = "/users/ahjiang/src/mainstream/log/videos/flowers/"
    models_dir = "/users/ahjiang/models/nsdi/flowers/inception/"

    streamer_file = "/users/ahjiang/src/mainstream/log/deploy/flowers/deploy-s0-250ms-10apps-mainstream1"
    analyze_deployment(images_dir, metadata_dir, models_dir, streamer_file)

    streamer_file = "/users/ahjiang/src/mainstream/log/deploy/flowers/deploy-s0-250ms-10apps-maxsharing1"
    analyze_deployment(images_dir, metadata_dir, models_dir, streamer_file)

    streamer_file = "/users/ahjiang/src/mainstream/log/deploy/flowers/deploy-s0-250ms-10apps-nosharing1"
    analyze_deployment(images_dir, metadata_dir, models_dir, streamer_file)
    '''

    video_id = "59a439c2-dependent"
    images_dir = "/users/ahjiang/image-data/video/flowers_video/"
    metadata_dir = "/users/ahjiang/src/mainstream/log/videos/flowers/"
    models_dir = "/users/ahjiang/models/nsdi/flowers/inception/"

    streamer_file = "/users/ahjiang/src/mainstream/log/deploy/flowers/deploy-s0-250ms-10apps-independent-mainstream1"
    analyze_deployment(images_dir, metadata_dir, models_dir, streamer_file)

    streamer_file = "/users/ahjiang/src/mainstream/log/deploy/flowers/deploy-s0-250ms-10apps-independent-maxsharing1"
    analyze_deployment(images_dir, metadata_dir, models_dir, streamer_file)

    streamer_file = "/users/ahjiang/src/mainstream/log/deploy/flowers/deploy-s0-250ms-10apps-independent-nosharing1"
    analyze_deployment(images_dir, metadata_dir, models_dir, streamer_file)
