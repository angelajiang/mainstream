import sys
import os
sys.path.append('src/inference')
import inference_h5


def visualize_deployment(images_dir, models_dir, streamer_file, outfile):
    frame_ids = []
    
    with open(streamer_file) as f:
        for line in f:
            vals = line.split(',')
            frame_id = int(vals[0])
            frame_ids.append(frame_id)

    xs = range(max(frame_ids))
    ys = []
    for x in xs:
        if x in frame_ids:
            ys.append(1)
        else:
            ys.append(0)

    with open(outfile, "w+") as f:
        for x, y in zip(xs, ys):
            line = str(x) + "," + str(y) + "\n"
            f.write(line)

def analyze_train_deployment(images_dir, models_dir, streamer_file, outfile):
    with open(streamer_file) as f:
        for line in f:
            pass
        last_line = line
        vals = last_line.split(',')
        model_path = str(vals[1]).rstrip()
        print model_path
        full_model_path = os.path.join(models_dir, model_path)
    full_model_path = "/users/ahjiang/models/trains-new/7-trains/trains7-229"

    predictions = inference_h5.predict_by_tag(full_model_path, images_dir, "no-train")

    d_predictions = {} #{frame_id: prediction}

    for i, p in enumerate(predictions):
        d_predictions[i] = p

    seen_frame_ids = []
    with open(streamer_file) as f:
        for line in f:
            vals = line.split(',')
            frame_id = int(vals[0])
            seen_frame_ids.append(frame_id)

    xs = range(max(seen_frame_ids))
    ys = []

    analyzed_frame_ids = max(d_predictions.keys())

    for x in xs:
        if x > analyzed_frame_ids:
            continue 
        if x in seen_frame_ids:
            ys.append(d_predictions[x])
        else:
            ys.append(-1)

    with open(outfile, "w+") as f:
        for x, y in zip(xs, ys):
            line = str(x) + "," + str(y) + "\n"
            f.write(line)

def analyze_deployment(tag, video_id, images_dir, metadata_dir, models_dir, streamer_file, label, num_apps, outfile):
    # Return false negative rate
    # images_dir: Dir with jpegs used to create video. 0.jpg, 1.jpg ...
    # metadata_dir: Dir with images_dir tag file
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
        predictions = inference_h5.predict_by_tag(full_model_path, images_dir_full, tag)

    d_predictions = {} #{frame_id: prediction}
    my_predictions = {} #{frame_id: prediction}
    for i, p in enumerate(predictions):
        d_predictions[i] = p

    with open(streamer_file) as f:
        for line in f:
            vals = line.split(',')
            frame_id = int(vals[0])
            my_predictions[frame_id] = d_predictions[frame_id]

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
                    prediction = my_predictions[frame_id]
                    if prediction == 1:
                        false_positives.add(event_id)
                else:
                    all_event_ids_set.add(event_id)
                    prediction = my_predictions[frame_id]
                    if prediction == 1:
                        true_positives.add(event_id)
            except:
                continue

    tpr = len(true_positives) / float(len(all_event_ids_set))
    fpr = len(false_positives) / float(len(all_negative_ids_set))

    with open(outfile, "a+") as f:
        line = label + "," + str(num_apps) + "," + str(round(tpr, 4)) + "," + str(round(fpr,4)) + "\n"
        f.write(line)
    print streamer_file, round(tpr, 4), round(fpr, 4)

    return tpr, fpr

if __name__ == "__main__":

    images_dir = "/users/ahjiang/image-data/video/vid5_frames_resized/"
    models_dir = "/users/ahjiang/models/nsdi/train/inception/"
    outdir =  "/users/ahjiang/src/mainstream-analysis/output/streamer/deploy/train"

    images_dir = "/users/ahjiang/image-data/instances/train_images_resized/2/"

    streamer_file = "log/deploy/trains/deploy-train-vid0-10-apps-nosharing"
    outfile = outdir + "/train2-10apps-nosharing"
    #analyze_train_deployment(images_dir, models_dir, streamer_file, outfile)

    streamer_file = "log/deploy/trains/deploy-train-vid0-10-apps-mainstream"
    outfile = outdir + "/train2-10apps-mainstream"
    #analyze_train_deployment(images_dir, models_dir, streamer_file, outfile)

    streamer_file = "log/deploy/trains/deploy-train-vid0-10-apps-maxsharing"
    outfile = outdir + "/train2-10apps-maxsharing"
    #analyze_train_deployment(images_dir, models_dir, streamer_file, outfile)

    images_dir = "/users/ahjiang/image-data/video/vid4_frames_resized"
    streamer_file = "log/deploy/trains/deploy-train-vid0-10-apps-nosharing"
    outfile = outdir + "/vid4-10apps-fpf-nosharing"
    analyze_train_deployment(images_dir, models_dir, streamer_file, outfile)

    streamer_file = "log/deploy/trains/deploy-train-vid0-10-apps-mainstream"
    outfile = outdir + "/vid4-10apps-fpf-mainstream"
    analyze_train_deployment(images_dir, models_dir, streamer_file, outfile)

