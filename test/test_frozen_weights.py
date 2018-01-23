import pytest
import pprint as pp
import sys
sys.path.append('test')
import get_weights_h5

@pytest.mark.unit
def test_model_weights():
    model1 = "/users/ahjiang/models/detection/yad2k/pedestrian/yolov2-atrium-caltech-pedestrian-10fr-trial0.h5"
    model2 = "/users/ahjiang/models/detection/yad2k/pedestrian/yolov2-atrium-caltech-pedestrian-60fr-trial0.h5"
    num_frozen = 73
    weights1 = get_weights_h5.get_weights_yad2k(model1, num_frozen)
    weights2 = get_weights_h5.get_weights_yad2k(model2, num_frozen)

    for layer_name in weights1.keys():

        print "===================", layer_name, "===================="

        for a, b in zip(weights1[layer_name], weights2[layer_name]):
            for c, d in zip(a, b):
                assert round(c, 3) == round(d, 3)

