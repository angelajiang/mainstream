import sys
import os
sys.path.append('src/inference')
import inference_h5


def analyze_deployment(label, images_dir, metadata_dir, models_dir, streamer_file):
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
        print model_path
        full_model_path = os.path.join(models_dir, model_path)
        predictions = inference_h5.predict_by_tag(full_model_path, images_dir_full, label)

    d_predictions = {} #{frame_id: prediction}
    with open(streamer_file) as f:
        for line in f:
            vals = line.split(',')
            frame_id = int(vals[0])
            d_predictions[frame_id] = predictions[frame_id]

    all_event_ids_set = set()
    true_positives = set()

    all_negative_ids_set = set()
    false_positives = set()

    with open(metadata_file) as f:
        for line in f:
            try:
                vals = line.split(',')
                frame_id = int(vals[0])
                event_id = int(vals[1])
                negative = int(vals[2])
                ignore = int(vals[3])
                if ignore:
                    continue
                if negative:
                    all_negative_ids_set.add(frame_id)
                    prediction = d_predictions[frame_id]
                    if prediction == 1:
                        false_positives.add(event_id)
                else:
                    all_event_ids_set.add(event_id)
                    prediction = d_predictions[frame_id]
                    if prediction == 1:
                        true_positives.add(event_id)
            except:
                continue

    tpr = len(true_positives) / float(len(all_event_ids_set))
    fpr = len(false_positives) / float(len(all_negative_ids_set))
    print streamer_file, round(tpr, 4), round(fpr, 4)
    return tpr, fpr

if __name__ == "__main__":

    #video_id = "97081724-dependent-daisy-p3-n7-buffer5000"
    video_id = "146269f6-independent-daisy-p3-n7-buffer2500"
    images_dir = "/users/ahjiang/image-data/video/flowers_video/"
    metadata_dir = "/users/ahjiang/src/mainstream/log/videos/flowers/"
    models_dir = "/users/ahjiang/models/nsdi/flowers/inception/"

    label = "daisy"

    streamer_file = "/users/ahjiang/src/mainstream/log/deploy/flowers/deploy-s0-250ms-6apps-independent-daisy-146269f6-mainstream1"
    analyze_deployment(label, images_dir, metadata_dir, models_dir, streamer_file)

    streamer_file = "/users/ahjiang/src/mainstream/log/deploy/flowers/deploy-s0-250ms-6apps-independent-daisy-146269f6-nosharing1"
    analyze_deployment(label, images_dir, metadata_dir, models_dir, streamer_file)

    streamer_file = "/users/ahjiang/src/mainstream/log/deploy/flowers/deploy-s0-250ms-6apps-independent-daisy-146269f6-maxsharing1"
    analyze_deployment(label, images_dir, metadata_dir, models_dir, streamer_file)

    streamer_file = "/users/ahjiang/src/mainstream/log/deploy/flowers/deploy-s0-250ms-7apps-independent-daisy-146269f6-mainstream1"
    analyze_deployment(label, images_dir, metadata_dir, models_dir, streamer_file)

    streamer_file = "/users/ahjiang/src/mainstream/log/deploy/flowers/deploy-s0-250ms-7apps-independent-daisy-146269f6-nosharing1"
    analyze_deployment(label, images_dir, metadata_dir, models_dir, streamer_file)

    streamer_file = "/users/ahjiang/src/mainstream/log/deploy/flowers/deploy-s0-250ms-7apps-independent-daisy-146269f6-maxsharing1"
    analyze_deployment(label, images_dir, metadata_dir, models_dir, streamer_file)

    streamer_file = "/users/ahjiang/src/mainstream/log/deploy/flowers/deploy-s0-250ms-8apps-independent-daisy-146269f6-mainstream1"
    analyze_deployment(label, images_dir, metadata_dir, models_dir, streamer_file)

    streamer_file = "/users/ahjiang/src/mainstream/log/deploy/flowers/deploy-s0-250ms-8apps-independent-daisy-146269f6-nosharing1"
    analyze_deployment(label, images_dir, metadata_dir, models_dir, streamer_file)

    streamer_file = "/users/ahjiang/src/mainstream/log/deploy/flowers/deploy-s0-250ms-8apps-independent-daisy-146269f6-maxsharing1"
    analyze_deployment(label, images_dir, metadata_dir, models_dir, streamer_file)

    streamer_file = "/users/ahjiang/src/mainstream/log/deploy/flowers/deploy-s0-250ms-9apps-independent-daisy-146269f6-mainstream1"
    analyze_deployment(label, images_dir, metadata_dir, models_dir, streamer_file)

    streamer_file = "/users/ahjiang/src/mainstream/log/deploy/flowers/deploy-s0-250ms-9apps-independent-daisy-146269f6-nosharing1"
    analyze_deployment(label, images_dir, metadata_dir, models_dir, streamer_file)

    streamer_file = "/users/ahjiang/src/mainstream/log/deploy/flowers/deploy-s0-250ms-9apps-independent-daisy-146269f6-maxsharing1"
    analyze_deployment(label, images_dir, metadata_dir, models_dir, streamer_file)

    streamer_file = "/users/ahjiang/src/mainstream/log/deploy/flowers/deploy-s0-250ms-10apps-independent-daisy-146269f6-mainstream1"
    analyze_deployment(label, images_dir, metadata_dir, models_dir, streamer_file)

    streamer_file = "/users/ahjiang/src/mainstream/log/deploy/flowers/deploy-s0-250ms-10apps-independent-daisy-146269f6-nosharing1"
    analyze_deployment(label, images_dir, metadata_dir, models_dir, streamer_file)

    streamer_file = "/users/ahjiang/src/mainstream/log/deploy/flowers/deploy-s0-250ms-10apps-independent-daisy-146269f6-maxsharing1"
    analyze_deployment(label, images_dir, metadata_dir, models_dir, streamer_file)
