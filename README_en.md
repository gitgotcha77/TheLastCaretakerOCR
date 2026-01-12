## Project download 
Click on `Code` -> Local -> Download ZIP.
Extract the ZIP somewhere you want, and open the project folder in Windows Explorer.


## Video recording
For this I use [OBS Studio](https://obsproject.com/) with local recording (you don't want to stream it).<br>
Of course nVidia, AMD or Steam recording works too.<br>
Please have a look at a tutorial on how to do that.

**Important notice before you start recording: try to keep a steady rhythm with selecting the next page!**

You can use an online metronome for it ;)<br>
Seriously, I use one too, every time.

1 page per second is the default value in the OCR script.

So:
 - start your game
 - walk to a terminal and select data logs
 - start your recording
 - select each page and try to keep a rhythm of ~ 1 page per second = 1 PPS
 - don't forget to scroll up/down on longer pages with Page-Up/-Down
 - stop recording once you've selected all data logs and pages
 - the duration should be around 3-4 minutes

For me, OBS Studio will create a video file looking like this `2026-01-01_12-12-12.mkv`. Copy your video file in here.<br>

Supported video heights are `720`, `1080`, `1440` and `2560`.

If you recorded your video in a different resolution/height, you have to specify correct crop-values by yourself.<br>
Edit `2 Run OCR.ps1` and change this line:
```
# OCR script call
& $sVenvPython $sOcrScript
```
to
```
# OCR script call
& $sVenvPython $sOcrScript --videoHeight 1234 --crop "X:Y:W:H"
```
- X:Y top-left starting position of the data log page area
- W:H width & height of data log page area

Have a look at `crop_values_example.jpg` for an example and how to get those values with `GIMP`.


## What's up with the '1 page per second' thing?
I use FFMPEG to extract one image per second from your recording.<br>
Ideally we want one `unique` page per image, no missing pages and no duplicate pages.<br> 
Missing pages would be bad. Duplicate pages shouldn't be a big problem, because the LLM *should* be able to detect them.<br>
If you're confitent you can do a consistent rhythm of 5 pages per second, go for it. 


## LM Studio
Download it [here](https://lmstudio.ai/).<br>
You can use `Ollama` or `vLLM` or whatever you want too, as long as you know the API URL, and the API is compatible with OpenAI's standart.<br>
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
 - `Ministral 3 14B Instruct`
 - `LLama 3.1 8B`
 - `SmoLLM3 3B`        as a low-VRAM local chat option
 - `Granite 4 H Micro` as a low-VRAM local chat option

Note: small LLM (fewer parameters = lower xB value) are more likely to only answer in english.
Except for DeepSeek maybe, which then may only answers in simplified chinese?

For OCR you can download and use other models with a yellow `eye` icon. The icon tells you that the model has `vision` capabilities.<br>
There are also explicit OCR models, f.e. `allenai/olmocr-2-7b`, however for some reason I could not get a correct text result with this model.

For chatting you can download pretty much everything that has not `OCR` or `embed` in their name.<br>

When you select a model, LM Studio should show you `Download Options`, and below that if your GPU can fully load the model:
 - `Full GPU Offload Possible`    => fastest, whole model can fit into VRAM and be processed by the GPU
 - `Partial GPU Offload Possible` => medium, model will be loaded into VRAM and RAM, GPU and CPU have to split the workload
 - `Likely too Large`             => will most likely not run at all, even if split between VRAM and RAM     

Usually you want to go for `Full GPU Offload Possible`.
To give you a comparison between `Full GPU Offload` and `Partial GPU Offload`, GPT-OSS 20B:
 - 120 Tokens/s with `Full`
 - 7.5 Tokens/s with `Partial` (50/50, means 12 Layers GPU and 12 Layers CPU)

If you've downloaded a model, go to `Developer`.<br>
Enable the LM Studio API by clicked right next to `Status: Stopped`.<br>
Now click at the top `Select a model to load`, then enable `Manually choose model load parameters`, and then select the model you've downloaded.<br>
You will see a list with many parameters.<br>
What I would recommend to change is:
 - for models used with OCR, set `Context Length` to 10000 (like all Qwen3 Vl)
 - for models used to chat, set `Context Length` to 80000 (or higher if you can, like GPT OSS 20B or Ministral 3 14B)
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
This will download and extract Python 3.13 (+ needed packages) and FFMPEG inside the project folder.

**PowerShell will ask you if you trust `1 Setup Project.ps1` and `config.ps1`.** (2 times, because "1 Setup Project.ps1" includes "config.ps1")<br>
Well ... you have to trust me here :)

If you want to do everything manually, or understand more what's going on, or have more control over it, continue [here](README_manual_steps.md).


## For the lazy ones: Google Gemini
Well ... Google Gemini can process videos. So, put your video in there, ask your questions and done? :)<br>
Yes and no.<br>

Yes, Gemini can process videos even in the free version, with maximum file size of 100 MB and video length of 4 minutes.<br>

What about the AI-Pro-Ultra-Mega-Deluxe version?<br>
IDK, 1h length + and whatever fits in your Google-Drive?

