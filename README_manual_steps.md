
## Manual step: software dependencies
I've created two scripts:
 - `ocr_local.py`: extract text from a video recording of TLC data log entries.
 - `llm_chat.py`: pass the extracted text to a local or online LLM.

You need `GIT`, `FFMPEG`, `Python` and some Python packages.<br>
I'm using Python 3.13, but 3.11 or 3.12 should be ok too.<br>

For Linux distros just use the distros package manager to install FFMPEG, Python and GIT.

For Windows have a look here:
 - [FFMPEG](https://github.com/BtbN/FFmpeg-Builds/releases)
 - [Python](https://www.python.org/downloads/windows/)
 - [Github Desktop](https://desktop.github.com/download/)


## Manual step: get this project / GIT checkout
```
got clone https://github.com/gitgotcha77/thelastcaretaker_ocr.git
cd thelastcaretaker_ocr
```
On Windows use Github Desktop.


## Manual step: Python VENV setup
For virtual environment I use `uv` and `venv`.<br>
Have a look [here](https://pypi.org/project/uv/) on how to install `uv`.

Now let's create a venv for this project:
```
uv venv venv_p313_tlc_ocr --python 3.13 --seed --no-project
```

The directory `venv_p313_tlc_ocr` will be created inside `thelastcaretaker_ocr`.

Activate the VENV:
 - Linux `source venv_p313_tlc_ocr/bin/activate`
 - Windows `call venv_p313_tlc_ocr\bin\activate.bat`
```
uv pip install -r requirements.txt
```


## Manual step: start OCR process
```
python ocr_local.py --videoFile SOME_VIDEO_RECORDING_of_DataLogs.mkv
```
This will create a text file called `SOME_VIDEO_RECORDING_of_DataLogs.mkv.ocr.txt`.

Depending on your hardware and the used model, this can take 30 minutes, or even more.

Models I've tested with my LM Studio setup:

|             Model name |   Performance   |   Note    |
|-----------------------:|:---------------:|:---------:|
|       qwen/qwen3-vl-8b | ~  2s per frame |           |
|      qwen/qwen3-vl-30b | ~  3s per frame | needs 24G |
|     google/gemma-3-27b | ~ 14s per frame | needs 24G |
| zai-org/glm-4.6v-flash | ~  4s per frame |           |

Those are performance numbers on my system (nVidia RTX 4090),<br>
BUT I also noticed a difference when using LM Studio on Linux (my system is Mint 22.2) vs Windows 11.<br>
Some models run faster on Windows, some faster on Linux.<br>
I'm not sure if there's a minimum requirement of context window for the OCR process, but I used 10k for every model.

The default system prompt for the model:
```
You are an OCR system. Extract all text visible in the image. 
Return only the text, without any additional commentary, formatting or your thinking process.
Skip the page navigation stuff at the bottom like 'PgDn Scroll down' and 'PgUp Scroll up'.
```

Of course, you can use a different system prompt, f.e. in german.

If you want to use a different model for OCR, call the script like this:
```
python ocr_local.py --videoFile SOME_VIDEO_RECORDING_of_DataLogs.mkv --modelName "glm-4.6v-flash@q4_k_m" --transcribeFile TRANSCRIBE_FILE.glm46v.en.txt
```
To see all possible arguments/options use:
```
python ocr_local.py --help
```

The created text file should look like this:
```
========== frame_0001.jpg ==========
Final Static 1/5
Waiting for lost answers

Page 217: "The Signal" (March 4, 2096)

Jonah barely speaks anymore. His voice is thin, his breaths shallow, but when the radio crackles, his eyes still flicker with something—belief, maybe. Or habit. I don't know anymore.

"EMERGENCY PROTOCOL TR-4 | STATUS: PENDING" "DEPARTURE SEQUENCE 34-X | FINAL CLEARANCE REQUIRED"

...

========== frame_0002.jpg ==========
...
```

The file size should be about 200k and contain all data log entries.


## Manual step: analyze story with LM Studio
Ok ... as I said in the beginning, LLMs are very memory hungry and for the final analysis we need a big context window (Context Length).<br>
We need at least 60k to fit the whole TXT file.<br>
So if you want to do that step locally, you also need a model which supports a big context window.

# !!! DO NOT DRAG AND DROP THE TXT FILE INTO LM STUDIO CHAT !!!
> Why not?<br>
> LM Studio starts to index the file, and it looks ok?

When you do this, LM Studio will show you `rag-v1` below the input area.<br>
In our case this is bad. I'll not go into details what RAG is or what it can do and for what cases it is useful.<br> 

**tl;dr:** RAG will kind of split up the TXT file and the LLM will NOT *see* all data log entries.<br>
Well that's bad if the LLM should *understand* the whole story.<br>

What you can and should do is copy and paste the whole TXT file in the input area.

Here's a totally-incomplete list of LLM models I know:

| LLM model name       | Max. context length | Memory usage  |
|----------------------|---------------------|---------------|
| GPT OSS 20B          | 128k                | ~20G with 80k |
| Ministral 3 14B      | 256k                | ~20G with 80k |
| Gemma 3 27B          | 256k                | ~60G with 80k |
| Gemma 3 12B          | 128k                | ~42G with 80k |
| Llama 3.1 8B         | 128k                | ~14G with 80k |
| Phi 4 Mini Reasoning | 128k                | ~13G with 80k |
| SmolLM 3 3B          | 64k                 | ~7G with 64k  |

The thing is: which one will fit with 60k+ context length?<br>
On my 4090 I used `gpt-oss-20b` with 80k, so I could also ask some more questions about the story.<br>

Ok, so how do I do it right?

First write what you want the LLM to do, your `system prompt`, f.e. something like this:

**EN / English**
```
I'm playing a game called "The Last Caretaker".
Help me to unravel the story in details.
In the game I've discovered story elements as data logs.
I've recorded a video navigating through all data log pages, and then extracted the text from each frame.
So there might be duplicated or overlapping text parts.
Each new data log page starts with "========== frame_XXXX.jpg ==========".
The first line afterwards is always the chapter title.
The second line is the sub-chapter title.
The last line might be for page navigation like "PgDn Scroll down" and "PgUp Scroll up", which can be ignored.
A data log entry might also include a date or year.
Try to put everything in chronological order by date and describe each chapter in details.
At last summarize the story plot.
Here're all text log entries from each frame:
```
**DE / Deutsch**
```
Ich spiele ein Spiel namens „The Last Caretaker”.
Hilf mir, die Geschichte im Detail zu entschlüsseln.
Im Spiel habe ich Story-Elemente in Form von Datenprotokollen entdeckt.
Ich habe ein Video aufgenommen, in dem ich alle Datenprotokollseiten durchgehe, und danach den Text aus jedem Frame extrahiert.
Daher kann es zu doppelten oder sich überschneidenden Textteilen kommen.
Jede neue Datenprotokollseite beginnt mit „========== frame_XXXX.jpg ==========”.
Die erste Zeile danach ist immer der Titel des Kapitels.
Die zweite Zeile ist der Titel des Unterkapitels.
Die letzte Zeile kann für die Seitennavigation bestimmt sein, z. B. „PgDn Nach unten scrollen“ und „PgUp Nach oben scrollen“, und kann ignoriert werden.
Ein Datenprotokolleintrag kann auch ein Datum oder ein Jahr enthalten.
Versuche, alles chronologisch nach Datum zu ordnen und jedes Kapitel detailliert zu beschreiben.
Fasse zum Schluss die Handlung der Geschichte zusammen.
Die Datenprotokolle sind in englischer Sprache, aber antworte immer auf Deutsch.
Hier sind alle Datenprotokolleintrag aus jedem Frame:
```

Second copy and paste the whole TXT file below `Here're all text log entries from each frame:` / `Hier sind alle Textprotokolleinträge aus jedem Frame:`, and then submit your query/prompt.

At the bottom of the LM Studio window you can see `CONTEXT IS XY % FULL`.<br>
Keep in mind that some LLM models might produce poor results (hallucination/confabulation) above 60-80%.<br>
Below 80% *should* be ok.


## Manual step: analyze story with online LLM
I think if you've < 24G VRAM, and want to use LM Studio to analyze the TXT file, it will not work or at least not work very well. 

Therefor I've also added a script to do online analysis with either OpenAI, Mistral, Anthropic or Google Generative AI (Vertex or Studio).

> But why all the hustle with creating a developer account and then create an API key?
> Can't I just write my prompt/question and then copy & paste the whole OCR text file?

Maybe you can, I couldn't ... none of the big online LLM providers allowed me to copy & paste the whole OCR text file at once, into their WEB-GUI.<br>
What you can do is split up the text and paste multiple parts, that *should* work.

First write something like `I'll paste you multiple parts of the data log entries. Here's part 1: ...`<br>
Copy & Past 1. part, submit.

`Here's part 2: ...`<br>
Copy & Past 2. part, submit.

And so on, and at the end ask your questions.

**If you want to use any online LLM with my script, you need an API KEY.**<br>
Then copy `.env` to `.env.local` and edit it.

Anyway, my script for chatting with an online LLM:
 - OpenAI (default, gpt-5-mini)
   ```
   python llm_chat.py
   ```
 - Google (gemini-2.5-flash)
   ```
   python llm_chat.py --provider google
   ```
 - Mistral (mistral-medium-latest)
   ```
   python llm_chat.py --provider mistral
   ```
 - Anthropic (claude-haiku-4-5)
   ```
   python llm_chat.py --provider anthropic
   ```
 - local LM Studio (whatever you've downloaded, in this example OpenAI's GPT-OSS 20B)
   ```
   python llm_chat.py --provider lmstudio --modelName "openai/gpt-oss-20b" --apiUrl http://localhost:1234/v1
   ```
   Note: do not use `qwen/qwen3-vl-8b` here. In my tests it ran *forever* and never produced an answer.
   
Btw. `llm_chat.py` outputs LLM Markdown text with `rich`.<br>
Right now with `rich 14.2.0` it can happen that the Markdown formatting *stops* for long texts.
