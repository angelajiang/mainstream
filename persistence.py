import redis

class Persistence():
    def __init__(self, db):
        self._db = db

    def add_app(self, app_uuid, dataset_uuid, name, acc_dev_percent):
        self._db.sadd('apps', app_uuid)
        app_acc_dev_key = "app:" + app_uuid + ":acc_dev_percent"
        self._db.set(app_acc_dev_key, acc_dev_percent)
        app_name_key = "app:" + app_uuid + ":name"
        self._db.set(app_name_key, name)
        app_dataset_key = "app:" + app_uuid + ":dataset_uuid"
        self._db.set(app_dataset_key, dataset_uuid)

    def add_dataset(self, dataset_uuid, accuracies_by_layer):
        self._db.sadd('datasets', dataset_uuid)
        for layer, accuracy in accuracies_by_layer.iteritems():
            dataset_acc_key = "dataset:" + dataset_uuid + ":acc:layer:" + str(layer)
            self._db.set(dataset_acc_key, accuracy)

    def train_dataset(self, name, image_dir, config_file):
        self._dataset_uuid = str(uuid.uuid4())[:8] # TODO: doesn't need to be global?
        self._db.sadd('datasets', self._dataset_uuid)

        # Train app with different numbers of layers frozen
        accuracies = self._helpers.get_accuracy_per_layer(self._dataset_uuid, image_dir, config_file, self._max_layers, 50, 0, True)

        for layer, accuracy in accuracies.iteritems():
            dataset_acc_key = "dataset:" + self._dataset_uuid + ":acc:layer:" + str(layer)
            self._db.set(dataset_acc_key, accuracy)

    def get_dataset_uuid_by_app_uuid(self, app_uuid):
        dataset_uuid = self._db.get("app:" + app_uuid + ":dataset_uuid")
        return dataset_uuid

    def get_app_uuids(self):
        app_uuids = self._db.smembers('apps')
        return app_uuids

    def get_app_name_by_app_uuid(self, app_uuid):
        app_name_key = "app:" + app_uuid + ":name"
        name = self._db.get(app_name_key)
        return name

    def get_acc_dev_by_app_uuid(self, app_uuid):
        app_acc_dev_key = "app:" + app_uuid + ":acc_dev_percent"
        acc_dev = float(self._db.get(app_acc_dev_key))
        return acc_dev

    def get_app_accuracies(self, app_uuid):
        accuracies = {}
        dataset_uuid = self.get_dataset_uuid_by_app_uuid(app_uuid)
        dataset_acc_keys = []
        dataset_acc_key_prefix = "dataset:" + dataset_uuid + ":acc:*"
        dataset_acc_keys = self._db.keys(dataset_acc_key_prefix)
        for dataset_acc_key in dataset_acc_keys:
            acc = float(self._db.get(dataset_acc_key))
            layer = int((dataset_acc_key.split(":"))[-1])
            accuracies[layer] = acc
        return accuracies

    def get_apps_accuracies(self):
        app_uuids = self.get_app_uuids()
        apps_accuracies = {}
        for app_uuid in app_uuids:
            apps_accuracies[app_uuid] = self.get_app_accuracies(app_uuid)
        return apps_accuracies

    def get_app_data(self, app_uuid):
        app_data = {} #name, acc_threshold, accuracies
        app_data["accuracies"] = self.get_app_accuracies(app_uuid)
        app_data["name"] = self.get_app_name_by_app_uuid(app_uuid)
        app_data["acc_dev_threshold"] = self.get_acc_dev_by_app_uuid(app_uuid)
        return app_data

