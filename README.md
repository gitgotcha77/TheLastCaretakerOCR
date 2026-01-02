# The Last Caretaker data logs OCR

This is just a fun project to be able to analyze all data log entries from the game `The Last Caretaker`.
At first, I wasn't really interested in the story of the game, but after some time I got curious.
I was too lazy to read through all data log pages, order them chronological and then make sense of the story.

Sooo I decided: why not record a video of all data log pages, then extract all as plain text and shove it into an LLM?

Yes you can argue that that's even more work, but hey I'm a programmer and I already did similar stuff, and it is a funny little project.

**WARNING**: LLMs are very memory hungry. ESPECIALLY if you want to do the final step locally with LM Studio!
I highly recommend 16G+ VRAM.


## Video recording
For this I use [OBS Studio](https://obsproject.com/) with local recording (you don't want to stream it).<br>
Of course nVidia, AMD or Steam recording works too.<br>
Please have a look at a tutorial on how to do that.

**Important notice before you start recording: try to keep a steady rhythm with selecting the next page!**

You can use an online metronom for it ;)<br>
Seriously, I use one too, every time.

1 page per second = 1 FPS is the default value in the OCR script.

So:
 - start your game
 - walk to a terminal and select data logs
 - start your recording
 - select each page and try to keep a rhythm of ~ 1 page per second = 1 FPS
 - don't forget to scroll up/down on longer pages with Page-Up/-Down
 - stop recording once you've selected all data logs and pages
 - the duration should be around 3-4 minutes

For me, OBS Studio will create a video file looking like this `2026-01-01_12-12-12.mkv`.

The default video file for the OCR script is `TLC_DataLogs_1080.mkv` so rename your video file and copy it here.<br>
1080 is my default height the game is running at.

If you want to use a different video file and/or a different height/resolution, edit `config.ps1` and change these 3 lines:
```
$sVideoFile   = "TLC_DataLogs_1080.mkv"
$sVideoHeight = 1080
$sVideoFps    = 1
```
Supported heights are `720`, `1080`, `1440` and `2560`.

If you want to use a different height/resolution and/or a different FPS value, edit `2 Run OCR.ps1` and change this line:
```
# OCR script call
& $sVenvPython $sOcrScript --videoFile $sVideoFile --videoHeight $sVideoHeight --fps $sVideoFps
```
to
```
# OCR script call
& $sVenvPython $sOcrScript --videoFile $sVideoFile --videoHeight $sVideoHeight --fps 123 --crop "X:Y:W:H"
```
- X:Y top-left starting position of the data log page area
- W:H width & height of data log page area

Have a look at `crop_values_example.jpg` for an example and how to get those values with `GIMP`.


## What's up with the 1 page per second thing?
I use FFmpeg to extract one image per second from your recording.<br>
Ideally we want one `unique` page per image, no missing pages and no duplicate pages.<br> 
Missing pages would be bad. Duplicate pages shouldn't be a big problem, because the LLM should be able to detect them.<br>
If you're confitent you can do a consistent rhythm of 5 pages per second, go for it. Adjust the FPS with passing `--fps 5` to my OCR script. 


