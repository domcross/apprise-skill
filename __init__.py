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
        self.log.info("%s - %s" % (tags, configfile))
        if tags and configfile:
            if configfile[:1] != "/":
                configfile = "/opt/mycroft/skills/apprise-skill/" + configfile
            self.log.info("configfile - %s" % configfile)
            if os.path.isfile(configfile):
                self.log.info("is file: %s" % configfile)
                config = apprise.AppriseConfig()
                config.add(configfile)
                self.apobj.add(config)
                taglist = tags.split(",")
                self.log.info("taglist: %s" % taglist)
                for t in taglist:
                    self.tags[t.strip().lower()] = t.strip()
            else:
                self.log.info("no such file: %s" % configfile)
        # second load tags and service-urls from settings
        for i in range(1, 4):
            tag = self.settings.get("tag{}".format(i), "")
            service = self.settings.get("service{}".format(i), "")
            if tag and service:
                self.tags[tag.lower()] = tag
                self.apobj.add(service, tag=tag)

        self.log.info("tags - %s" % self.tags)
        #self.log.info("urls - %s" % self.apobj.urls())


    @intent_file_handler('apprise.intent')
    def handle_apprise(self, message):
        if not self.tags:
            self.speak_dialog('setup.error')
            return
        all_keyword = self.translate("AllKeyword")
        tags = self.tags
        tags[all_keyword.lower()] = all_keyword
        self.log.info("tags %s" % tags)
        tag = message.data.get("tag")
        text = message.data.get("text")
        self.log.info("%s - %s" % (tag, text))

        best_tag, score = match_one(tag.lower(), tags)
        self.log.info("%s - %s" % (best_tag, score))
        if score > 0.9:
            if best_tag == all_keyword:
                success = self.apobj.notify(text, title=text)
            else:
                success = self.apobj.notify(text, title=text, tag=best_tag)
            self.log.info("result %s" % success)
            if success:
                self.speak_dialog('apprise', {'tag': best_tag})
            else:
                self.speak_dialog('send.error', {'tag': best_tag})


def create_skill():
    return Apprise()
