from mycroft import MycroftSkill, intent_file_handler
from mycroft.util.parse import match_one
import apprise
import os.path


class Apprise(MycroftSkill):
    def __init__(self):
        self.apobj = None
        self.tags = []
        MycroftSkill.__init__(self)

    def initialize(self):
        self._setup()
        self.settings.set_changed_callback(self.on_websettings_changed)
        self.register_entity_file('tag.entity')

    def on_websettings_changed(self):
        self.log.debug("websettings changed!")
        self._setup()

    def _setup(self):
        self.apobj = apprise.Apprise()
        self.tags = {}
        # first load configfile if specified
        tags = self.settings.get("tags", "")
        configfile = self.settings.get("configfile", "")
        self.log.debug("%s - %s" % (tags, configfile))
        if tags and configfile:
            if configfile[:1] != "/":
                configfile = "/opt/mycroft/skills/apprise-skill/" + configfile
            self.log.debug("configfile - %s" % configfile)
            if os.path.isfile(configfile):
                config = apprise.AppriseConfig()
                config.add(configfile)
                self.apobj.add(config)
                taglist = tags.split(",")
                self.log.debug("taglist: %s" % taglist)
                for t in taglist:
                    self.tags[t.strip().lower()] = t.strip()
            else:
                self.log.warn("config file does not exist: %s" % configfile)
        # second load tags and service-urls from settings
        for i in range(1, 4):
            tag = self.settings.get("tag{}".format(i), "")
            service = self.settings.get("service{}".format(i), "")
            if tag and service:
                self.tags[tag.lower()] = tag
                self.apobj.add(service, tag=tag)

        self.log.debug("tags - %s" % self.tags)

    @intent_file_handler('apprise.intent')
    def handle_apprise(self, message):
        if not self.tags:
            self.speak_dialog('setup.error')
            return
        all_keyword = self.translate("AllKeyword")
        tags = self.tags
        tags[all_keyword.lower()] = all_keyword
        self.log.debug("tags %s" % tags)
        tag = message.data.get("tag")
        text = message.data.get("text")
        self.log.debug("tag: %s - text: %s" % (tag, text))

        success = False
        best_tag, score = match_one(tag.lower(), tags)
        self.log.debug("%s - %s" % (best_tag, score))
        if score > 0.9:
            if best_tag == all_keyword:
                success = self.apobj.notify(text, title=text)
            else:
                success = self.apobj.notify(text, title=text, tag=best_tag)
            self.log.debug("result %s" % success)
        if success:
            self.speak_dialog('send.success', {'tag': best_tag})
        else:
            self.speak_dialog('send.error', {'tag': best_tag})


def create_skill():
    return Apprise()
