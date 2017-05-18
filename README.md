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
redis-server
python -m Pyro4.naming # Start nameserver for pyro
python trainer_server.py
python trainer_client.py start <image_dir> <config_file> acc_threshold
```
