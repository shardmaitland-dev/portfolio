# translateAPI

RYU's Translation Engine.

## Powered by ArgosTranslate

Open-source offline translation library written in Python

Argos Translate uses OpenNMT for translations and can be used as either a Python library, command-line, or GUI application. Argos Translate supports installing language model packages which are zip archives with a ".argosmodel" extension containing the data needed for translation. LibreTranslate is an API and web-app built on top of Argos Translate.

Argos Translate also manages automatically pivoting through intermediate languages to translate between languages that don't have a direct translation between them installed. For example, if you have a es → en and en → fr translation installed you are able to translate from es → fr as if you had that translation installed. This allows for translating between a wide variety of languages at the cost of some loss of translation quality.

### Supported languages

Arabic, Azerbaijani, Catalan, Chinese, Czech, Danish, Dutch, English, Esperanto, Finnish, French, German, Greek, Hebrew, Hindi, Hungarian, Indonesian, Irish, Italian, Japanese, Korean, Persian, Polish, Portuguese, Russian, Slovak, Spanish, Swedish, Turkish, Ukrainian

## Installation using venv

Download a copy of this ArgosTranslate and install with pip.

```
git clone https://github.com/argosopentech/argos-translate.git
cd argos-translate
python -m venv env
source env/bin/activate
pip install -e .
```

### Clone Repo and copy and paste common files into root folder.

argos-translate foldwer will be created, copy from here to root
Check Differences

### Known Failures

- In Windows, need python 3.10 to install sentencepiece==0.1.99
- Error while building sentencepiece. Ensure that requirements.txt file has the latest versions installed.

```
ctranslate2==2.24.0
sentencepiece==0.1.99
stanza==1.1.1
```

- Error with webkitSpeechRecognition in Firefox
  **Update winter 2019**
  The linked bug report has been marked as fixed.

To enable the SpeechRecognition in Firefox Nightly > 72, go to about:config and switch the flags media.webspeech.recognition.enable and media.webspeech.recognition.force_enable to true.

However note this is an online service, which means you'll need an internet connection.

## Endpoints

### /updateIndex

Used to download any new language indexes.

```
[GET]: /updateIndex?from_code=es&to_code=en
```

### /Translate

Used to translate text passed, If there is no direct translate route, system will translate to common "en" before attempting to translate to requested lang.
For example _french -> dutch_ will first perform _french -> english_ then _english -> dutch_

```
[POST]: /translate

{
    "from_code":"en",
    "to_code":"es",
    "text":"Hello World!"
}

```

#### Cloud RUN Locally

https://cloud.google.com/run/docs/testing/local#gcloud-cli

```
gcloud beta code dev
```
