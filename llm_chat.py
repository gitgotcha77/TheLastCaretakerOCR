import os as pkOS
import glob as pkGlob
import dotenv as pkDotEnv
import getpass as pkGetPass
import argparse as pkArgParse
import datetime as pkDateTime

from rich.console  import Console  as pkRichConsole
from rich.markdown import Markdown as pkRichMD

from langchain import messages    as pkLcMessages
from langchain import chat_models as pkLcChatModels

from langchain_openai       import ChatOpenAI             as pkLcOpenAI
from langchain_anthropic    import ChatAnthropic          as pkLcAnthropic
from langchain_mistralai    import ChatMistralAI          as pkLcMistral
from langchain_google_genai import ChatGoogleGenerativeAI as pkLcGoogle


from tlc_ocr_texts import dLanguages
from tlc_ocr_texts import dTexts
from tlc_ocr_texts import dDefaultModels


def getApiKey(sProvider: str, sKey: str, sForce: str = None) -> bool:
    if sForce is not None and sForce != '':
        pkOS.environ[sKey] = sForce
        return True

    if not pkOS.environ.get(sKey):
        pkOS.environ[sKey] = pkGetPass.getpass(f"Enter your {sProvider} API key: ")
        if pkOS.environ[sKey] == '':
            print('')
            print('All online LLM need an API key. Cannot continue ...')
            print('')
            exit(2)
        return True

    return False


def getChatModel(sProvider: str, sMmodelName: str, sApiKey: str = None, sApiUrl: str = None) -> pkLcChatModels.BaseChatModel:
    if sProvider == 'openai':
        getApiKey('OpenAI', 'OPENAI_API_KEY', sApiKey)
        return pkLcOpenAI(model=sMmodelName)

    elif sProvider == 'anthropic':
        getApiKey('Anthropic', 'ANTHROPIC_API_KEY', sApiKey)
        return pkLcAnthropic(model=sMmodelName)

    elif sProvider == 'google':
        getApiKey('Google', 'GOOGLE_API_KEY', sApiKey)
        return pkLcGoogle(model=sMmodelName)

    elif sProvider == 'mistral':
        getApiKey('Mistral', 'MISTRAL_API_KEY', sApiKey)
        return pkLcMistral(model=sMmodelName)

    elif sProvider == 'lmstudio':
        if sApiUrl is None or sApiUrl == '':
            sApiUrl = 'http://localhost:1234/v1'
        return pkLcOpenAI(model=sMmodelName, base_url=sApiUrl)

    else:
        raise ValueError(f"Unknown provider: {sProvider}")


def queryLLM(sPrompt: str, sFileContent: str, sProvider: str, sModelName: str, sApiKey: str = None, sApiUrl: str = None):
    try:
        lcChatModel = getChatModel(sProvider, sModelName, sApiKey, sApiUrl)
        lcUserMessage = pkLcMessages.HumanMessage(content=f"{sPrompt}\n{sFileContent}")
        lcAiMessage = lcChatModel.invoke([lcUserMessage])
        return lcAiMessage.content

    except Exception as exChat:
        print(f"Error querying LLM: {exChat}")
        return None


