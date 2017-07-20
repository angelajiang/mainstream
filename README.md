# Trainer
## Dependencies
``` bash
sudo pip install keras
sudo pip install h5py
sudo pip install pyro4
sudo pip install redis
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


