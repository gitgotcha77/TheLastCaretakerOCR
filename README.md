# The Last Caretaker data logs OCR

This is just a fun project to be able to analyze all data log entries from the game `The Last Caretaker`.
At first, I wasn't really interested in the story of the game, but after some time I got curious.
I was too lazy to read through all data log pages, order them chronological and then make sense of the story.

Sooo I decided: why not extract all data log pages as plain text and shove it into an LLM?

Yes you can argue that that's even more work, but hey I'm a programmer and I already did similar stuff and it is an interesting project.

**WARNING**: LLMs are very memory hungry. ESPECIALLY if you want to do the final step locally with LM Studio!
I highly recommend 20G+ VRAM.

## LM Studio setup
Download it [here](https://lmstudio.ai/).<br>
You can use `Ollama` or `vLLM` or whatever you want too, as long as you know the API URL.<br>
For `LM Studio` it would be `http://localhost:1234/v1/chat/completions`, but don't worry because that's also the default in my OCR script.<br>
You can pass a different API URL to the COR script with `--apiUrl ...`.<br>

Once you've started LM Studio, the first thing you should to is to click on `Power User` at the bottom left.
You should see 4 new icons on the left side:
 - `Chat`
 - `Developer`
 - `My Models`
 - `Discover`

Click on `Discover`.

As of end of 2025 you should see a list of stuff-picked models, some usable models are:
 - `Glm 4.6v Flash`
 - `Qwen3 Vl 4B`
 - `Qwen3 Vl 8B` that's the default in my OCR script
 - `Qwen3 Vl 30B`

You can download and use other models with a yellow `eye` icon. The icon tells you that the model has `vision` capabilities.

There are also explicit OCR models, f.e. `allenai/olmocr-2-7b`, however for some reason I could not get a correct text result with this model.

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
 - set `Context Length` to 10000
 - enable `Show advanced settings`
 - enable `Flash Attention`
 - enable `Remember settings for ...`

On the right side of LM Studio you should see `API Usage`, and `This model's API identifier` or model name.<br>
IF you've downloaded a different model then the default `Qwen3 Vl 8B`, you can copy the identifier and pass it with `--modelName ...`.

## Python setup
I've created two scripts:
 - ocr_local.py    extract text from a video recording of TLC data log entries.
 - datalog_chat.py pass the extracted text to a local or online LLM.

You need `GIT`, `Python` and some Python packages.<br>
I'm using Python 3.11, but 3.12 or 3.13 should be ok too.<br>
For Linux distros just use the distros package manager to install Python and GIT.

For Windows have a look here:
 - [Python](https://www.python.org/downloads/windows/)
 - [Github Desktop](https://desktop.github.com/download/)

## Get this project / GIT checkout
```
got clone https://github.com/gitgotcha77/thelastcaretaker_ocr.git
cd thelastcaretaker_ocr
```

## Python VENV setup
For virtual environment I use `uv` and `venv`.<br>
Have a look [here](https://pypi.org/project/uv/) on how to install `uv`.

Now let's create a venv for this project:
```
uv venv venv_p311_tlc_ocr --python 3.11 --seed --no-project
```

The directory `venv_p311_tlc_ocr` will be created inside `thelastcaretaker_ocr`.

Activate the VENV:
 - Linux `source venv_p311_tlc_ocr/bin/activate`
 - Windows `call venv_p311_tlc_ocr\bin\activate.bat`
```
uv pip install -r requirements.txt
```

## Video recording
For this I use [OBS Studio](https://obsproject.com/) with local recording (you don't want to stream it).<br>
Of course nVidia or Steam recording works too.<br>
Please have a look at a tutorial on how to do that.

**Important notice before you start recording: try to keep a steady rhythm with selecting the next page.**<br> 
You can use an online metronom for it ;)

Then:
 - start your game
 - walk to a terminal and select data logs
 - start your recording
 - select each page and try to keep a rhythm of ~ 1 page per second
 - stop recording once you've selected all data logs and pages

For me OBS Studio will create a MKV file looking like this `2026-01-01_12-12-12.mkv`.

## What's up with the 1 page per second thing?
I use FFmpeg to extract one image per second from your recording.<br>
Ideally we want one `unique` page per image, no missing pages and no duplicate pages.<br> 
Missing pages would be bad. Duplicate pages shouldn't be a big problem, because the LLM should be able to detect them.<br>
If you're confitent you can do a consistent rhythm of 5 pages per second, go for it. Adjust the FPS with passing `--fps 5` to my OCR script. 

## Start OCR process
```
python ocr_local.py --videoFile 2026-01-01_12-12-12.mkv
```
This will create a text file called `2026-01-01_12-12-12.mkv.ocr.txt`.

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
python ocr_local.py --videoFile 2026-01-01_12-12-12.mkv --modelName "glm-4.6v-flash@q4_k_m" --transcribeFile 2026-01-01_12-12-12.glm46v.en.txt
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

## Final step: analyze Data Logs with an LLM
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
```
I'm playing a game called "The Last Caretaker".
Help me to unravel the story in details.
In the game I've discovered story elements as data logs.
I've recorded a video navigating through all data log pages, and then extract the text from each frame.
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

Second copy and paste the whole TXT file below `Here're all text log entries from each frame:`, and then submit your query/prompt.

At the bottom of the LM Studio window you can see `CONTEXT IS XY % FULL`.<br>
Keep in mind that most LLM models produce poorer results (hallucination/confabulation) the higher this % value gets.<br>
Below 60% **should** be ok.
