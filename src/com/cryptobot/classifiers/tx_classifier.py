from com.cryptobot.classifiers.classifier import Classifier


class TXClassifier(Classifier):
    def parse(self, items):
        pass

    def filter(self, items):
        pass

    def classify(self, items) -> object:
        items = self.parse(items)
        items = self.filter(items)

        return items
