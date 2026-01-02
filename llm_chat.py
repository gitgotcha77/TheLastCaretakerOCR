import os as pkOS
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


dDefaultModels = {
    'openai':    'gpt-5-mini',
    'anthropic': 'claude-haiku-4-5',
    'google':    'gemini-2.5-flash',
    'mistral':   'mistral-medium-latest'
}

dPromptTemplates = {
    'en': """
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
""",
    'de': """
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
"""
}


def getApiKey(sProvider: str, sKey: str, sForce: str = None) -> bool:
    if sForce is not None and sForce != '':
        pkOS.environ[sKey] = sForce
        return True

    if not pkOS.environ.get(sKey):
        pkOS.environ[sKey] = pkGetPass.getpass(f"Enter your {sProvider} API key: ")
        return True

    return False


def getChatModel(sProvider: str, sMmodelName: str, sApiKey: str = None, sApiUrl: str = None) -> pkLcChatModels.BaseChatModel:
    if sProvider == 'openai':
        getApiKey('OpenAI', 'OPENAI_API_KEY', sApiKey)
        return pkLcOpenAI(model=sMmodelName, base_url=sApiUrl)

    elif sProvider == 'anthropic':
        getApiKey('Anthropic', 'ANTHROPIC_API_KEY', sApiKey)
        return pkLcAnthropic(model=sMmodelName)

    elif sProvider == 'google':
        getApiKey('Google', 'GOOGLE_API_KEY', sApiKey)
        return pkLcGoogle(model=sMmodelName)

    elif sProvider == 'mistral':
        getApiKey('Mistral', 'MISTRAL_API_KEY', sApiKey)
        return pkLcMistral(model=sMmodelName)

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

    apParser = pkArgParse.ArgumentParser(description='Query an LLM with a prompt and file content.')

    apParser.add_argument('--textFile'  , dest='sTextFile'  , help='Path to the text file to include', required=True)
    apParser.add_argument('--template'  , dest='sTemplate'  , help='Use prompt template for language EN or DE', choices=['de', 'en'], default='de')
    apParser.add_argument('--prompt'    , dest='sPrompt'    , help='The prompt to send to the LLM (do not use template)', default='')
    apParser.add_argument('--provider'  , dest='sProvider'  , help='The LLM provider to use', choices=['openai', 'anthropic', 'google', 'mistral'], default='openai')
    apParser.add_argument('--modelName' , dest='sModelName' , help='The model name to use (default depends on provider)')
    apParser.add_argument('--resultFile', dest='sResultFile', help='Write LLM output to this file. If not set use textFile_PROVIDER_MODEL.txt')
    apParser.add_argument('--apiKey'    , dest='sApiKey'    , help='API key for the LLM service. For safety I recommend ".env.local" or ".env"')
    apParser.add_argument('--apiUrl'    , dest='sApiUrl'    , help='LM Studio is compatible with OpenAI chat client.')

    nsOps = apParser.parse_args()

    sPrompt = nsOps.sPrompt or dDefaultModels.get(nsOps.sTemplate, dPromptTemplates['de'])

    if not pkOS.path.exists(nsOps.sTextFile):
        print('')
        print(f"Text file [{nsOps.sTextFile}] not found")
        print('')
        exit(1)

    sModelName = nsOps.sModelName or dDefaultModels.get(nsOps.sProvider, dDefaultModels['openai'])

    if nsOps.sResultFile is None or nsOps.sResultFile == '':
        sDT = pkDateTime.datetime.now().strftime('%Y%m%d-%H%M')
        sP = nsOps.sProvider.replace('/', '-').replace('@', '-').replace('\\', '-')
        sMN = sModelName.replace('/', '-').replace('@', '-').replace('\\', '-')
        nsOps.sResultFile = f"{nsOps.sTextFile}_{sDT}_{sP}_{sMN}.txt"

    print('')
    print(f"RESPONSE FILE: [{nsOps.sResultFile}]")
    ioOutput = open(nsOps.sResultFile, 'wt', encoding='utf-8')

    with open(nsOps.sTextFile, 'rt', encoding='utf-8') as ioFile:
        sFileContent = ioFile.read()

    riConsole = pkRichConsole()
    print('')
    riConsole.print(pkRichMD('# USER'))
    print(sPrompt)
    print(f"... [content of {nsOps.sTextFile}] ...")

    sSepUser = "\n=== USER ==================================================\n"
    sSepLLM  = "\n=== LLM  ==================================================\n"

    while True:
        ioOutput.write(sSepUser)
        ioOutput.write(sPrompt)

        print('')
        riConsole.print(pkRichMD('# LLM'))
        sResponse = queryLLM(sPrompt, sFileContent, nsOps.sProvider, sModelName, nsOps.sApiKey, nsOps.sApiUrl)
        if sResponse:
            riConsole.print(pkRichMD(sResponse, justify='left'))
            print(sResponse)

            ioOutput.write(sSepLLM)
            ioOutput.write(sResponse)
        else:
            print('? EMPTY ?')

        try:
            print('')
            riConsole.print(pkRichMD('# USER'))
            sPrompt = input("\nEnter your next prompt (or quit/q/exit/e to exit): ").strip()

            if sPrompt.lower() in ('quit', 'exit', 'q', 'e'):
                print("Goodbye!")
                break

        except KeyboardInterrupt:
            print("\n\nInterrupted by user. Exiting...")
            break

        except Exception as exInput:
            print(f"An error occurred: {exInput}")
            print("Please try again or enter 'quit' to exit.")

    print('')
