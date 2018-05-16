
# Mainstream

[![Build Status](https://travis-ci.org/angelajiang/mainstream.svg?branch=master)](https://travis-ci.org/angelajiang/mainstream)

# Dependencies
``` bash
# trainer
sudo pip install keras
sudo pip install h5py
sudo pip install pyro4
sudo pip install redis
# scheduler
sudo pip install --upgrade pip enum34
sudo pip install zmq
# tests
sudo pip install pytest
# profiling
go get github.com/google/pprof
# profiling (debian-based systems)
sudo apt-get install google-perftools graphviz
# profiling (os x)
brew install google-perftools graphviz
```

Alternatively, use `pip install -r src/requirements.txt` to install all dependencies.

# Running instructions
``` python
redis-server redis.conf
python -m Pyro4.naming # Start nameserver for pyro
python src/server.py <redis_port>
python src/client.py <cmd> <args...>
```

## Running M-trainer
``` python
python src/client.py train <name> <config_file> <model_dir> <log_dir> <indices> <image_dir> <image_test_dir>
```
- `name`: Human readable name of your dataset.
- `config_file`: Path to config file. Example in `config/example`.
- `model_dir`: Path to output directory to store trained models.
- `log_dir`: Path to log directory.
- `indices`: Indices representing chokepoints for freezing layers. Should be `inception`, `resnet`, `mobilenets` or int repesenting a range
- `image_dir`: Path to directory of images to train on. Each subdirectory contains images for each class. Example of dataset in correct format on the Orca cluster at `/datasets/BigLearning/ahjiang/image-data/training/flower_photos/`
- `image_test_dir`: Path to test directory. (Optional)

## Saving models
Currently, models trained by M-Trainer are saved in .pb and .ckpt files. These need be merged
into a single .pb file. This should be done programmatically but currently
is done manually

### Python API approach
``` bash
python src/inference/freeze.py <model_prefix>
```
- `model_prefix`: Should be the name used to save checkpoint files. Files should exist called <model_prefix>.ckpt <model_prefix>.meta, and <model_prefix>.pb. Model will be saved as `model_prefix`-frozen.pb

### Command-line approach
```bash
cd /path/to/tensorflow
bazel build tensorflow/python/tools:freeze_graph
bazel-bin/tensorflow/python/tools/freeze_graph \
--input_graph=/users/ahjiang/models/saving_v2/flowers-1.pb  \
--input_binary=True \
--output_graph=/users/ahjiang/models/frozen_graph.pb \
--output_node_names dense_2/Softmax \
--input_checkpoint=/users/ahjiang/models/saving_v2/flowers-1.ckpt
```

## Deploying a schedule using Mainstream to Streamer

### Start Streamer's mainstream server
```bash
# In Streamer. Run this server before sending schedules.
./apps/mainstream_server -C <config_dir> --camera <camera_name> -n <model_name> -m <model_dir>
```

- `config_dir`: Path to config dir.
- `camera_name`: Camera name as specified in `<config_dir>/camera.toml`
- `model_name`: Camera name as specified in `<config_dir>/models.toml`
- `model_dir`: Path to directory with model files (*.pb). Note: these should be frozen models.

### Deploy a schedule to Streamer
``` python
video_desc = {"stream_fps": 30}
model_desc = {"total_layers": 41,
              "channels": 3,
              "height": 299,
              "width": 299,
              "layer_latencies": [1] * 41,
              "frozen_layer_names": {1: "input",
                                     10: "conv1",
                                     21: "conv2",
                                     30: "pool",
                                     40: "fc",
                                     41: "softmax"}}
apps = [
        {"app_id":1,
         "model_path": {
            0:  "/path/to/model.pb",
            10: "/path/to/model.pb",
            21: "/path/to/model.pb",
            30: "/path/to/model.pb",
            40: "/path/to/model.pb"
        },
        "event_length_ms": 10,
        "correlation": 0,
        "accuracies": {1: 1,
                       10: 0.8,
                       21: 0.6,
                       30: 0.6,
                       40: 0.2
                      }
        }]

schedule = Scheduler(apps, video_desc, model_desc)
schedule.run(cost_threshold)
```

- `cost_threshold`: Starting cost threshold (e.g., 250). More accurate starting cost threshold allows the scheduler to converge faster.

### Run experiment which deploys schedules to Streamer with increasing number of applications
```bash
# In Mainstream, send schedules to Streamer
python src/scheduler/run_scheduler.py <num_apps> <outfile_prefix>
```

- `num_apps`: Run Scheduler with `num_apps` applications. Applications specified in `data/app_data_mobilenets.py`.
- `outfile_prefix`: Path to `outfile_prefix`. Results will be written to `outfile_prefix`-{mainstream, nosharing, maxsharing}

# Testing instructions
``` bash
cd /path/to/mainstream/
pytest -s test \
--tf_dir /path/to/tensorflow \
--data_dir /path/to/training/data
```

# redis.conf
``` bash
appendonly yes # Set appendonly on to allow persistence across redis instances
```

