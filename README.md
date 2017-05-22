# Trainer
## Dependencies
``` bash
sudo pip install keras
sudo pip install h5py
sudo pip install pyro4
sudo pip install redis
```

## Running instructions
``` python
redis-server redis.conf
python -m Pyro4.naming # Start nameserver for pyro
python trainer_server.py
python trainer_client.py start <image_dir> <config_file> acc_threshold
```

## redis.conf
``` bash
port 6380 # Use port other than 6379 to avoid collisions init.d redis-server
appendonly yes # Set appendonly on to allow persistence across redis instances
```