Whatever, `2 Optional Crop.ps1` helps you.<br>
Right-click `2 Optional Crop.ps1` -> `Mit PowerShell ausführen`. (again you will be asked twice to trust the PowerShell scripts)<br>
`2 Optional Crop.ps1` asks you about a video file, height and about your graphic card (for faster video encoding).

Once the script finishes, you will get a new video file `VIDEO_FILENAME.crop-n2-0.5.mp4`.

THe new video should only show the area of the data log text.<br>
**-> smaller file size**<br>
It also omits every second frame and reduces the bit rate.<br>
**-> smaller file size AND shorter length**

This *should* bring you below 100 MB and 4 minutes, allowing you to use the video in the Gemini web GUI.

Hey... it would be much more interesting to do it all yourself on your own PC, wouldn't it?


## OCR process
Right-click `2 Run OCR.ps1` -> `Run in PowerShell`. (again you will be asked twice to trust the PowerShell scripts)<br>
`2 Run OCR.ps1` will ask you which video file should be used, height and PPS values.<br>
Then frames will be extracted from the video, send to `LM Studio` and the result will be saved in `VIDEO_FILENAME.ocr.txt`.<br>
Depending on your hardware, and used model, this might take 20 - 60 minutes.<br>
During the OCR process you can already look at `VIDEO_FILENAME.ocr.txt`.

Remember: `LM Studio` has to be running, with enabled API, and the used LLM has to be downloaded.

After the OCR process finished, go back to `LM Studio` and click on `Eject` to unload the model (and free up VRAM).


## LM Studio chat
Ok ... as I said in the beginning, LLMs are very memory hungry and for the final analysis we need a big context window (Context Length).<br>
We need at least 60k to fit the whole OCR text file.<br>
For models with `Reasoning` more like 80k+, because those models will produces more output tokens.<br>
So if you want to do that step locally, you also need a model which supports a big context window.

# !!! DO NOT DRAG AND DROP THE TXT FILE INTO LM STUDIO CHAT !!!
> Why not?<br>
> LM Studio starts to index the file, and it looks ok?

When you do this, LM Studio will show you `rag-v1` below the input area.<br>
In our case this is bad. I'll not go into details what RAG is or what it can do and for what cases it is useful.<br> 

**tl;dr:** RAG will kind of split up the TXT file and the LLM will NOT *see* all data log entries.<br>
Well that's bad if the LLM should *understand* the whole story.<br>

What you can and should do is copy and paste the whole TXT file in the input area.

Here's a totally-incomplete list of LLM models I know and tested:

| LLM model name            | Max. context length | Memory usage  |
|---------------------------|---------------------|---------------|
| GPT OSS 20B               | 128k                | ~16G with 80k |
| Ministral 3 14B Instruct  | 256k                | ~21G with 80k |
| Gemma 3 12B               | 128k                | ~43G with 80k |
| Llama 3.1 8B              | 128k                | ~14G with 80k |
| Phi 4 Mini Reasoning      | 128k                | ~13G with 80k |
| SmolLM 3 3B               | 64k                 | ~7G with 64k  |
| Granite 4 H Micro         | 1000k               | ~6G with 100k |

On my 4090 I used `gpt-oss-20b` with 80k, so I could also ask some more questions about the story.<br>

Ok, so how do I do it right?

First write what you want the LLM to do, your `system prompt`, f.e. something like this:
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

Second, copy the whole TXT file content, paste it below `Here're all text log entries from each frame:`, and then submit your query/prompt.

At the bottom of the LM Studio window you can see `CONTEXT IS XY % FULL`.<br>
Keep in mind that some LLM models might produce poor results (hallucination/confabulation) above 60-80%.<br>
Below 80% *should* be ok.


## Online LLM chat (only with API keys)
Copy `.env` to `.env.local`, edit it and add your API Key, depending on your provider.

**You might not see `.env` in your Windows Explorer.** 
 - you should see 3 `...` at the top-middle
 - click on it
 - select `Options`
 - select `View`
 - for `Hidden files and folders` select `Show hidden files, folders, or drivers`
 - also deactivate `Hide extensions for known files types` 
 
Right-click `3 LLM chat.ps1` -> `Run in PowerShell`. (again you will be asked twice to trust the PowerShell scripts)<br>
You will be asked which OCR-text file should be used, LLM provider and model name.

> But why all the hustle with creating a developer account and then create an API key?<br>
> Can't I just write my prompt/question and then copy & paste the whole OCR text file?

Maybe you can, I couldn't ... none of the big online LLM providers allowed me to copy & paste the whole OCR text file at once, into their WEB-GUI.<br>
What you can do is split up the text and paste multiple parts, that *should* work.

First write something like `I'll paste you multiple parts of the data log entries. Here's part 1: ...`<br>
Copy & Past 1. part, submit.

`Here's part 2: ...`<br>
Copy & Past 2. part, submit.

And so on, and at the end ask your questions.

Ok I've to admit it is cumbersome, unless you already have API keys for all big providers anyway, like I have.<br>
However, did I mention you will only pay per token usage if you use the API? :)<br>
Not like a monthly fixed subscription fee.<br>


## So Long, and Thanks for All the Fish !

P.S.: if someone wants to send me an nVidia DGX Spark, or Ryzen AI Max+ 395: GLADLY, write me! :)
