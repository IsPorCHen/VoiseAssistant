import random
import webbrowser
import pyttsx3
import speech_recognition
import json
import os
from vosk import Model, KaldiRecognizer
import wave

def swap_language(*args):
    print("Метод swap_language вызван!")  # Логируем вызов метода
    print(f"Текущий язык: {assistant.speech_language}")

    """Смена языка"""
    current_language = assistant.speech_language

    if current_language == "ru":
        assistant.speech_language = "en"
        assistant.recognition_language = "en-US"
        play_voice_assistant_speech("Я меняю язык на английский.")
    else:
        assistant.speech_language = "ru"
        assistant.recognition_language = "ru-RU"
        play_voice_assistant_speech("I am switching to Russian.")

    setup_assistant_voice()

def play_greetings(*args):
    if assistant.speech_language == "ru":
        play_voice_assistant_speech("Привет! Как я могу помочь?")
    else:
        play_voice_assistant_speech("Hi! Can i help you?")
    """Функция для проигрывания приветствия"""

def play_farewell_and_quit(*args):
    """Функция для прощания и выхода"""
    if assistant.speech_language == "ru":
        play_voice_assistant_speech("До свидания! Хорошего дня")
    else:
        play_voice_assistant_speech("Goodbye! Have a nice day!")
    exit()

def search_for_term_on_google(*args):
    """Поиск в Google"""
    search_term = " ".join(args)
    url = f"https://www.google.com/search?q={search_term}"
    webbrowser.get().open(url)
    if assistant.speech_language == "ru":
        play_voice_assistant_speech(f"Я ищу {search_term} в Google.")
    else:
        play_voice_assistant_speech(f"I seatch on {search_term} в Google.")

def drop_coin(*args):
    """Подбросить монетку"""
    result = "Орел" if random.choice([True, False]) else "Решка"
    play_voice_assistant_speech(f"Выпало: {result}")


# Загрузка команд из JSON
def load_commands_from_json():
    with open("commands.json", "r", encoding="utf-8") as f:
        return json.load(f)


# Глобальные переменные
commands = load_commands_from_json()
recognizer = speech_recognition.Recognizer()
microphone = speech_recognition.Microphone()
ttsEngine = pyttsx3.init()

class VoiceAssistant:
    """Настройки голосового ассистента"""
    name = ""
    sex = ""
    speech_language = ""
    recognition_language = ""


# Настройка голоса
def setup_assistant_voice():
    """
    Установка голоса по умолчанию (индекс может меняться в зависимости от настроек операционной системы)
    """
    voices = ttsEngine.getProperty("voices")

    if assistant.speech_language == "en":
        assistant.recognition_language = "en-US"
        if assistant.sex == "female":
            ttsEngine.setProperty("voice", voices[1].id)  # Microsoft Zira Desktop (English)
        else:
            ttsEngine.setProperty("voice", voices[2].id)  # Microsoft David Desktop (English)
    else:
        assistant.recognition_language = "ru-RU"
        ttsEngine.setProperty("voice", voices[0].id)  # Microsoft Irina Desktop (Russian)


# Проигрывание речи
def play_voice_assistant_speech(text_to_speech):
    ttsEngine.say(str(text_to_speech))
    ttsEngine.runAndWait()

def record_and_recognize_audio(*args: tuple):
    """
    Запись и распознавание аудио с использованием выбранного языка
    """
    with microphone:
        recognized_data = ""

        # Регулирование уровня окружающего шума
        recognizer.adjust_for_ambient_noise(microphone, duration=2)

        try:
            print("Listening...")
            audio = recognizer.listen(microphone, 5, 5)

            with open("microphone-results.wav", "wb") as file:
                file.write(audio.get_wav_data())

        except speech_recognition.WaitTimeoutError:
            print("Can you check if your microphone is on, please?")
            return ""

        try:
            print("Started recognition...")
            recognized_data = recognizer.recognize_google(audio, language=assistant.recognition_language).lower()
            print(f"Распознано: {recognized_data}")  # Выводим распознанный текст

        except speech_recognition.UnknownValueError:
            pass

        except speech_recognition.RequestError:
            print("Trying to use offline recognition...")
            recognized_data = use_offline_recognition()

        return recognized_data.strip()



def use_offline_recognition():
    recognized_data = ""
    try:
        if not os.path.exists("models/vosk-model-small-ru-0.4"):
            print("Please download the model from the specified URL and unpack it in the 'models' folder.")
            exit(1)

        wave_audio_file = wave.open("microphone-results.wav", "rb")
        model = Model("models/vosk-model-small-ru-0.4")
        offline_recognizer = KaldiRecognizer(model, wave_audio_file.getframerate())

        data = wave_audio_file.readframes(wave_audio_file.getnframes())
        if len(data) > 0:
            if offline_recognizer.AcceptWaveform(data):
                recognized_data = offline_recognizer.Result()
                recognized_data = json.loads(recognized_data)
                recognized_data = recognized_data["text"]
    except:
        print("Error with offline speech recognition.")
    
    return recognized_data

def execute_command_with_name(command_name: str, *args: list):
    print(f"Ищем команду: {command_name}")  # Логирование полученной команды

    for key, command in commands.items():
        print(f"Проверка команд: {command_name} в {command['examples']}")  # Логирование примеров команды

        # Проверяем, содержит ли примеры команд введенную команду
        if any(command_name in example for example in command["examples"]):
            print(f"Команда {command_name} найдена, выполняем {command['responses']}")  # Логируем, что команда найдена

            function_name = command["responses"]
            if function_name in globals():
                globals()[function_name](*args)

            if "responses_voice" in command:
                # play_voice_assistant_speech(command["responses_voice"])
                break
    else:
        print("Команда не найдена.")
        play_voice_assistant_speech("Извините, я вас не понял")



if __name__ == "__main__":
    assistant = VoiceAssistant()
    assistant.name = "Alice"
    assistant.sex = "female"
    assistant.speech_language = "ru"

    setup_assistant_voice()

    while True:
        voice_input = record_and_recognize_audio()
        os.remove("microphone-results.wav")
        print(f"Вы сказали: {voice_input}")

        # Если команда пуста, пропускаем итерацию
        if not voice_input:
            continue

        # Разделение команды и дополнительных параметров
        voice_input = voice_input.split(" ")
        command = voice_input[0]
        command_options = voice_input[1:]

        # Выполнение команды с голосовым ответом
        execute_command_with_name(command, *command_options)

