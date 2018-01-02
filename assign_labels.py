import io


def transcribe(content):
    from google.cloud import speech
    from google.cloud.speech import enums
    from google.cloud.speech import types
    client = speech.SpeechClient()

    audio = types.RecognitionAudio(content=content)
    config = types.RecognitionConfig(
        encoding=enums.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=16000,
        language_code='ka-GE')
    response = client.recognize(config, audio)
    for result in response.results:
        print('Transcript: {}'.format(result.alternatives[0].transcript))
        return result


from google.cloud import storage
import audioop
import wave
import os

storage_client = storage.Client()
bucket_name = 'ge-open-speech-recording.appspot.com'
bucket = storage_client.get_bucket(bucket_name)


def do_labeling():
    blobs = bucket.list_blobs(prefix="wav")
    for blob in blobs:
        if blob.name == "wav/":
            continue
        print(blob.name)
        key = os.path.splitext(blob.name)[0][4:]
        sound_key = ds.key("Sound", key)
        sound = ds.get(sound_key)
        if sound:
            print("Already classified:", key)
            continue
        file_name = "current.wav"
        try:
            os.remove(file_name)
        except os.error:
            pass
        blob.download_to_filename(file_name)
        wave_file = wave.open(file_name, 'r')
        length = wave_file.getnframes()
        wave_data = wave_file.readframes(length)
        state = None
        content, state = audioop.ratecv(wave_data, 2, 1, 48000, 16000, state)

        result = transcribe(content)
        os.remove(file_name)

        label = key.split("_", 1)[0]
        sound = datastore.Entity(key=sound_key)
        #soundidentifier = key
        sound["label_translit"] = label
        if result and result.alternatives and len(result.alternatives) > 0:
            sound["google_transcript"] = result.alternatives[0].transcript
            sound["google_confidence"] = result.alternatives[0].confidence
        sound["label_ge"] = get_label_ge(label)
        # sound['raw'] = content
        ds.put(sound)
        print("Saved:", sound)

def assign_randoms():
    result = ds.query(kind="Sound")
    for entry in result:
        print(entry)


words = [
    'ნოლი',
    'ერთი',
    'ორი',
    'სამი',
    'ოთხი',
    'ხუთი',
    'ექვსი',
    'შვიდი',
    'რვა',
    'ცხრა',
    'ჩართე',
    'გამორთე',
    'სდექ',
    'მიდი',
    'წადი',
    'ზემოთ',
    'ქვემოთ',
    'მარცხნივ',
    'მარჯვნივ',
    'კი',
    'დიახ',
    'ჰო',
    'არა',
    'გააღე',
    'დაკეტე',
    'დახურე',
    'გააღე',
    'დარეკე',
    'კატა',
    'ჩიტი',
    'ხე',
    'მაყვალა',
    'ჯუმბერი',
];

toAsciiMap = {
    'ი': 'i',
    'ე': 'e',
    'ა': 'a',
    'ო': 'o',
    'უ': 'u',

    'პ': 'p',
    'ფ': 'f',
    'ბ': 'b',
    'ვ': 'v',
    'მ': 'm',

    'ტ': 't',
    'თ': 'T',
    'დ': 'd',
    'ნ': 'n',
    'ს': 's',
    'ზ': 'z',
    'წ': 'w',
    'ც': 'c',
    'ძ': 'Z',
    'ჯ': 'j',
    'ჩ': 'C',
    'ჭ': 'W',
    'შ': 'S',
    'ჟ': 'J',
    'რ': 'r',
    'ლ': 'l',

    'კ': 'k',
    'ქ': 'q',
    'გ': 'g',
    'ღ': 'R',
    'ხ': 'x',

    'ყ': 'y',
    'ჰ': 'h'
}

word_translits = {}


def get_translit(word):
    result = ""
    for ch in word:
        result += toAsciiMap[ch]
    return result


for word in words:
    translit = get_translit(word)
    word_translits[translit] = word


def get_label_ge(label_translit):
    return word_translits[label_translit]



from google.cloud import datastore

ds = datastore.Client("ge-open-speech-recording")

def label_dir(dir_name):
    files = os.listdir(dir_name)
    for file_name in files:
        key = os.path.splitext(file_name)[0]
        sound = ds.get(sound_key)
        if sound:
            print("Already classified:", key)
            continue
        try:
            wave_file = wave.open(dir_name + "/" + file_name, 'r')
        except:
            print("Error:", file_name)
            continue
        length = wave_file.getnframes()
        wave_data = wave_file.readframes(length)
        state = None
        content, state = audioop.ratecv(wave_data, 2, 1, 48000, 16000, state)
        result = transcribe(content)
        print (result)

        label = file_name.split("_", 1)[0]

        sound = Sound()
        sound.identifier = key
        sound.label_translit = label
        if result and result.alternatives and len(result.alternatives) > 0:
            sound.google_transcript = result.alternatives[0].transcript
            sound.google_confidence = result.alternatives[0].confidence
        sound.label_ge = get_label_ge(label)
        # sound['raw'] = content
        sound.put()
        print("Saved:", sound)


def from_datastore(entity):
    if not entity:
        return None

    if isinstance(entity, list):
        entity = entity.pop()

    entity['id'] = entity.key.id
    return entity


digit2word = {
    "0": 'ნოლი',
    "1": 'ერთი',
    "2": 'ორი',
    "3": 'სამი',
    "4": 'ოთხი',
    "5": 'ხუთი',
    "6": 'ექვსი',
    "7": 'შვიდი',
    "8": 'რვა',
    "9": 'ცხრა',
}

import random

def machine_vote():
    counter = 0
    ok_counter = 0

    query = ds.query(kind='Sound')
    result = query.fetch()
    for page in result.pages:
        # page = next(result.pages)
        for sound in page:
            counter += 1
            transcript = "-"
            if 'google_transcript' in sound:
                transcript = sound['google_transcript']
                if transcript in digit2word:
                    sound['google_transcript'] = digit2word[transcript]
                    transcript = sound['google_transcript']
            if transcript == sound['label_ge']:
                sound['vote'] = 5
                ok_counter += 1
            else:
                sound['vote'] = 0
            sound["rnd_pos"] = random.randint(1, 100000)
            ds.put(sound)
            print(sound['vote'])
    print (counter, ok_counter)

do_labeling()
#label_dir("../conversion/wav")
machine_vote()
#get_to_vote()

