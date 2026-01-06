import os as pkOS
import glob as pkGlob
import base64 as pkB64
import shutil as pkShUtil
import argparse as pkArgParse
import mimetypes as pkMime

from rich.console import Console as pkRichConsole

import tqdm as pkTqdm
import ffmpeg as pkFfmpeg
import requests as pkRequests

from tlc_ocr_texts import dLanguages
from tlc_ocr_texts import dTexts


dCropValues = {
    720 : '413:504:648:157',
    1080: '623:765:971:239',
    1440: '830:952:1297:316',
    2560: '1498:1804:2293:556',
}

sCropValues = str(list(dCropValues.keys()))
sCropValues = sCropValues[1:-1]


def getFrames(sVideoFile: str, sFramesPath: str, iPps: int = 1, iScaleWidth: int = -1, sCrop: str = '') -> list:
    sVF = f"fps={iPps}"
    if sCrop != '':
        sVF += f",crop={sCrop}"
    if iScaleWidth != -1:
        sVF += f",scale={iScaleWidth}:-1"

    sOutputFile = pkOS.path.join(sFramesPath, 'frame_%04d.jpg')

    try:
        ffInst = pkFfmpeg.FFmpeg()
        ffInst.input(sVideoFile).output(sOutputFile, qscale=2, vf=sVF).execute()

    except Exception as exFfmpeg:
        print(f"Error extracting frames: {exFfmpeg}")
        print(f"Video file: {sVideoFile}")
        print(f"Output file: {sOutputFile}")
        print(f"Video filter: {sVF}")
        exit(2)

    lFrames = sorted([f for f in pkOS.listdir(sFramesPath) if f.endswith('.jpg')])

    return lFrames


def sendToLLM(sImageB64: str, sModelName: str, sPrompt: str, sImageMT: str = 'image/jpeg',
              sApiKey: str = 'lm-studio', sApiUrl: str = 'http://localhost:1234/v1/chat/completions') -> str:
    dHeaders = {
        'Content-Type':  'application/json',
        'Authorization': f"Bearer {sApiKey}"
    }
    dPayload = {
        'model':    sModelName,
        'messages': [{
            'role':    'user',
            'content': [
                {'type': 'text', 'text': sPrompt},
                {'type': 'image_url', 'image_url': {'url': f"data:{sImageMT};base64,{sImageB64}"}}
            ]
        }]
    }

    try:
        rqResponse = pkRequests.post(sApiUrl, headers=dHeaders, json=dPayload)
        if rqResponse.status_code == 200:
            result = rqResponse.json()
            sContent = result['choices'][0]['message']['content'].strip()  # type: str

            # check for <thinking> / <think>
            bCleanBox = False
            iPos = sContent.find('</thinking>')
            if iPos > 0:
                iPos += 11
                sContent = sContent[iPos:]
                bCleanBox = True
            iPos = sContent.find('</think>')
            if iPos > 0:
                iPos += 8
                sContent = sContent[iPos:]
                bCleanBox = True
            if bCleanBox:
                sContent = sContent.replace('<|begin_of_box|>', '')
                sContent = sContent.replace('<|end_of_box|>', '')

            return sContent

        else:
            print(f"API error: {rqResponse.status_code}, {rqResponse.text}")
            return ''

    except Exception as exReq:
        print(f"Request failed: {exReq}")
        return ''


