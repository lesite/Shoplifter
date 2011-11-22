import mongoengine as db


def setup():
    db.connect('shoplifter_test')
