from mycroft import MycroftSkill, intent_file_handler


class Apprise(MycroftSkill):
    def __init__(self):
        MycroftSkill.__init__(self)

    @intent_file_handler('apprise.intent')
    def handle_apprise(self, message):
        self.speak_dialog('apprise')


def create_skill():
    return Apprise()

