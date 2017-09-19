import sys
import os
sys.path.append('src/inference')
import inference_h5


def visualize_deployment(tag, images_dir, metadata_dir, models_dir, streamer_file, outfile):
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

    predictions = inference_h5.predict_by_tag(full_model_path, images_dir, "train")

    d_predictions = {} #{frame_id: prediction}

    for i, p in enumerate(predictions):
        print i, p
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
            ys.append(0)

    with open(outfile, "w+") as f:
        for x, y in zip(xs, ys):
            line = str(x) + "," + str(y) + "\n"
            f.write(line)

def analyze_deployment(tag, images_dir, metadata_dir, models_dir, streamer_file, label, num_apps, outfile):
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

    #video_id = "97081724-dependent-daisy-p3-n7-buffer5000"
    video_id = "146269f6-independent-daisy-p3-n7-buffer2500"
    images_dir = "/users/ahjiang/image-data/video/flowers_video/"
    metadata_dir = "/users/ahjiang/src/mainstream/log/videos/flowers/"
    models_dir = "/users/ahjiang/models/nsdi/flowers/inception/"
    outfile = "/users/ahjiang/src/mainstream-analysis/output/streamer/deploy/daisy/results"

    tag = "daisy"

    '''
    num_apps = 2
    streamer_file = "/users/ahjiang/src/mainstream/log/deploy/flowers/deploy-s0-250ms-2apps-independent-daisy-146269f6-mainstream1"
    label = "mainstream"
    analyze_deployment(tag, images_dir, metadata_dir, models_dir, streamer_file, label, num_apps, outfile)

    label = "nosharing"
    streamer_file = "/users/ahjiang/src/mainstream/log/deploy/flowers/deploy-s0-250ms-2apps-independent-daisy-146269f6-nosharing1"
    analyze_deployment(tag, images_dir, metadata_dir, models_dir, streamer_file, label, num_apps, outfile)

    label = "maxsharing"
    streamer_file = "/users/ahjiang/src/mainstream/log/deploy/flowers/deploy-s0-250ms-2apps-independent-daisy-146269f6-maxsharing1"
    analyze_deployment(tag, images_dir, metadata_dir, models_dir, streamer_file, label, num_apps, outfile)

    num_apps = 3
    label = "mainstream"
    streamer_file = "/users/ahjiang/src/mainstream/log/deploy/flowers/deploy-s0-250ms-3apps-independent-daisy-146269f6-mainstream1"
    analyze_deployment(tag, images_dir, metadata_dir, models_dir, streamer_file, label, num_apps, outfile)

    label = "nosharing"
    streamer_file = "/users/ahjiang/src/mainstream/log/deploy/flowers/deploy-s0-250ms-3apps-independent-daisy-146269f6-nosharing1"
    analyze_deployment(tag, images_dir, metadata_dir, models_dir, streamer_file, label, num_apps, outfile)

    label = "maxsharing"
    streamer_file = "/users/ahjiang/src/mainstream/log/deploy/flowers/deploy-s0-250ms-3apps-independent-daisy-146269f6-maxsharing1"
    analyze_deployment(tag, images_dir, metadata_dir, models_dir, streamer_file, label, num_apps, outfile)

    num_apps = 4
    label = "mainstream"
    streamer_file = "/users/ahjiang/src/mainstream/log/deploy/flowers/deploy-s0-250ms-4apps-independent-daisy-146269f6-mainstream1"
    analyze_deployment(tag, images_dir, metadata_dir, models_dir, streamer_file, label, num_apps, outfile)

    label = "nosharing"
    streamer_file = "/users/ahjiang/src/mainstream/log/deploy/flowers/deploy-s0-250ms-4apps-independent-daisy-146269f6-nosharing1"
    analyze_deployment(tag, images_dir, metadata_dir, models_dir, streamer_file, label, num_apps, outfile)

    label = "maxsharing"
    streamer_file = "/users/ahjiang/src/mainstream/log/deploy/flowers/deploy-s0-250ms-4apps-independent-daisy-146269f6-maxsharing1"
    analyze_deployment(tag, images_dir, metadata_dir, models_dir, streamer_file, label, num_apps, outfile)

    num_apps = 5
    label = "mainstream"
    streamer_file = "/users/ahjiang/src/mainstream/log/deploy/flowers/deploy-s0-250ms-5apps-independent-daisy-146269f6-mainstream1"
    analyze_deployment(tag, images_dir, metadata_dir, models_dir, streamer_file, label, num_apps, outfile)

    label = "nosharing"
    streamer_file = "/users/ahjiang/src/mainstream/log/deploy/flowers/deploy-s0-250ms-5apps-independent-daisy-146269f6-nosharing1"
    analyze_deployment(tag, images_dir, metadata_dir, models_dir, streamer_file, label, num_apps, outfile)

    label = "maxsharing"
    streamer_file = "/users/ahjiang/src/mainstream/log/deploy/flowers/deploy-s0-250ms-5apps-independent-daisy-146269f6-maxsharing1"
    analyze_deployment(tag, images_dir, metadata_dir, models_dir, streamer_file, label, num_apps, outfile)

    num_apps = 6
    label = "mainstream"
    streamer_file = "/users/ahjiang/src/mainstream/log/deploy/flowers/deploy-s0-250ms-6apps-independent-daisy-146269f6-mainstream1"
    analyze_deployment(tag, images_dir, metadata_dir, models_dir, streamer_file, label, num_apps, outfile)

    label = "nosharing"
    streamer_file = "/users/ahjiang/src/mainstream/log/deploy/flowers/deploy-s0-250ms-6apps-independent-daisy-146269f6-nosharing1"
    analyze_deployment(tag, images_dir, metadata_dir, models_dir, streamer_file, label, num_apps, outfile)

    label = "maxsharing"
    streamer_file = "/users/ahjiang/src/mainstream/log/deploy/flowers/deploy-s0-250ms-6apps-independent-daisy-146269f6-maxsharing1"
    analyze_deployment(tag, images_dir, metadata_dir, models_dir, streamer_file, label, num_apps, outfile)

    num_apps = 7
    label = "mainstream"
    streamer_file = "/users/ahjiang/src/mainstream/log/deploy/flowers/deploy-s0-250ms-7apps-independent-daisy-146269f6-mainstream1"
    analyze_deployment(tag, images_dir, metadata_dir, models_dir, streamer_file, label, num_apps, outfile)

    label = "nosharing"
    streamer_file = "/users/ahjiang/src/mainstream/log/deploy/flowers/deploy-s0-250ms-7apps-independent-daisy-146269f6-nosharing1"
    analyze_deployment(tag, images_dir, metadata_dir, models_dir, streamer_file, label, num_apps, outfile)

    label = "maxsharing"
    streamer_file = "/users/ahjiang/src/mainstream/log/deploy/flowers/deploy-s0-250ms-7apps-independent-daisy-146269f6-maxsharing1"
    analyze_deployment(tag, images_dir, metadata_dir, models_dir, streamer_file, label, num_apps, outfile)

    num_apps = 8
    label = "mainstream"
    streamer_file = "/users/ahjiang/src/mainstream/log/deploy/flowers/deploy-s0-250ms-8apps-independent-daisy-146269f6-mainstream1"
    analyze_deployment(tag, images_dir, metadata_dir, models_dir, streamer_file, label, num_apps, outfile)

    label = "nosharing"
    streamer_file = "/users/ahjiang/src/mainstream/log/deploy/flowers/deploy-s0-250ms-8apps-independent-daisy-146269f6-nosharing1"
    analyze_deployment(tag, images_dir, metadata_dir, models_dir, streamer_file, label, num_apps, outfile)

    label = "maxsharing"
    streamer_file = "/users/ahjiang/src/mainstream/log/deploy/flowers/deploy-s0-250ms-8apps-independent-daisy-146269f6-maxsharing1"
    analyze_deployment(tag, images_dir, metadata_dir, models_dir, streamer_file, label, num_apps, outfile)

    num_apps = 9
    label = "mainstream"
    streamer_file = "/users/ahjiang/src/mainstream/log/deploy/flowers/deploy-s0-250ms-9apps-independent-daisy-146269f6-mainstream1"
    analyze_deployment(tag, images_dir, metadata_dir, models_dir, streamer_file, label, num_apps, outfile)

    label = "nosharing"
    streamer_file = "/users/ahjiang/src/mainstream/log/deploy/flowers/deploy-s0-250ms-9apps-independent-daisy-146269f6-nosharing1"
    analyze_deployment(tag, images_dir, metadata_dir, models_dir, streamer_file, label, num_apps, outfile)

    label = "maxsharing"
    streamer_file = "/users/ahjiang/src/mainstream/log/deploy/flowers/deploy-s0-250ms-9apps-independent-daisy-146269f6-maxsharing1"
    analyze_deployment(tag, images_dir, metadata_dir, models_dir, streamer_file, label, num_apps, outfile)

    num_apps = 10
    label = "mainstream"
    streamer_file = "/users/ahjiang/src/mainstream/log/deploy/flowers/deploy-s0-250ms-10apps-independent-daisy-146269f6-mainstream1"
    analyze_deployment(tag, images_dir, metadata_dir, models_dir, streamer_file, label, num_apps, outfile)

    label = "nosharing"
    streamer_file = "/users/ahjiang/src/mainstream/log/deploy/flowers/deploy-s0-250ms-10apps-independent-daisy-146269f6-nosharing1"
    analyze_deployment(tag, images_dir, metadata_dir, models_dir, streamer_file, label, num_apps, outfile)

    label = "maxsharing"
    streamer_file = "/users/ahjiang/src/mainstream/log/deploy/flowers/deploy-s0-250ms-10apps-independent-daisy-146269f6-maxsharing1"
    analyze_deployment(tag, images_dir, metadata_dir, models_dir, streamer_file, label, num_apps, outfile)

    '''
    images_dir = "/users/ahjiang/image-data/video/vid5_frames_resized/"
    models_dir = "/users/ahjiang/models/nsdi/train/inception/"
    outdir =  "/users/ahjiang/src/mainstream-analysis/output/streamer/deploy/train"

    streamer_file = "log/deploy/trains/deploy-train-vid5-20-apps-nosharing4"
    outfile = outdir + "/vid5-20apps-nosharing"
    analyze_train_deployment(images_dir, models_dir, streamer_file, outfile)

    streamer_file = "log/deploy/trains/deploy-train-vid5-20-apps-mainstream1"
    outfile = outdir + "/vid5-20apps-mainstream"
    analyze_train_deployment(images_dir, models_dir, streamer_file, outfile)

