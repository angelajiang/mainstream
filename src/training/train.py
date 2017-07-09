import sys
sys.path.append('util')
import ConfigParser
import FineTunerFast as ft

def train(config_file, dataset_dir, model_prefix, num_training_layers):
    ft_obj = ft.FineTunerFast(config_file, dataset_dir, "/tmp/history", model_prefix)
    acc = ft_obj.finetune(num_training_layers)
    acc = str.format("{0:.4f}", acc)
    print acc

if __name__ == "__main__":
    config_file, dataset_dir, model_prefix, num_training_layers = sys.argv[1:]
    train(config_file, dataset_dir, model_prefix, int(num_training_layers))
