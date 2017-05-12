
BASIC_PIPELINE = { \
    "pipeline_name": "MainStreamPipeline",
    "processors": [
    {
        "processor_name": "Camera",
        "processor_type": "Camera",
        "parameters": {
            "camera_name": "GST_TEST"
        }
    },
    {
        "processor_name": "Transformer",
        "processor_type": "ImageTransformer",
        "parameters": {
            "channel": "3",
            "width": "227",
            "height": "227",
            "subtract_mean": "false"
        },
        "inputs": {
            "input": "Camera:bgr_output"
        }
    }
    ]
}

BASIC_NN = \
{
    "processor_name": "BaseNN",
    "processor_type": "NeuralNet",
    "parameters": {
        "start_layer": 1,
        "end_layer": 1,
    },
    "inputs": {
    }
}

BASIC_CLASSIFIER = \
{
    "processor_name": "Classifier",
    "processor_type": "ImageClassifier",
    "parameters": {
        "model": "Inception",
        "channel": "3",
        "batch_size": "1"
    },
    "inputs": {
    }
}

