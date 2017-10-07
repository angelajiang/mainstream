# Trainer
## Dependencies
``` bash
# trainer
sudo pip install keras
sudo pip install h5py
sudo pip install pyro4
sudo pip install redis
# scheduler
sudo pip install zmq
# tests
sudo pip install pytest
```

## Running instructions
``` python
redis-server redis.conf
python -m Pyro4.naming # Start nameserver for pyro
python src/server.py <redis_port>
python src/client.py <cmd> <args...>
```

## Testing instructions
``` bash
cd /path/to/mainstream/
pytest -s test \
--tf_dir /path/to/tensorflow \
--data_dir /path/to/training/data
```

## redis.conf
``` bash
appendonly yes # Set appendonly on to allow persistence across redis instances
```

## Saving models
Currently, models are saved in .pb and .ckpt files. These need be merged
into a single .pb file. This should be done programmatically but currently
is done manually

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

## Run scheduler
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
        {"model_path": "app1_model.pb",
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
schedule.run()
```

