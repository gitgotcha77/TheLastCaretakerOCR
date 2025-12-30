# The Last Caretaker data logs OCR

I've created two scripts:
 - ocr_local.py    extract text from a video recording of TLC data log entries.
 - datalog_chat.py pass the extracted text to a local or online LLM.

You need `GIT`, `Python` and some Python packages.<br>
I'm using Python 3.11, but 3.12 or 3.13 should be ok too.<br>
For Linux distros just use the distros package manager to install `Python` and `GIT`.

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

**Before you start recording an important notice: try to keep a steady rhythm with selecting the next page.**<br> 

Then:
 - start your game
 - walk to a terminal and select data logs
 - start your recording
 - select each page and try to keep a rhythm of ~ 1 page per second
 - stop recording once you've selected all data logs and pages

For me OBS Studio will create a MKV file looking like this `2026-01-01_12-12-12.mkv`.

## Start OCR process
```
python ocr_local.py --videoFile 2026-01-01_12-12-12.mkv --modelName "glm-4.6v-flash@q4_k_m" --transcribeFile 2026-01-01_12-12-12.glm46v.en.txt
```