if __name__ == '__main__':
    # qwen/qwen3-vl-8b          # ~  9s per frame
    # qwen/qwen3-vl-30b         # ~  3s per frame, needs 24G
    # google/gemma-3-27b        # ~ 14s per frame, needs 24G
    # zai-org/glm-4.6v-flash    # ~  4s per frame

    sFramesPath = 'frames'

    # check for video recordings
    lVideoFiles = pkGlob.glob('*.mkv')
    lVideoFiles.extend(pkGlob.glob('*.mp4'))
    iVideoFiles = len(lVideoFiles)

    apParser = pkArgParse.ArgumentParser(description='Extract text of each data log frame of The Last Caretaker recording')

    apParser.add_argument('--videoFile'     , dest='sVideoFile'     , help='Video file for OCR processing')
    apParser.add_argument('--transcribeFile', dest='sTranscribeFile', help='Output file of transcription. If not set video-file.ocr.txt will be used.')
    apParser.add_argument('--pps'           , dest='iPps'           , help='How fast you changed pages: page per second. Def: 1')
    apParser.add_argument('--modelName'     , dest='sModelName'     , help='Model name used for OCR. Def: qwen/qwen3-vl-8b', default='qwen/qwen3-vl-8b')
    apParser.add_argument('--videoHeight'   , dest='iVideoHeight'   , help=f"Height of recording: used for crop-values. {sCropValues}")
    apParser.add_argument('--crop'          , dest='sCrop'          , help='Crop each frame: left side of each data log entry is useless. Format: W:H:X:Y', default='')
    apParser.add_argument('--language'      , dest='sLanguage'      , help='Interface language')
    apParser.add_argument('--resize'        , dest='iResize'        , help='Some models need a specific image size. Resize is done after crop. Def: -1', default=-1)
    apParser.add_argument('--apiKey'        , dest='sApiKey'        , help='Optional API key, but LM Studio should not need one.')
    apParser.add_argument('--apiUrl'        , dest='sApiUrl'        , help='Optional API URL of your LM Studio.', default='http://localhost:1234/v1/chat/completions')
    apParser.add_argument('--prompt'        , dest='sPrompt'        , help='Optional OCR system prompt')

    nsOps = apParser.parse_args()

    rcConsole = pkRichConsole()

    rcConsole.line()
    if nsOps.sLanguage is None or nsOps.sLanguage == '':
        rcConsole.print('[bold green]Supported interface languages[/]:')
        for sLC in dLanguages:
            rcConsole.print(f" - {sLC}: {dLanguages[sLC]}")
        nsOps.sLanguage = rcConsole.input('[bold yellow]Use language[/]: ')
        nsOps.sLanguage = nsOps.sLanguage.strip().lower()
        if nsOps.sLanguage == '':
            nsOps.sLanguage = 'en'
    if nsOps.sLanguage not in dLanguages:
        rcConsole.print(f"[bold red]Unsupported language {nsOps.sLanguage}")
        nsOps.sLanguage = 'en'
    dTexts = dTexts[nsOps.sLanguage]
    rcConsole.print(f"[bold green]{dTexts['use_language']}[/]: {nsOps.sLanguage}")

    rcConsole.line()
    if nsOps.sVideoFile is None or nsOps.sVideoFile == '':
        if len(lVideoFiles) > 0:
            rcConsole.print(f"[bold green]{dTexts['video_files']}[/]:")
            for iNdx, sVideoFile in enumerate(lVideoFiles):
                print(f"  - {iNdx:2d}: {sVideoFile}")
            iUseVideo = -1
            while iUseVideo < 0 or iUseVideo >= iVideoFiles:
                iUseVideo = int(rcConsole.input(f"[bold yellow]{dTexts['ask_video']}[/] "))
            nsOps.sVideoFile = lVideoFiles[iUseVideo]
        else:
            rcConsole.print(f"[bold red]{dTexts['missing_video']}")
            rcConsole.line()
            exit(1)
    rcConsole.print(f"[bold green]{dTexts['use_video']}[/]: {nsOps.sVideoFile}")

    rcConsole.line()
    if nsOps.iPps is None or nsOps.iPps == '':
        nsOps.iPps = rcConsole.input(f"[bold yellow]{dTexts['ask_pps']}[/] (1 = {dTexts['default']}) ")
        nsOps.iPps = nsOps.iPps.strip()
        if nsOps.iPps == '':
            nsOps.iPps = 1
    nsOps.iPps = int(nsOps.iPps)
    rcConsole.print(f"[bold green]{dTexts['use_pps']}[/]: {nsOps.iPps}")

    rcConsole.line()
    if nsOps.iVideoHeight is None or nsOps.iVideoHeight == '':
        nsOps.iVideoHeight = rcConsole.input(f"[bold yellow]{dTexts['ask_height']}[/] (1080 = {dTexts['default']}) ")
        nsOps.iVideoHeight = nsOps.iVideoHeight.strip()
        if nsOps.iVideoHeight == '':
            nsOps.iVideoHeight = 1080
    nsOps.iVideoHeight = int(nsOps.iVideoHeight)
    rcConsole.print(f"[bold green]{dTexts['use_height']}[/]: {nsOps.iVideoHeight}")

    if nsOps.sTranscribeFile is None or nsOps.sTranscribeFile == '':
        nsOps.sTranscribeFile = f"{nsOps.sVideoFile}.ocr.txt"

    if nsOps.iVideoHeight not in dCropValues:
        if nsOps.sCrop != '':
            sCropValue = nsOps.sCrop
        else:
            rcConsole.line()
            rcConsole.print(f"[red bold]Right now I've only crop-values for[/]: {sCropValues}.")
            rcConsole.print('However you can specify your own values with --crop W:H:X:Y.')
            rcConsole.print('Have a look at "crop_values_example.jpg" on how to get those values.')
            rcConsole.line()
            exit(2)
    else:
        sCropValue = dCropValues[nsOps.iVideoHeight]

    if nsOps.sPrompt is None or nsOps.sPrompt == '':
        nsOps.sPrompt = dTexts['ocr_prompt']

    if pkOS.path.exists(sFramesPath):
        pkShUtil.rmtree(sFramesPath)
    pkOS.makedirs(sFramesPath)

    rcConsole.line()
    rcConsole.print(f"[bold blue]{dTexts['job_ffmpeg']}[/]: {nsOps.sVideoFile}")
    lFrameFiles = getFrames(nsOps.sVideoFile, sFramesPath, nsOps.iPps, nsOps.iResize, sCropValue)
    rcConsole.print(f"[bold green]{dTexts['done_ffmpeg']}[/]: {len(lFrameFiles)}")

    rcConsole.line()
    rcConsole.print(f"[bold blue]{dTexts['job_transcribing']}[/]: [{nsOps.sTranscribeFile}]")
    rcConsole.print(dTexts['note_transcribing'])
    with open(nsOps.sTranscribeFile, 'w', encoding='utf-8') as ioTXT:

        sResult = ''
        sResponse = ''
        sPrevious = ''

        for sFrameFile in pkTqdm.tqdm(lFrameFiles):

            sFullFile = pkOS.path.join(sFramesPath, sFrameFile)
            sMimeType, sEncoding = pkMime.guess_type(sFullFile)

            with open(sFullFile, 'rb') as ioIMG:
                sImageB64 = pkB64.b64encode(ioIMG.read()).decode('utf-8')

            sResponse = sendToLLM(sImageB64, nsOps.sModelName, nsOps.sPrompt, sMimeType, nsOps.sApiKey, nsOps.sApiUrl)
            if sResponse:
                if sResponse != sPrevious:
                    sResult = f"========== {sFrameFile} ==========\n{sResponse}\n\n"
                    ioTXT.write(sResult)
                    ioTXT.flush()
                sPrevious = sResponse
            else:
                sPrevious = ''

    rcConsole.line()
    rcConsole.print(f"[bold green]{dTexts['done_transcribing']}[/]: {nsOps.sTranscribeFile}")
    rcConsole.line()
