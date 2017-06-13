from config import config_dict

import unittest

import os.path
import shutil

import keras

import tensorflow as tf

from src.classifiers.cnn import CNN
from src.classifiers.utils import save_classifier, load_classifier
from src.utils import load_cifar10, load_mnist, make_directory, set_group_permissions_rec

class TestCNNModel(unittest.TestCase):

    def setUp(self):
        make_directory("./tests/")

    def tearDown(self):
        shutil.rmtree("./tests/")

    def test_cifar(self):

        BATCH_SIZE = 10
        NB_TRAIN = 1000
        NB_TEST = 100

        session = tf.Session()
        keras.backend.set_session(session)

        # get CIFAR10
        (X_train, Y_train), (X_test, Y_test) = load_cifar10()
        X_train, Y_train, X_test, Y_test = X_train[:NB_TRAIN], Y_train[:NB_TRAIN], X_test[:NB_TEST], Y_test[:NB_TEST]

        im_shape = X_train[0].shape

        classifier = CNN(im_shape, act="brelu")

        classifier.compile({'loss':'categorical_crossentropy', 'optimizer':'adam', 'metrics':['accuracy']})

        # Fit the classifier
        classifier.fit(X_train, Y_train, epochs=1, batch_size=BATCH_SIZE)

        scores = classifier.evaluate(X_test, Y_test)

        print("\naccuracy: %.2f%%" % (scores[1] * 100))


    def test_mnist(self):

        BATCH_SIZE = 10
        NB_TRAIN = 1000
        NB_TEST = 100

        session = tf.Session()
        keras.backend.set_session(session)

        # get MNIST
        (X_train, Y_train), (X_test, Y_test) = load_mnist()
        X_train, Y_train, X_test, Y_test = X_train[:NB_TRAIN], Y_train[:NB_TRAIN], X_test[:NB_TEST], Y_test[:NB_TEST]

        im_shape = X_train[0].shape

        classifier = CNN(im_shape, act="relu")

        classifier.compile({'loss':'categorical_crossentropy', 'optimizer':'adam', 'metrics':['accuracy']})

        # Fit the classifier
        classifier.fit(X_train, Y_train, epochs=1, batch_size=BATCH_SIZE)

        scores = classifier.evaluate(X_test, Y_test)

        print("\naccuracy: %.2f%%" % (scores[1] * 100))

    def test_cnn_brelu(self):

        BATCH_SIZE = 10
        NB_TRAIN = 1000
        NB_TEST = 100

        session = tf.Session()
        keras.backend.set_session(session)

        # get MNIST
        (X_train, Y_train), (X_test, Y_test) = load_mnist()
        X_train, Y_train, X_test, Y_test = X_train[:NB_TRAIN], Y_train[:NB_TRAIN], X_test[:NB_TEST], Y_test[:NB_TEST]

        im_shape = X_train[0].shape

        classifier = CNN(im_shape,act="brelu", act_params={"alpha": 1, "max_value": 2})

        classifier.compile({'loss':'categorical_crossentropy', 'optimizer':'adam', 'metrics':['accuracy']})

        # Fit the classifier
        classifier.fit(X_train, Y_train, epochs=1, batch_size=BATCH_SIZE)

        act_config = classifier.model.layers[1].get_config()

        self.assertEquals(act_config["alpha"], 1)
        self.assertEquals(act_config["max_value"], 2)

    def test_cnn_batchnorm(self):

        BATCH_SIZE = 10
        NB_TRAIN = 1000
        NB_TEST = 100

        session = tf.Session()
        keras.backend.set_session(session)

        # get MNIST
        (X_train, Y_train), (X_test, Y_test) = load_mnist()
        X_train, Y_train, X_test, Y_test = X_train[:NB_TRAIN], Y_train[:NB_TRAIN], X_test[:NB_TEST], Y_test[:NB_TEST]

        im_shape = X_train[0].shape

        classifier = CNN(im_shape,act="relu", bnorm=True)

        classifier.compile({'loss':'categorical_crossentropy', 'optimizer':'adam', 'metrics':['accuracy']})

        # Fit the classifier
        classifier.fit(X_train,Y_train,epochs=1,batch_size=BATCH_SIZE)

        bnorm_layer = classifier.model.layers[2]

        self.assertIsInstance(bnorm_layer, keras.layers.normalization.BatchNormalization)


    def test_save_load_model(self):
        BATCH_SIZE = 10
        NB_TRAIN = 100
        NB_TEST = 10

        comp_params = {"loss":'categorical_crossentropy',
                       "optimizer":'adam',
                       "metrics":['accuracy']}

        session = tf.Session()
        keras.backend.set_session(session)

        # get MNIST
        (X_train, Y_train), (X_test, Y_test) = load_mnist()
        X_train, Y_train, X_test, Y_test = X_train[:NB_TRAIN], Y_train[:NB_TRAIN], X_test[:NB_TEST], Y_test[:NB_TEST]

        im_shape = X_train[0].shape

        classifier = CNN(im_shape, act="brelu")

        classifier.compile(comp_params)

        # Fit the classifier
        classifier.fit(X_train, Y_train, epochs=1, batch_size=BATCH_SIZE)

        path = "./tests/save/cnn/"
        # test saving
        save_classifier(classifier, path)

        if config_dict["profile"] == "CLUSTER":
            set_group_permissions_rec(path)

        self.assertTrue(os.path.isfile(path + "model.json"))
        self.assertTrue(os.path.getsize(path + "model.json") > 0)
        self.assertTrue(os.path.isfile(path + "weights.h5"))
        self.assertTrue(os.path.getsize(path + "weights.h5") > 0)

        #test loading
        loaded_classifier = load_classifier(path)

        scores = classifier.evaluate(X_test, Y_test)
        scores_loaded = loaded_classifier.evaluate(X_test, Y_test)

        self.assertAlmostEqual(scores, scores_loaded)

if __name__ == '__main__':
    unittest.main()
