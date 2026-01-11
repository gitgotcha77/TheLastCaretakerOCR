
dCropValues = {
    720 : '413:504:648:157',
    1080: '623:765:971:239',
    1440: '830:952:1297:316',
    2560: '1498:1804:2293:556',
}

dDefaultModels = {
    'openai':    'gpt-5-mini',
    'anthropic': 'claude-haiku-4-5',
    'google':    'gemini-2.5-flash',
    'mistral':   'mistral-medium-latest',
    'lmstudio':  'openai/gpt-oss-20b',
}

dLanguages = {
    'en': 'English, default',
    'de': 'Deutsch',
}


dTexts = {
    'en': {
        'default': 'default',
        'chat_prompt': """
I'm playing a game called "The Last Caretaker".
Help me to unravel the story in details.
In the game I've discovered story elements as data logs.
I've recorded a video navigating through all data log pages, and then extracted text from each frame.
So there might be duplicated or overlapping text parts.
Each new data log page starts with "========== frame_XXXX.jpg ==========".
The first line afterwards is always the chapter title.
The second line is the sub-chapter title.
The last line might be for page navigation, like "PgDn Scroll down" or "PgUp Scroll up", and can be ignored.
A data log entry might also include a date or year.
Try to put everything in chronological order by year and date and describe each chapter in details.
At last summarize the story plot.
Here're all data log entries from each frame:
""",
        'ocr_prompt':        'You are an OCR system. Extract all text in the image. '
                             'Return only the text, without any additional commentary, formatting or your thinking process. '
                             'Skip page navigation stuff at the bottom like "PgDn Scroll down" and "PgUp Scroll up".',
        'use_language':      'Selected language',
        'video_files':       'Found video files',
        'ask_video':         'Which video file should be used?',
        'missing_video':     'No video files found in the project directory and no --videoFile option was passed!',
        'use_video':         'Selected video',
        'ask_pps':           'How many pages per second in the video?',
        'use_pps':           'Entered pages per second',
        'ask_height':        'What is the height of your video?',
        'use_height':        'Entered height',
        'job_ffmpeg':        'Extracting frames from video',
        'done_ffmpeg':       'Extracted frames',
        'job_transcribing':  'Transcribing to',
        'note_transcribing': 'You can have a look at the file during the transcribe process',
        'done_transcribing': 'All text extracted and saved to',
        'ocrtxt_files':      'Found OCR-text files',
        'ask_ocrtxt':        'Which OCR-text file should be used?',
        'missing_ocrtxt':    'No OCR-text files found in the project directory and no --textFile option was passed!',
        'use_ocrtxt':        'Selected OCR-text',
        'providers':         'Available LLM providers',
        'ask_provider':      'Which provider do you want to use?',
        'missing_provider':  'Invalid provider specified and no --provider option was passed!',
        'use_provider':      'Selected provider',
        'ask_modelname':     'Enter which LLM you want to use',
        'use_modelname':     'Selected LLM',
        'history_file':      'File with your LLM chat history',
        'enter_prompt':      'Enter your next prompt (or quit/q/exit/e to exit)',
        'ask_ccv':           'Should I create a cropped video too? (This will NOT overwrite your current video) (y/N)',
        'ask_ccv_encoder':   'Your graphic cards GPU manufacturer (amd, nvidia, intel, no idea)',
        'use_ccv':           'Cropping video with FFMPEG ...',
        'ccv_file':          'Created video file',
    },
    'de': {
        'default': 'Standard',
        'chat_prompt': """
Ich spiele ein Spiel namens „The Last Caretaker”.
Hilf mir, die Geschichte im Detail zu entschlüsseln.
Im Spiel habe ich Story-Elemente in Form von Datenprotokollen entdeckt.
Ich habe ein Video aufgenommen, in dem ich durch alle Datenprotokollseiten navigiert bin, und dann den Text aus jedem Frame extrahiert.
Daher kann es zu doppelten oder sich überschneidenden Textteilen kommen.
Jede neue Datenprotokollseite beginnt mit „========== frame_XXXX.jpg ==========”.
Die erste Zeile danach ist immer der Titel des Kapitels.
Die zweite Zeile ist der Titel des Unterkapitels.
Die letzte Zeile kann für die Seitennavigation bestimmt sein, z.B. „PgDn Scroll down" oder "PgUp Scroll up“, und kann ignoriert werden.
Ein Datenprotokolleintrag kann auch ein Datum oder ein Jahr enthalten.
Versuche, alles chronologisch nach Jahr und Datum zu ordnen und jedes Kapitel detailliert zu beschreiben.
Fasse zum Schluss die Handlung der Geschichte zusammen.
Die Datenprotokolle sind in englischer Sprache, aber antworte immer auf Deutsch.
Hier sind alle Datenprotokolleinträge aus jedem Frame:
""",
        'ocr_prompt':        'You are an OCR system. Extract all text in the image. '
                             'Return only the text, without any additional commentary, formatting or your thinking process. '
                             'Skip page navigation stuff at the bottom like "PgDn Scroll down" and "PgUp Scroll up".',
        'use_language':      'Ausgewählte Sprache',
        'video_files':       'Gefundene Video-Dateien',
        'ask_video':         'Welche Video-Dateien soll verwendet werden?',
        'missing_video':     'Keine Video-Dateien im Projektverzeichnis gefunden und es wurde keine --videoFile Option angegeben!',
        'use_video':         'Ausgewählte Video-Datei',
        'ask_pps':           'Wie viele Seiten pro Sekunde im Video?',
        'use_pps':           'Eingegebene Seiten pro Sekunde',
        'ask_height':        'Wie gross ist die Höhe deines Videos?',
        'use_height':        'Eingegebene Höhe',
        'job_ffmpeg':        'Extrahiere Einzelbilder aus dem Videos',
        'done_ffmpeg':       'Anzahl an Bildern',
        'job_transcribing':  'Transkribiere nach',
        'note_transcribing': 'Du kannst dir die Datei während der Transkription bereits ansehen.',
        'done_transcribing': 'Der gesamte Text wurde extrahiert und gespeichert unter',
        'ocrtxt_files':      'Gefundene OCR-Text-Dateien',
        'ask_ocrtxt':        'Welche OCR-Text-Datei soll verwendet werden?',
        'missing_ocrtxt':    'Keine OCR-Text-Dateien im Projektverzeichnis gefunden und es wurde keine --textFile Option angegeben!',
        'use_ocrtxt':        'Ausgewählte OCR-Text-Datei',
        'providers':         'Verfügbare LLM-Anbieter',
        'ask_provider':      'Welchen Anbieter möchtest du nutzen?',
        'missing_provider':  'Ungültiger Anbieter und keine --provider Option angegeben!',
        'use_provider':      'Ausgewählter Anbieter',
        'ask_modelname':     'Gib ein, welches LLM du verwenden möchtest',
        'use_modelname':     'Ausgewähltes LLM',
        'history_file':      'Datei mit deinem LLM Chat Verlauf',
        'enter_prompt':      'Gib deine Frage ein (oder quit/q/exit/e um zu beenden)',
        'ask_ccv':           'Soll ich auch ein zugeschnittenes Video erstellen? (Deine Video-Datei wird NICHT überschrieben) (j/N)',
        'ask_ccv_encoder':   'Der Hersteller der GPU deiner Grafikkarte (amd, nvidia, intel, k.A.)',
        'use_ccv':           'Schneide Video mittels FFMPEG ...',
        'ccv_file':          'Erstellte Video-Datei',
    }
}
