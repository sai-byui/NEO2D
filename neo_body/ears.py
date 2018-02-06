import speech_recognition
from agent import Agent

PHRASE_TIME_LIMIT = 4.0  # each phrase will run 4 seconds before the microphone stops processing audio

# This is where we can put our verbal keywords commands
# all words must be lower case to be recognized
KEYWORDS = (("hello neo", .3), ("walk forward", .3), ("good evening mister anderson", .3), )


""" Syntax notes for important SpeechRecognition functions

recognizer_instance.listen(
source: AudioSource,
timeout: Union[float, None] = None,
phrase_time_limit: Union[float, None] = None,
snowboy_configuration: Union[Tuple[str, Iterable[str]], None] = None
) -> AudioData

recognizer_instance.recognize_sphinx(
audio_data: AudioData,
language: str = "en-US",
keyword_entries: Union[Iterable[Tuple[str, float]], None] = None,
grammar: Union[str, None] = None, show_all: bool = False
) -> Union[str, pocketsphinx.pocketsphinx.Decoder]

Link to SpeechRecognition reference library:
https://github.com/Uberi/speech_recognition/blob/master/reference/library-reference.rst
"""


class Ears(Agent):
    """The listening agent of the program. The ears take in audio input and recognize speech commands
        This agent uses the SpeechRecognition library with pocketsphinx to process phrases offline"""

    def __init__(self):
        """default constructor"""
        super(Ears, self).__init__("ears")
        # this object contains all the methods for working with speech recognition
        self.recognizer = speech_recognition.Recognizer()
        # the system microphone
        self.microphone = speech_recognition.Microphone()
        with self.microphone as source:
            # when the program first starts, the ears listen for ambient noise so it can distinguish it from actual speech
            print("Please wait. Calibrating microphone...")
            self.recognizer.adjust_for_ambient_noise(source, 5)
            # this allows the ears to adjust its energy threshold levels as the program runs
            self.recognizer.dynamic_energy_threshold = True
            print("Say something!")
            audio = self.recognizer.listen(self.microphone, None, PHRASE_TIME_LIMIT)
        # recognize speech using Sphinx
        try:
            print("NEO heard '" + self.recognizer.recognize_sphinx(audio, "en-US", KEYWORDS, None, False) + "'")
        except speech_recognition.UnknownValueError:
            print("NEO could not understand audio")
        except speech_recognition.RequestError as e:
            print("Sphinx error; {0}".format(e))

    def listen(self):
        while True:
            with self.microphone as source:
                audio = self.recognizer.listen(self.microphone)
                try:
                    print("NEO heard '" + self.recognizer.recognize_sphinx(audio) + "'")
                except speech_recognition.UnknownValueError:
                    print("NEO could not understand audio")
                except speech_recognition.RequestError as e:
                    print("Sphinx error; {0}".format(e))
