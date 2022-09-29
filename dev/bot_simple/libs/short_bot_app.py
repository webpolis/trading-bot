import json
import scheduler as sch
import token_


class ShortBotApp:
    def __init__(self, config, whale_number, page_number, last_date, freq):
        self._scheduler = sch.Scheduler(config)
        self.tokens = {}
        for token_, symbol in zip(config["tokens"]["name"], config["tokens"]["symbol"]):
            self.tokens[token_] = token_.Token(name=token_, symbol=symbol, whale_number=whale_number)


    def launch(self):
        self.start()

    def start(self):
        # self._scheduler.run(self.pooles)
        self._scheduler.job(self.tokens)

    def stop(self):
        pass

if __name__ == '__main__':
    with open('/home/agustin/Git-Repos/Short-bot/config/config.json') as json_file:
        config = json.load(json_file)
    app = ShortBotApp(config).launch()