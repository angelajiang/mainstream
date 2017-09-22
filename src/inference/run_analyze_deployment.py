import sys
sys.path.append('src/inference')
import analyze_deployment

if __name__ == "__main__":

    video_id = "97081724-dependent-daisy-p3-n7-buffer5000"
    #video_id = "146269f6-independent-daisy-p3-n7-buffer2500"
    images_dir = "/users/ahjiang/image-data/video/flowers_video/"
    metadata_dir = "/users/ahjiang/src/mainstream/log/videos/flowers/"
    models_dir = "/users/ahjiang/models/nsdi/flowers/inception/"
    outfile = "/users/ahjiang/src/mainstream-analysis/output/streamer/deploy/daisy/results-independent-97081724"

    tag = "daisy"

    num_apps = 2
    streamer_file = "/users/ahjiang/src/mainstream/log/deploy/flowers/deploy-s0-250ms-2apps-perturbed-daisy-06e4f5c8-mainstream1"
    label = "mainstream"
    analyze_deployment.analyze_deployment(tag, video_id, images_dir, metadata_dir, models_dir, streamer_file, label, num_apps, outfile)

    label = "nosharing"
    streamer_file = "/users/ahjiang/src/mainstream/log/deploy/flowers/deploy-s0-250ms-2apps-perturbed-daisy-06e4f5c8-nosharing1"
    analyze_deployment.analyze_deployment(tag, video_id, images_dir, metadata_dir, models_dir, streamer_file, label, num_apps, outfile)

    label = "maxsharing"
    streamer_file = "/users/ahjiang/src/mainstream/log/deploy/flowers/deploy-s0-250ms-2apps-perturbed-daisy-06e4f5c8-maxsharing1"
    analyze_deployment.analyze_deployment(tag, video_id, images_dir, metadata_dir, models_dir, streamer_file, label, num_apps, outfile)

    num_apps = 3
    label = "mainstream"
    streamer_file = "/users/ahjiang/src/mainstream/log/deploy/flowers/deploy-s0-250ms-3apps-perturbed-daisy-06e4f5c8-mainstream1"
    analyze_deployment.analyze_deployment(tag, video_id, images_dir, metadata_dir, models_dir, streamer_file, label, num_apps, outfile)

    label = "nosharing"
    streamer_file = "/users/ahjiang/src/mainstream/log/deploy/flowers/deploy-s0-250ms-3apps-perturbed-daisy-06e4f5c8-nosharing1"
    analyze_deployment.analyze_deployment(tag, video_id, images_dir, metadata_dir, models_dir, streamer_file, label, num_apps, outfile)

    label = "maxsharing"
    streamer_file = "/users/ahjiang/src/mainstream/log/deploy/flowers/deploy-s0-250ms-3apps-perturbed-daisy-06e4f5c8-maxsharing1"
    analyze_deployment.analyze_deployment(tag, video_id, images_dir, metadata_dir, models_dir, streamer_file, label, num_apps, outfile)

    num_apps = 4
    label = "mainstream"
    streamer_file = "/users/ahjiang/src/mainstream/log/deploy/flowers/deploy-s0-250ms-4apps-perturbed-daisy-06e4f5c8-mainstream1"
    analyze_deployment.analyze_deployment(tag, video_id, images_dir, metadata_dir, models_dir, streamer_file, label, num_apps, outfile)

    label = "nosharing"
    streamer_file = "/users/ahjiang/src/mainstream/log/deploy/flowers/deploy-s0-250ms-4apps-perturbed-daisy-06e4f5c8-nosharing1"
    analyze_deployment.analyze_deployment(tag, video_id, images_dir, metadata_dir, models_dir, streamer_file, label, num_apps, outfile)

    label = "maxsharing"
    streamer_file = "/users/ahjiang/src/mainstream/log/deploy/flowers/deploy-s0-250ms-4apps-perturbed-daisy-06e4f5c8-maxsharing1"
    analyze_deployment.analyze_deployment(tag, video_id, images_dir, metadata_dir, models_dir, streamer_file, label, num_apps, outfile)

    num_apps = 5
    label = "mainstream"
    streamer_file = "/users/ahjiang/src/mainstream/log/deploy/flowers/deploy-s0-250ms-5apps-perturbed-daisy-06e4f5c8-mainstream1"
    analyze_deployment.analyze_deployment(tag, video_id, images_dir, metadata_dir, models_dir, streamer_file, label, num_apps, outfile)

    label = "nosharing"
    streamer_file = "/users/ahjiang/src/mainstream/log/deploy/flowers/deploy-s0-250ms-5apps-perturbed-daisy-06e4f5c8-nosharing1"
    analyze_deployment.analyze_deployment(tag, video_id, images_dir, metadata_dir, models_dir, streamer_file, label, num_apps, outfile)

    label = "maxsharing"
    streamer_file = "/users/ahjiang/src/mainstream/log/deploy/flowers/deploy-s0-250ms-5apps-perturbed-daisy-06e4f5c8-maxsharing1"
    analyze_deployment.analyze_deployment(tag, video_id, images_dir, metadata_dir, models_dir, streamer_file, label, num_apps, outfile)

    num_apps = 6
    label = "mainstream"
    streamer_file = "/users/ahjiang/src/mainstream/log/deploy/flowers/deploy-s0-250ms-6apps-perturbed-daisy-06e4f5c8-mainstream1"
    analyze_deployment.analyze_deployment(tag, video_id, images_dir, metadata_dir, models_dir, streamer_file, label, num_apps, outfile)

    label = "nosharing"
    streamer_file = "/users/ahjiang/src/mainstream/log/deploy/flowers/deploy-s0-250ms-6apps-perturbed-daisy-06e4f5c8-nosharing1"
    analyze_deployment.analyze_deployment(tag, video_id, images_dir, metadata_dir, models_dir, streamer_file, label, num_apps, outfile)

    label = "maxsharing"
    streamer_file = "/users/ahjiang/src/mainstream/log/deploy/flowers/deploy-s0-250ms-6apps-perturbed-daisy-06e4f5c8-maxsharing1"
    analyze_deployment.analyze_deployment(tag, video_id, images_dir, metadata_dir, models_dir, streamer_file, label, num_apps, outfile)

    num_apps = 7
    label = "mainstream"
    streamer_file = "/users/ahjiang/src/mainstream/log/deploy/flowers/deploy-s0-250ms-7apps-perturbed-daisy-06e4f5c8-mainstream1"
    analyze_deployment.analyze_deployment(tag, video_id, images_dir, metadata_dir, models_dir, streamer_file, label, num_apps, outfile)

    label = "nosharing"
    streamer_file = "/users/ahjiang/src/mainstream/log/deploy/flowers/deploy-s0-250ms-7apps-perturbed-daisy-06e4f5c8-nosharing1"
    analyze_deployment.analyze_deployment(tag, video_id, images_dir, metadata_dir, models_dir, streamer_file, label, num_apps, outfile)

    label = "maxsharing"
    streamer_file = "/users/ahjiang/src/mainstream/log/deploy/flowers/deploy-s0-250ms-7apps-perturbed-daisy-06e4f5c8-maxsharing1"
    analyze_deployment.analyze_deployment(tag, video_id, images_dir, metadata_dir, models_dir, streamer_file, label, num_apps, outfile)

    num_apps = 8
    label = "mainstream"
    streamer_file = "/users/ahjiang/src/mainstream/log/deploy/flowers/deploy-s0-250ms-8apps-perturbed-daisy-06e4f5c8-mainstream1"
    analyze_deployment.analyze_deployment(tag, video_id, images_dir, metadata_dir, models_dir, streamer_file, label, num_apps, outfile)

    label = "nosharing"
    streamer_file = "/users/ahjiang/src/mainstream/log/deploy/flowers/deploy-s0-250ms-8apps-perturbed-daisy-06e4f5c8-nosharing1"
    analyze_deployment.analyze_deployment(tag, video_id, images_dir, metadata_dir, models_dir, streamer_file, label, num_apps, outfile)

    label = "maxsharing"
    streamer_file = "/users/ahjiang/src/mainstream/log/deploy/flowers/deploy-s0-250ms-8apps-perturbed-daisy-06e4f5c8-maxsharing1"
    analyze_deployment.analyze_deployment(tag, video_id, images_dir, metadata_dir, models_dir, streamer_file, label, num_apps, outfile)

    num_apps = 9
    label = "mainstream"
    streamer_file = "/users/ahjiang/src/mainstream/log/deploy/flowers/deploy-s0-250ms-9apps-perturbed-daisy-06e4f5c8-mainstream1"
    analyze_deployment.analyze_deployment(tag, video_id, images_dir, metadata_dir, models_dir, streamer_file, label, num_apps, outfile)

    label = "nosharing"
    streamer_file = "/users/ahjiang/src/mainstream/log/deploy/flowers/deploy-s0-250ms-9apps-perturbed-daisy-06e4f5c8-nosharing1"
    analyze_deployment.analyze_deployment(tag, video_id, images_dir, metadata_dir, models_dir, streamer_file, label, num_apps, outfile)

    label = "maxsharing"
    streamer_file = "/users/ahjiang/src/mainstream/log/deploy/flowers/deploy-s0-250ms-9apps-perturbed-daisy-06e4f5c8-maxsharing1"
    analyze_deployment.analyze_deployment(tag, video_id, images_dir, metadata_dir, models_dir, streamer_file, label, num_apps, outfile)

    num_apps = 10
    label = "mainstream"
    streamer_file = "/users/ahjiang/src/mainstream/log/deploy/flowers/deploy-s0-250ms-10apps-perturbed-daisy-06e4f5c8-mainstream1"
    analyze_deployment.analyze_deployment(tag, video_id, images_dir, metadata_dir, models_dir, streamer_file, label, num_apps, outfile)

    label = "nosharing"
    streamer_file = "/users/ahjiang/src/mainstream/log/deploy/flowers/deploy-s0-250ms-10apps-perturbed-daisy-06e4f5c8-nosharing1"
    analyze_deployment.analyze_deployment(tag, video_id, images_dir, metadata_dir, models_dir, streamer_file, label, num_apps, outfile)

    label = "maxsharing"
    streamer_file = "/users/ahjiang/src/mainstream/log/deploy/flowers/deploy-s0-250ms-10apps-perturbed-daisy-06e4f5c8-maxsharing1"
    analyze_deployment.analyze_deployment(tag, video_id, images_dir, metadata_dir, models_dir, streamer_file, label, num_apps, outfile)

    '''
    num_apps = 2
    streamer_file = "/users/ahjiang/src/mainstream/log/deploy/flowers/deploy-s0-250ms-2apps-dependent-daisy-97081724-mainstream1"
    label = "mainstream"
    analyze_deployment.analyze_deployment(tag, video_id, images_dir, metadata_dir, models_dir, streamer_file, label, num_apps, outfile)

    label = "nosharing"
    streamer_file = "/users/ahjiang/src/mainstream/log/deploy/flowers/deploy-s0-250ms-2apps-dependent-daisy-97081724-nosharing1"
    analyze_deployment.analyze_deployment(tag, video_id, images_dir, metadata_dir, models_dir, streamer_file, label, num_apps, outfile)

    label = "maxsharing"
    streamer_file = "/users/ahjiang/src/mainstream/log/deploy/flowers/deploy-s0-250ms-2apps-dependent-daisy-97081724-maxsharing1"
    analyze_deployment.analyze_deployment(tag, video_id, images_dir, metadata_dir, models_dir, streamer_file, label, num_apps, outfile)

    num_apps = 3
    label = "mainstream"
    streamer_file = "/users/ahjiang/src/mainstream/log/deploy/flowers/deploy-s0-250ms-3apps-dependent-daisy-97081724-mainstream1"
    analyze_deployment.analyze_deployment(tag, video_id, images_dir, metadata_dir, models_dir, streamer_file, label, num_apps, outfile)

    label = "nosharing"
    streamer_file = "/users/ahjiang/src/mainstream/log/deploy/flowers/deploy-s0-250ms-3apps-dependent-daisy-97081724-nosharing1"
    analyze_deployment.analyze_deployment(tag, video_id, images_dir, metadata_dir, models_dir, streamer_file, label, num_apps, outfile)

    label = "maxsharing"
    streamer_file = "/users/ahjiang/src/mainstream/log/deploy/flowers/deploy-s0-250ms-3apps-dependent-daisy-97081724-maxsharing1"
    analyze_deployment.analyze_deployment(tag, video_id, images_dir, metadata_dir, models_dir, streamer_file, label, num_apps, outfile)

    num_apps = 4
    label = "mainstream"
    streamer_file = "/users/ahjiang/src/mainstream/log/deploy/flowers/deploy-s0-250ms-4apps-dependent-daisy-97081724-mainstream1"
    analyze_deployment.analyze_deployment(tag, video_id, images_dir, metadata_dir, models_dir, streamer_file, label, num_apps, outfile)

    label = "nosharing"
    streamer_file = "/users/ahjiang/src/mainstream/log/deploy/flowers/deploy-s0-250ms-4apps-dependent-daisy-97081724-nosharing1"
    analyze_deployment.analyze_deployment(tag, video_id, images_dir, metadata_dir, models_dir, streamer_file, label, num_apps, outfile)

    label = "maxsharing"
    streamer_file = "/users/ahjiang/src/mainstream/log/deploy/flowers/deploy-s0-250ms-4apps-dependent-daisy-97081724-maxsharing1"
    analyze_deployment.analyze_deployment(tag, video_id, images_dir, metadata_dir, models_dir, streamer_file, label, num_apps, outfile)

    num_apps = 5
    label = "mainstream"
    streamer_file = "/users/ahjiang/src/mainstream/log/deploy/flowers/deploy-s0-250ms-5apps-dependent-daisy-97081724-mainstream1"
    analyze_deployment.analyze_deployment(tag, video_id, images_dir, metadata_dir, models_dir, streamer_file, label, num_apps, outfile)

    label = "nosharing"
    streamer_file = "/users/ahjiang/src/mainstream/log/deploy/flowers/deploy-s0-250ms-5apps-dependent-daisy-97081724-nosharing1"
    analyze_deployment.analyze_deployment(tag, video_id, images_dir, metadata_dir, models_dir, streamer_file, label, num_apps, outfile)

    label = "maxsharing"
    streamer_file = "/users/ahjiang/src/mainstream/log/deploy/flowers/deploy-s0-250ms-5apps-dependent-daisy-97081724-maxsharing1"
    analyze_deployment.analyze_deployment(tag, video_id, images_dir, metadata_dir, models_dir, streamer_file, label, num_apps, outfile)

    num_apps = 6
    label = "mainstream"
    streamer_file = "/users/ahjiang/src/mainstream/log/deploy/flowers/deploy-s0-250ms-6apps-dependent-daisy-97081724-mainstream1"
    analyze_deployment.analyze_deployment(tag, video_id, images_dir, metadata_dir, models_dir, streamer_file, label, num_apps, outfile)

    label = "nosharing"
    streamer_file = "/users/ahjiang/src/mainstream/log/deploy/flowers/deploy-s0-250ms-6apps-dependent-daisy-97081724-nosharing1"
    analyze_deployment.analyze_deployment(tag, video_id, images_dir, metadata_dir, models_dir, streamer_file, label, num_apps, outfile)

    label = "maxsharing"
    streamer_file = "/users/ahjiang/src/mainstream/log/deploy/flowers/deploy-s0-250ms-6apps-dependent-daisy-97081724-maxsharing1"
    analyze_deployment.analyze_deployment(tag, video_id, images_dir, metadata_dir, models_dir, streamer_file, label, num_apps, outfile)
    '''

    num_apps = 7
    label = "mainstream"
    streamer_file = "/users/ahjiang/src/mainstream/log/deploy/flowers/deploy-s0-250ms-7apps-dependent-daisy-97081724-mainstream1"
    analyze_deployment.analyze_deployment(tag, video_id, images_dir, metadata_dir, models_dir, streamer_file, label, num_apps, outfile)

    label = "nosharing"
    streamer_file = "/users/ahjiang/src/mainstream/log/deploy/flowers/deploy-s0-250ms-7apps-dependent-daisy-97081724-nosharing1"
    analyze_deployment.analyze_deployment(tag, video_id, images_dir, metadata_dir, models_dir, streamer_file, label, num_apps, outfile)

    label = "maxsharing"
    streamer_file = "/users/ahjiang/src/mainstream/log/deploy/flowers/deploy-s0-250ms-7apps-dependent-daisy-97081724-maxsharing1"
    analyze_deployment.analyze_deployment(tag, video_id, images_dir, metadata_dir, models_dir, streamer_file, label, num_apps, outfile)

    num_apps = 8
    label = "mainstream"
    streamer_file = "/users/ahjiang/src/mainstream/log/deploy/flowers/deploy-s0-250ms-8apps-dependent-daisy-97081724-mainstream1"
    analyze_deployment.analyze_deployment(tag, video_id, images_dir, metadata_dir, models_dir, streamer_file, label, num_apps, outfile)

    label = "nosharing"
    streamer_file = "/users/ahjiang/src/mainstream/log/deploy/flowers/deploy-s0-250ms-8apps-dependent-daisy-97081724-nosharing1"
    analyze_deployment.analyze_deployment(tag, video_id, images_dir, metadata_dir, models_dir, streamer_file, label, num_apps, outfile)

    label = "maxsharing"
    streamer_file = "/users/ahjiang/src/mainstream/log/deploy/flowers/deploy-s0-250ms-8apps-dependent-daisy-97081724-maxsharing1"
    analyze_deployment.analyze_deployment(tag, video_id, images_dir, metadata_dir, models_dir, streamer_file, label, num_apps, outfile)

    num_apps = 9
    label = "mainstream"
    streamer_file = "/users/ahjiang/src/mainstream/log/deploy/flowers/deploy-s0-250ms-9apps-dependent-daisy-97081724-mainstream1"
    analyze_deployment.analyze_deployment(tag, video_id, images_dir, metadata_dir, models_dir, streamer_file, label, num_apps, outfile)

    label = "nosharing"
    streamer_file = "/users/ahjiang/src/mainstream/log/deploy/flowers/deploy-s0-250ms-9apps-dependent-daisy-97081724-nosharing1"
    analyze_deployment.analyze_deployment(tag, video_id, images_dir, metadata_dir, models_dir, streamer_file, label, num_apps, outfile)

    label = "maxsharing"
    streamer_file = "/users/ahjiang/src/mainstream/log/deploy/flowers/deploy-s0-250ms-9apps-dependent-daisy-97081724-maxsharing1"
    analyze_deployment.analyze_deployment(tag, video_id, images_dir, metadata_dir, models_dir, streamer_file, label, num_apps, outfile)

    num_apps = 10
    label = "mainstream"
    streamer_file = "/users/ahjiang/src/mainstream/log/deploy/flowers/deploy-s0-250ms-10apps-dependent-daisy-97081724-mainstream1"
    analyze_deployment.analyze_deployment(tag, video_id, images_dir, metadata_dir, models_dir, streamer_file, label, num_apps, outfile)

    label = "nosharing"
    streamer_file = "/users/ahjiang/src/mainstream/log/deploy/flowers/deploy-s0-250ms-10apps-dependent-daisy-97081724-nosharing1"
    analyze_deployment.analyze_deployment(tag, video_id, images_dir, metadata_dir, models_dir, streamer_file, label, num_apps, outfile)

    label = "maxsharing"
    streamer_file = "/users/ahjiang/src/mainstream/log/deploy/flowers/deploy-s0-250ms-10apps-dependent-daisy-97081724-maxsharing1"
    analyze_deployment.analyze_deployment(tag, video_id, images_dir, metadata_dir, models_dir, streamer_file, label, num_apps, outfile)
