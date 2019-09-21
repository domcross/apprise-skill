from mycroft import MycroftSkill, intent_file_handler
from mycroft.util.parse import match_one
import apprise


class Apprise(MycroftSkill):
    def __init__(self):
        self.apobj = None
        self.services = {}
        MycroftSkill.__init__(self)

    def initialize(self):
        self._setup()
        self.settings.set_changed_callback(self.on_websettings_changed)
        self.register_entity_file('someone.entity')

    def on_websettings_changed(self):
        self.log.debug("websettings changed!")
        self._setup()

    def _setup(self):
        self.apobj = apprise.Apprise()
        self.services = {}
        for i in range(1, 4):
            name = self.settings.get("name{}".format(i), "")
            service = self.settings.get("service{}".format(i), "")
            if name and service:
                self.log.info("%s - %s" % (name, service))
                self.services[name.lower()] = service
                self.apobj.add(service, tag=name)

    @intent_file_handler('apprise.intent')
    def handle_apprise(self, message):
        if not self.services:
            self.speak("error")
            return

        #self.log.info(message.data)
        someone = message.data.get("someone")
        something = message.data.get("something")
        self.log.info("%s - %s" % (someone, something))

        best_match, score = match_one(someone.lower(), self.services)
        self.log.info("%s - %s" % (best_match, score))
        if score > 0.9:
            self.apobj.notify(something, title=something, tag=best_match)
            self.speak_dialog('apprise', {'someone': someone})


def create_skill():
    return Apprise()

