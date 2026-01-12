import os as pkOS
import re as pkRE
import glob as pkGlob
import shlex as pkShlex
import argparse as pkArgParse

from rich.console import Console as pkRichConsole

import ffmpeg as pkFfmpeg

from tlc_ocr_texts import dCropValues
from tlc_ocr_texts import dLanguages
from tlc_ocr_texts import dTexts


def createCroppedVideo(sVideoFile: str, sCrop: str, sEncoder: str = '') -> str:

    sCroppedFile = f"{sVideoFile}.crop-n2-0.5.mp4"

    #  V....D  h264_amf     AMD AMF H.264 Encoder (codec h264)
    #  V....D  h264_mf      H264 via MediaFoundation (codec h264)
    #  V....D  h264_nvenc   NVIDIA NVENC H.264 encoder (codec h264)
    #  V.....  h264_qsv     H.264 / AVC / MPEG-4 AVC / MPEG-4 part 10 (Intel Quick Sync Video acceleration) (codec h264)
    #  V....D  h264_vaapi   H.264/AVC (VAAPI) (codec h264)
    #  V....D  h264_vulkan  H.264/AVC (Vulkan) (codec h264)

    if sEncoder is None or sEncoder not in ['amd', 'nvidia', 'intel']:
        sEncoder = 'libx264'
    elif sEncoder == 'amd':
        sEncoder = 'h264_amf'
    elif sEncoder == 'nvidia':
        sEncoder = 'h264_nvenc'
    elif sEncoder == 'intel':
        sEncoder = 'h264_qsv'

    sVF = f"crop={sCrop},select='not(mod(n,2))',setpts=0.5*PTS"

    sCommand = ''
    sInputFile = pkShlex.quote(sVideoFile)
    sOutputFile = pkShlex.quote(sCroppedFile)

    try:
        sCommand = f".\\ffmpeg\\bin\\ffmpeg.exe -i {sInputFile} -c:v {sEncoder} -vf \"{sVF}\" -crf 31 -an -y {sOutputFile}"
        pkOS.system(sCommand)
        # for some reason pkFfmpeg will not use "select=...,setpts=..." correctly
        # ffInst = pkFfmpeg.FFmpeg()
        # ffInst.input(sVideoFile).output(sOutputFile, {'c:v': sEncoder}, vf=sVF, crf=31).execute()

    except Exception as exFfmpeg:
        print(f"Error converting: {exFfmpeg}")
        print(f"Command: {sCommand}")
        exit(3)

    return sCroppedFile


if __name__ == '__main__':
    sCropValues = str(list(dCropValues.keys()))
    sCropValues = sCropValues[1:-1]

    # check for video recordings
    lVideoFiles = pkGlob.glob('*.mkv')
    lVideoFiles.extend(pkGlob.glob('*.mp4'))
    iVideoFiles = len(lVideoFiles)

    apParser = pkArgParse.ArgumentParser(description='Create a cropped and speed-up version of your The Last Caretaker recording')

    apParser.add_argument('--videoFile'  , dest='sVideoFile'  , help='Video file for cropping')
    apParser.add_argument('--videoHeight', dest='iVideoHeight', help=f"Height of recording: used for crop-values. {sCropValues}")
    apParser.add_argument('--crop'       , dest='sCrop'       , help='Crop each frame: left side of each data log entry is useless. Format: W:H:X:Y', default='')
    apParser.add_argument('--language'   , dest='sLanguage'   , help='Interface language')

    nsOps = apParser.parse_args()

    reHeight = pkRE.compile(r'\D(720|1080|1440|2560)\D', pkRE.IGNORECASE)

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
                sSuffix = ''
                if not iNdx:
                    sSuffix = f" ({dTexts['default']})"
                print(f"  - {iNdx:2d}: {sVideoFile}{sSuffix}")
            iUseVideo = -1
            while iUseVideo < 0 or iUseVideo >= iVideoFiles:
                sSelect = rcConsole.input(f"[bold yellow]{dTexts['ask_video']}[/] ")
                if sSelect == '':
                    iUseVideo = 0
                else:
                    iUseVideo = int(sSelect)
            nsOps.sVideoFile = lVideoFiles[iUseVideo]
        else:
            rcConsole.print(f"[bold red]{dTexts['missing_video']}")
            rcConsole.line()
            exit(1)
    rcConsole.print(f"[bold green]{dTexts['use_video']}[/]: {nsOps.sVideoFile}")

    # try to detect video height from filename
    lMatches = reHeight.findall(nsOps.sVideoFile)
    iHeightDefault = 0
    if len(lMatches) > 0:
        iHeightDefault = int(lMatches[0])
    if iHeightDefault < 720 or iHeightDefault > 2560:
        iHeightDefault = 1080

    rcConsole.line()
    if nsOps.iVideoHeight is None or nsOps.iVideoHeight == '':
        nsOps.iVideoHeight = rcConsole.input(f"[bold yellow]{dTexts['ask_height']}[/] ({iHeightDefault} = {dTexts['default']}) ")
        nsOps.iVideoHeight = nsOps.iVideoHeight.strip()
        if nsOps.iVideoHeight == '':
            nsOps.iVideoHeight = iHeightDefault
    if not isinstance(nsOps.iVideoHeight, int):
        nsOps.iVideoHeight = int(nsOps.iVideoHeight)
    rcConsole.print(f"[bold green]{dTexts['use_height']}[/]: {nsOps.iVideoHeight}")

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

    rcConsole.line()
    sEncoder = rcConsole.input(f"[bold yellow]{dTexts['ask_ccv_encoder']}[/] ").strip().lower()
    rcConsole.print(f"[bold blue]{dTexts['use_ccv']}[/]")
    sCroppedVideo = createCroppedVideo(nsOps.sVideoFile, sCropValue, sEncoder)

    rcConsole.line()
    rcConsole.print(f"[bold green]{dTexts['ccv_file']}[/]: {sCroppedVideo}")
    rcConsole.line()
