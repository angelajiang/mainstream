import sys
sys.path.append('util')
import ConfigParser
import FineTunerFast as ft

def save_imagenet():
    model = net.build_model(self.net, self.dataset.nb_classes)
    model.compile(optimizer=self.optimizer,
                  loss='categorical_crossentropy',
                  metrics=["accuracy"])
    self.model = model

def train(config_file, dataset_dir, model_prefix, num_frozen):
    ft_obj = ft.FineTunerFast(config_file,
                              dataset_dir,
                              "/tmp/history",
                              model_prefix)
    acc = ft_obj.finetune(num_frozen)
    acc = str.format("{0:.4f}", acc)
    print acc

if __name__ == "__main__":
    config_file, dataset_dir, model_prefix, num_frozen = sys.argv[1:]
    train(config_file, dataset_dir, model_prefix, int(num_frozen))
