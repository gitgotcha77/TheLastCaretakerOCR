import argparse as pkArgParse
import base64 as pkB64
import mimetypes as pkMime
import os as pkOS

import ffmpeg as pkFfmpeg
import requests as pkRequests
import tqdm as pkTqdm


sSystemPrompt = """
You are an OCR system. Extract all text visible in the image. 
Return only the text, without any additional commentary, formatting or your thinking process.
Skip the page navigation stuff at the bottom like 'PgDn Scroll down' and 'PgUp Scroll up'.
"""

dCropValues = {
    '720' : '413:504:648:157',
    '1080': '623:765:971:239',
    '1440': '830:952:1297:316',
    '2560': '1498:1804:2293:556',
}

sCropValues = str(list(dCropValues.keys()))
sCropValues = sCropValues[1:-1]


def getFrames(sVideoFile: str, sFramesPath: str, iFps: int = 1, iScaleWidth: int = -1, sCrop: str = '') -> list:
    print('')
    print(f"Extracting frames from video [{sVideoFile}] ...")
    print(f"    frames path: {sFramesPath}")
    print(f"            FPS: {iFps}")
    print(f"          scale: {iScaleWidth}")
    print(f"           crop: {sCrop}")

    sVF = f"fps={iFps}"
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
    print(f"          count: {len(lFrames)}")

    return lFrames


def sendToLLM(sImageB64: str, sModelName: str, sPrompt: str, sImageMT: str = 'image/jpeg',
              sApiKey: str = 'lm-studio', sApiUrl: str = 'http://localhost:1234/v1/chat/completions') -> str:
    dHeaders = {
        'Content-Type':  'application/json',
        'Authorization': f"Bearer {sApiKey}"
    }
    dPayload = {
        'model':    sModelName,
        'messages': [
            {
                'role':    'user',
                'content': [
                    {'type': 'text', 'text': sPrompt},
                    {'type': 'image_url', 'image_url': {'url': f"data:{sImageMT};base64,{sImageB64}"}}
                ]
            }
        ]
    }

    try:
        rqResponse = pkRequests.post(sApiUrl, headers=dHeaders, json=dPayload)
        if rqResponse.status_code == 200:
            result = rqResponse.json()
            sContent = result['choices'][0]['message']['content']  # type: str

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

    apParser = pkArgParse.ArgumentParser(description='Extract text of each data log frame of The Last Caretaker recording')

    apParser.add_argument('--videoFile'     , dest='sVideoFile'     , help='Video file for OCR processing', required=True)
    apParser.add_argument('--framesPath'    , dest='sFramesPath'    , help='Path for temporary frame files. Def: frames', default='frames')
    apParser.add_argument('--transcribeFile', dest='sTranscribeFile', help='Output file of transcription. If not set video-file.ocr.txt will be used.', default='')
    apParser.add_argument('--modelName'     , dest='sModelName'     , help='Model name used for OCR. Def: qwen/qwen3-vl-8b', default='qwen/qwen3-vl-8b')
    apParser.add_argument('--fps'           , dest='iFps'           , help='In this case: how fast you changed pages (1 FPS = 1 page per second). Def: 1', default=1)
    apParser.add_argument('--videoHeight'   , dest='iVideoHeight'   , help=f"Height of recording: used for crop-values. {sCropValues}. Def: 1080", default='1080')
    apParser.add_argument('--crop'          , dest='sCrop'          , help='Crop each frame: left side of each data log entry is useless. Format: W:H:X:Y', default='')
    apParser.add_argument('--resize'        , dest='iResize'        , help='Some models need a specific image size. Resize is done after crop. Def: -1', default=-1)
    apParser.add_argument('--apiKey'        , dest='sApiKey'        , help='Optional API key, but LM Studio should not need one.')
    apParser.add_argument('--apiUrl'        , dest='sApiUrl'        , help='Optional API URL of your LM Studio.', default='http://localhost:1234/v1/chat/completions')
    apParser.add_argument('--prompt'        , dest='sPrompt'        , help='Optional OCR system prompt', default=sSystemPrompt)

    nsOps = apParser.parse_args()

    if nsOps.iVideoHeight not in dCropValues:
        if nsOps.sCrop != '':
            sCropValue = nsOps.sCrop
        else:
            print('')
            print(f"Right now I've only crop-values for: {sCropValues}.")
            print('However you can specify your own values with --crop W:H:X:Y.')
            print('Have a look at "crop_values_example.jpg" on how to get those values.')
            print('')
            exit(1)
    else:
        sCropValue = dCropValues[nsOps.iVideoHeight]

    if nsOps.sTranscribeFile == '':
        nsOps.sTranscribeFile = f"{nsOps.sVideoFile}.ocr.txt"

    pkOS.makedirs(nsOps.sFramesPath, exist_ok=True)

    lFrameFiles = getFrames(nsOps.sVideoFile, nsOps.sFramesPath, nsOps.iFps, nsOps.iResize, sCropValue)

    print('')
    print(f"Transcribing to [{nsOps.sTranscribeFile}] ...")
    print(f"You can have a look at the file during the transcribe process")

    with open(nsOps.sTranscribeFile, 'w', encoding='utf-8') as ioTXT:

        sResult = ''
        sResponse = ''
        sPrevious = ''

        for sFrameFile in pkTqdm.tqdm(lFrameFiles):

            try:
                sFullFile = pkOS.path.join(nsOps.sFramesPath, sFrameFile)
                sMimeType, sEncoding = pkMime.guess_type(sFullFile)

                with open(sFullFile, 'rb') as ioIMG:
                    sImageB64 = pkB64.b64encode(ioIMG.read()).decode('utf-8')

                sResponse = sendToLLM(sImageB64, nsOps.sModelName, nsOps.sPrompt, sMimeType, nsOps.sApiKey, nsOps.sApiUrl)
                if sResponse:
                    if sPrevious != sResponse:
                        sResult = f"========== {sFrameFile} ==========\n{sResponse}\n\n"
                        ioTXT.write(sResult)
                        ioTXT.flush()
                    sPrevious = sResponse

                else:
                    sPrevious = ''

            except Exception as exProc:
                print(f"Error processing {sFrameFile}: {exProc}")
                # might be due to out-of-tokens

    print('')
    print(f"All text extracted and saved to [{nsOps.sTranscribeFile}]")
    print('')
