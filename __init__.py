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
                self.apobj.add(service, tag=name.lower())

    @intent_file_handler('apprise.intent')
    def handle_apprise(self, message):
        if not self.services:
            self.speak_dialog('setup.error')
            return
        all_keyword = self.translate("AllKeyword").lower()
        names = list(self.services.keys())
        names.append(all_keyword)
        self.log.info("names %s" % names)
        # self.log.info(message.data)
        someone = message.data.get("someone")
        something = message.data.get("something")
        self.log.info("%s - %s" % (someone, something))

        name, score = match_one(someone.lower(), names)
        self.log.info("%s - %s" % (name, score))
        if score > 0.9:
            if name == all_keyword:
                success = self.apobj.notify(something, title=something)
            else:
                success = self.apobj.notify(something, title=something, tag=name)
            self.log.info("result %s" % success)
            if success:
                self.speak_dialog('apprise', {'someone': name})
            else:
                self.speak_dialog('send.error', {'someone': name})


def create_skill():
    return Apprise()

