import sys
sys.path.append('src/util')
import net


def get_layers(model_path):
    model, tags = net.load(model_path)
    net.compile(model)

    count = 0 
    for layer in model.layers:
        print str(count) + "," + layer.get_config()["name"]
        count += 1

if __name__ == "__main__":
    model_path_h5 = sys.argv[1]
    get_layers(model_path_h5)
