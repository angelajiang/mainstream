import keras

class LossHistory(keras.callbacks.Callback):
    def __init__(self, history_file, num_frozen, X_test, Y_test):
        self.num_epochs = 0
        self.num_frozen = num_frozen
        self.X_test = X_test
        self.Y_test = Y_test
        self.f = open(history_file, 'a+', 0)

    def on_train_begin(self, logs={}):
        self.num_epochs = 0

    def on_epoch_end(self, batch, logs={}):
        self.num_epochs += 1
        test_loss, test_acc = self.model.evaluate(self.X_test, self.Y_test, verbose=0)
        test_loss = str.format("{0:.4f}", test_loss)
        test_acc = str.format("{0:.4f}", test_acc)
        val_loss = logs.get('val_loss')
        val_loss = str.format("{0:.4f}", val_loss)
        val_acc = logs.get('val_acc')
        val_acc = str.format("{0:.4f}", val_acc)
        line = str(self.num_frozen) + "," + str(self.num_epochs) + "," + str(val_loss) + "," + str(val_acc) + "," + str(test_loss) + "," + str(test_acc) + "\n"
        self.f.write(line)
        self.f.flush()

class Yad2kLossHistory(keras.callbacks.Callback):
    def __init__(self, history_file, num_frozen):
        self.num_epochs = 0
        self.num_frozen = num_frozen
        self.f = open(history_file, 'a+', 0)

    def on_train_begin(self, logs={}):
        self.num_epochs = 0

    def on_epoch_end(self, batch, logs={}):
        val_loss = logs.get('val_loss')
        #val_loss = str.format("{0:.4f}", val_loss)

        self.num_epochs += 1

        line = "%d,%d,%s\n" % (self.num_frozen, self.num_epochs, val_loss)
        self.f.write(line)
        self.f.flush()
