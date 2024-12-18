import speech_recognition as sr
import os
import time
import re

recognizer = sr.Recognizer()

def listen():
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source, duration=0.5)  # Ajusta para o ruído ambiente
        print("Diga algo...")
        #audio = recognizer.listen(source, timeout=3, phrase_time_limit=6)  # Limita o tempo de escuta
        audio = recognizer.listen(source, phrase_time_limit=8)
        t = time.localtime()
        current_time = time.strftime("%H:%M:%S", t)
        print(current_time)
        try:
            command = recognizer.recognize_google(audio, language='pt-BR')
            print(f"Você disse: {command}")
            return command
        except sr.UnknownValueError:
            print("Não entendi o que você disse.")
            return ""
        except sr.RequestError:
            print("Erro ao se comunicar com o serviço de reconhecimento de voz.")
            return ""

def parse_input(input_string, field_names):
    # Create a pattern to match field names
    pattern = r"|".join(re.escape(field) for field in field_names)
    
    # Initialize a dictionary with field names set to empty strings
    fields = {field: '' for field in field_names}
    
    # Use regex to find all occurrences of field names
    matches = re.finditer(pattern, input_string)
    
    # Extract the positions of the matches
    field_positions = [(match.start(), match.group()) for match in matches]
    
    # Add an end position for the last field
    field_positions.append((len(input_string), ''))
    
    # Extract and map values to their respective fields
    for i in range(len(field_positions) - 1):
        start_pos, field_name = field_positions[i]
        end_pos = field_positions[i + 1][0]
        value = input_string[start_pos + len(field_name):end_pos].strip()
        if field_name in fields:
            fields[field_name] = value
    
    return fields

field_names = ["NOME", "IDADE", "TELEFONE", "PROFISSÃO"]

command = ""

while command != "ENCERRAR":
    command = listen().upper()  # string

    output = parse_input(command, field_names)
    print("Output for input:", output)