## LM Studio setup
Download it [here](https://lmstudio.ai/).<br>
You can use `Ollama` or `vLLM` or whatever you want too, as long as you know the API URL.<br>
For `LM Studio` it would be `http://localhost:1234/v1/chat/completions` (for OCR), resp `http://localhost:1234/v1` (for LLM chat), but don't worry because that's also the default in my OCR script.<br>
You can pass a different API URL to the OCR script with `--apiUrl ...`.<br>

Once you've started LM Studio, the first thing you should to is to click on `Power User` at the bottom left.
You should see 4 new icons on the left side:
 - `Chat`
 - `Developer`
 - `My Models`
 - `Discover`

Click on `Discover`.

As of end of 2025 you should see a list of stuff-picked models.<br>
Some usable OCR models are:
 - `Glm 4.6v Flash`
 - `Qwen3 Vl 4B`
 - `Qwen3 Vl 8B` that's the default in my OCR script
 - `Qwen3 Vl 30B`
 
 Some usable chat models are:
 - `GPT OSS 20B` that's the default in the local LLM chat script
 - `Ministral 3 14B`
 - `LLama 3.2 3B instruct` as a low-VRAM local chat option

For OCR you can download and use other models with a yellow `eye` icon. The icon tells you that the model has `vision` capabilities.<br>
There are also explicit OCR models, f.e. `allenai/olmocr-2-7b`, however for some reason I could not get a correct text result with this model.

For chatting you can download pretty much everything that has not `OCR` or `embed` in their name.<br>

When you select a model, LM Studio should show you `Download Options`, and below that if your GPU can fully load the model:
 - `Full GPU Offload Possible`    => fastest, whole model can fit into VRAM and be processed by the GPU
 - `Partial GPU Offload Possible` => medium, model will be loaded into VRAM and RAM, GPU and CPU have to split the workload
 - `Likely too Large`             => will most likely not run at all, even if split between VRAM and RAM     

Usually you want to go for `Full GPU Offload Possible`.

If you've downloaded a model, go to `Developer`.<br>
Enable the LM Studio API by clicked right next to `Status: Stopped`.<br>
Now click at the top `Select a model to load`, then enable `Manually choose model load parameters`, and then select the model you've downloaded.<br>
You will see a list with many parameters.<br>
What I would recommend to change is:
 - for models used with OCR set `Context Length` to 10000 (like all Qwen3 Vl)
 - for models used to chat set `Context Length` to 80000 (or higher if you can, like GPT OSS 20B or Ministral 3 14B)
 - enable `Show advanced settings`
 - enable `Flash Attention`
 - enable `Remember settings for ...`

On the right side of LM Studio you should see `API Usage`, and `This model's API identifier` or model name.<br>
IF you've downloaded a different model then the default `Qwen3 Vl 8B`, you can copy the identifier and pass it with `--modelName ...`.


## LM Studio Q3_K_L, Q4_K_M, Q8_0, F16, what ? ...
That's a big topic. Search for `GGUF quantization methods`.

**tl;dr**: LLMs are very memory hungry and smart people found smart ways to reduce the memory hunger.<br>
Lower Q-number means lower memory usage but also *possible* lower accuracy/quality of the LLMs answer.<br>
Q8 - Q4 should be ok.


## Automatic setup
Right-click `1 Setup Project.ps1` -> `Run in PowerShell`.<br>
This will install Python 3.13 (+ needed packages) and FFMPEG inside the project folder.<br>
Also start `LM Studio` with enabled API, and the LLM you want to use, downloaded.<br>

If you want to do everything manually, or understand more what's going on, or have more control over it, scroll down to the first `Manual step: ...`.


## OCR process
Right-click `2 Run OCR.ps1` -> `Run in PowerShell`. This will extract video frames and send them to `LM Studio`.<br>
Depending on your hardware, and used model, this might take 20 - 60 minutes.<br>
During the OCR process you can already look at `TLC_DataLogs_1080.mkv.ocr.txt`.


## LLM chat
Right-click `3 Local LLM chat.ps1` -> `Run in PowerShell` if you want to use `LM Studio`.
Right-click `3 Online LLM chat DE.ps1` -> `Run in PowerShell` if you want to use the default online LLM for chatting with a german prompt.
Right-click `3 Online LLM chat EN.ps1` -> `Run in PowerShell` if you want to use the default online LLM for chatting with an english prompt.


## Manual step: Python setup
I've created two scripts:
 - `ocr_local.py`: extract text from a video recording of TLC data log entries.
 - `llm_chat.py`: pass the extracted text to a local or online LLM.

You need `GIT`, `Python` and some Python packages.<br>
I'm using Python 3.13, but 3.11 or 3.12 should be ok too.<br>
For Linux distros just use the distros package manager to install Python and GIT.

For Windows have a look here:
 - [Python](https://www.python.org/downloads/windows/)
 - [Github Desktop](https://desktop.github.com/download/)


## Manual step: get this project / GIT checkout
```
got clone https://github.com/gitgotcha77/thelastcaretaker_ocr.git
cd thelastcaretaker_ocr
```


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
python ocr_local.py --videoFile TLC_DataLogs_1080.mkv
```
This will create a text file called `TLC_DataLogs_1080.mkv.ocr.txt`.

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
python ocr_local.py --videoFile TLC_DataLogs_1080.mkv --modelName "glm-4.6v-flash@q4_k_m" --transcribeFile 2026-01-01_12-12-12.glm46v.en.txt
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

| LLM model name       | Max. context length |
|----------------------|---------------------|
| GPT OSS 20B and 120B | 128k                |
| Ministral 3 14B      | 256k                |
| Qwen 3 8B and 30B    | 256k                |
| Gemma 3 27B          | 256k                |

The thing is: which one will fit with 60k+ context length?<br>
On my 4090 I used `gpt-oss-20b` with 100k, so I could also ask some more questions about the story.<br>

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
Keep in mind that most LLM models produce poorer results (hallucination/confabulation) the higher this % value gets.<br>
Below 60% **should** be ok.

## Manual step: analyze story with online LLM
I think if you've < 24G VRAM, and want to use LM Studio to analyze the TXT file, it will not work or at least not work very well. 

Therefor I've also added a script to do online analysis with either OpenAI, Mistral, Anthropic or Google Generative AI (Vertex or Studio).

> Can't I just copy & paste like with LM Studio?

Maybe you can, I couldn't ... none of the above LLM providers allowed me to copy & paste the whole TXT file at once.<br>
Well you can split up the text and paste multiple parts, that *should* work.

**If you want to use any online LLM with my script, you need an API KEY.**<br>
Then copy `.env` to `.env.local` and edit it.

Anyway, my script for chatting with an online LLM:
 - OpenAI (default, gpt-5-mini)
   ```
   python llm_chat.py --textFile TLC_DataLogs_1080.mkv.ocr.txt
   ```
 - Google (gemini-2.5-flash)
   ```
   python llm_chat.py --textFile TLC_DataLogs_1080.mkv.ocr.txt --provider google
   ```
 - Mistral (mistral-medium-latest)
   ```
   python llm_chat.py --textFile TLC_DataLogs_1080.mkv.ocr.txt --provider mistral
   ```
 - Anthropic (claude-haiku-4-5)
   ```
   python llm_chat.py --textFile TLC_DataLogs_1080.mkv.ocr.txt --provider anthropic
   ```
 - local LM Studio (whatever you've downloaded, in this example OpenAI's GPT-OSS 20B)
   ```
   python llm_chat.py --textFile TLC_DataLogs_1080.mkv.ocr.txt --provider openai --modelName "openai/gpt-oss-20b" --apiUrl http://localhost:1234/v1
   ```
   Note: do not use `qwen/qwen3-vl-8b` here. In my tests it ran *forever* and never produced an answer.
   
Btw. `llm_chat.py` outputs LLM Markdown text with `rich`.<br>
Right now with `rich 14.2.0` it can happen that the Markdown formatting *stops* for long texts.


## So Long, and Thanks for All the Fish !