if __name__ == '__main__':
    if pkOS.path.exists('.env.local'):
        pkDotEnv.load_dotenv(dotenv_path='.env.local')
    elif pkOS.path.exists('.env'):
        pkDotEnv.load_dotenv(dotenv_path='.env')

    # check for OCR text files
    lOcrTextFiles = pkGlob.glob('*.ocr.txt')
    iOcrTextFiles = len(lOcrTextFiles)

    apParser = pkArgParse.ArgumentParser(description='Query an LLM with a prompt and file content.')

    apParser.add_argument('--textFile'  , dest='sTextFile'  , help='Path to the text file to include')
    apParser.add_argument('--language'  , dest='sLanguage'  , help='Interface language')
    apParser.add_argument('--prompt'    , dest='sPrompt'    , help='The prompt to send to the LLM (do not use template)', default='')
    apParser.add_argument('--provider'  , dest='sProvider'  , help='The LLM provider to use: anthropic, google, mistral, openai, lmstudio')
    apParser.add_argument('--modelName' , dest='sModelName' , help='The model name to use (default depends on provider)')
    apParser.add_argument('--resultFile', dest='sResultFile', help='Write LLM output to this file. If not set use textFile_PROVIDER_MODEL.txt')
    apParser.add_argument('--apiKey'    , dest='sApiKey'    , help='API key for the online LLM API. For safety I recommend ".env.local" or ".env"')
    apParser.add_argument('--apiUrl'    , dest='sApiUrl'    , help='LM Studio is compatible with OpenAI chat client.')

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
    if nsOps.sTextFile is None or nsOps.sTextFile == '':
        if len(lOcrTextFiles) > 0:
            rcConsole.print(f"[bold green]{dTexts['ocrtxt_files']}[/]:")
            for iNdx, sTextFile in enumerate(lOcrTextFiles):
                print(f"  - {iNdx:2d}: {sTextFile}")
            iUseFile = -1
            while iUseFile < 0 or iUseFile >= iOcrTextFiles:
                sSelect = rcConsole.input(f"[bold yellow]{dTexts['ask_ocrtxt']}[/] ")
                if sSelect == '':
                    iUseFile = 0
                else:
                    iUseFile = int(sSelect)
            nsOps.sTextFile = lOcrTextFiles[iUseFile]
        else:
            rcConsole.print(f"[bold red]{dTexts['missing_ocrtxt']}")
            rcConsole.line()
            exit(1)
    rcConsole.print(f"[bold green]{dTexts['use_ocrtxt']}[/]: {nsOps.sTextFile}")

    iDefaultModels = len(dDefaultModels)

    rcConsole.line()
    if nsOps.sProvider is None or nsOps.sProvider == '':
        rcConsole.print(f"[bold green]{dTexts['providers']}[/]:")
        for sProvider in dDefaultModels:
            rcConsole.print(f" - {sProvider} ({dDefaultModels[sProvider]})")
        nsOps.sProvider = rcConsole.input(f"[bold yellow]{dTexts['ask_provider']}[/] ").strip().lower()
        if nsOps.sProvider == '':
            nsOps.sProvider = 'openai'
    if nsOps.sProvider not in dDefaultModels:
        rcConsole.print(f"[bold red]{dTexts['missing_provider']}[/] {nsOps.sProvider}")
        nsOps.sProvider = 'openai'
    rcConsole.print(f"[bold green]{dTexts['use_provider']}[/]: {nsOps.sProvider}")

    rcConsole.line()
    if nsOps.sModelName is None or nsOps.sModelName == '':
        sDefault = dDefaultModels[nsOps.sProvider]
        nsOps.sModelName = rcConsole.input(f"[bold yellow]{dTexts['ask_modelname']}[/] ({sDefault} = {dTexts['default']}) : ").strip().lower()
        if nsOps.sModelName == '':
            nsOps.sModelName = dDefaultModels[nsOps.sProvider]
    rcConsole.print(f"[bold green]{dTexts['use_modelname']}[/]: {nsOps.sModelName}")

    if nsOps.sPrompt is None or nsOps.sPrompt == '':
        nsOps.sPrompt = dTexts['chat_prompt']

    if nsOps.sResultFile is None or nsOps.sResultFile == '':
        sDT = pkDateTime.datetime.now().strftime('%Y%m%d-%H%M')
        sP = nsOps.sProvider.replace('/', '').replace('@', '').replace('\\', '').replace('-', '')
        sMN = nsOps.sModelName.replace('/', '').replace('@', '').replace('\\', '').replace('-', '')
        nsOps.sResultFile = f"{nsOps.sTextFile}_{sDT}_{sP}_{sMN}.md"

    rcConsole.line()
    rcConsole.print(f"[red bold]{dTexts['history_file']}[/]: {nsOps.sResultFile}")
    ioOutput = open(nsOps.sResultFile, 'wt', encoding='utf-8')

    with open(nsOps.sTextFile, 'rt', encoding='utf-8') as ioFile:
        sFileContent = ioFile.read()

    sPrompt = nsOps.sPrompt

    rcConsole.line()
    rcConsole.print(pkRichMD('# USER'))
    rcConsole.print(sPrompt)
    rcConsole.print(f"(... {nsOps.sTextFile} ...)")

    sSepUser = "\n=== USER ==================================================\n"
    sSepLLM  = "\n=== LLM  ==================================================\n"

    while True:
        ioOutput.write(sSepUser)
        ioOutput.write("\n")
        ioOutput.write(sPrompt)
        ioOutput.write("\n")

        rcConsole.line()
        rcConsole.print(pkRichMD('# LLM'))

        sResponse = queryLLM(sPrompt, sFileContent, nsOps.sProvider, nsOps.sModelName, nsOps.sApiKey, nsOps.sApiUrl)
        if sResponse:
            rcConsole.print(pkRichMD(sResponse, justify='left'))

            ioOutput.write(sSepLLM)
            ioOutput.write("\n")
            ioOutput.write(sResponse)
            ioOutput.write("\n")
        else:
            rcConsole.print('[red bold]? EMPTY ?')

        try:
            rcConsole.line()
            rcConsole.print(pkRichMD('# USER'))

            rcConsole.line()
            sPrompt = rcConsole.input(f"{dTexts['enter_prompt']}: ").strip()

            if sPrompt.lower() in ('quit', 'exit', 'q', 'e'):
                rcConsole.print('[green]Goodbye!')
                break

        except KeyboardInterrupt:
            rcConsole.line()
            rcConsole.print('[red bold]Interrupted by user. Exiting...')
            break

        except Exception as exInput:
            rcConsole.print(f"[red bold]ERROR: {exInput}")
            rcConsole.print("Please try again or enter 'quit' to exit.")

    rcConsole.line()
    rcConsole.print(f"[red bold]{dTexts['history_file']}[/]: {nsOps.sResultFile}")
    rcConsole.line()
