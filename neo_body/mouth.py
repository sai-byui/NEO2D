from agent import Agent
# import pyttsx3


class Mouth(Agent):
    """The speaking agent of the program"""

    def __init__(self):
        """default constructor"""
        super(Mouth, self).__init__("mouth")
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 150)  # 150 words per minute
        self.engine.setProperty('volume', 0.9)
        self.engine.say("HELLO WORLD, my name is neo!")
        self.engine.runAndWait()

        self.object_detection_notified = False
        self.inspection_message_spoken = False

    def list_similar_objects(self):
        if self.ask("wernicke_area", "correct_syntax") and not self.ask("wernicke_area", "answer_unknown"):
            object_list = self.ask("brain", "list_of_objects")
            for obj in object_list:
                print(obj[0])
        else:
            print("I don't know")

    def state_current_position(self):
        position = self.ask("neo", "position")
        self.speak("My current position is " + str(position))

    def identify_detected_object(self, sentence):
        if not self.object_detection_notified:
            self.engine.say(sentence)
            self.object_detection_notified = True

    def speak(self, sentence):
        self.engine.say(sentence)
        if not self.engine._inLoop:
            self.engine.startLoop()

    def stopSentence(self):
        if self.engine.isBusy():
            self.engine.stop()

