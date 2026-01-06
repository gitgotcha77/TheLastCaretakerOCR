## Projekt herunterladen 
Klicke auf `Code` -> Local -> Download ZIP.
Entpacke die ZIP-Datei an einem Ort deiner Wahl und öffne dann den Projektordner im Windows Explorer.


## Videoaufnahme
Dafür benutze ich [OBS Studio](https://obsproject.com/) mit lokaler Aufnahme (du willst das nicht streamen).<br>
Natürlich funktionieren auch nVidia-, AMD- oder Steam-Aufnahmen.<br>
Bitte schau dir ein Tutorial an, wie man das macht.

**Wichtiger Hinweis vor dem Start der Aufnahme: Versuche, beim Auswählen der nächsten Seite einen gleichmäßigen Rhythmus einzuhalten!**

Du kannst dafür ein Online-Metronom verwenden ;)<br>
Ernsthaft – ich benutze auch jedes Mal eines.

1 Seite pro Sekunde (Page per Second, PPS) ist der Standardwert im OCR-Skript.

Also:
 - starte dein Spiel
 - gehe zu einem Terminal und wähle `Data logs`
 - starte die Aufnahme
 - wähle jede Seite aus und halte einen Rhythmus von ca. 1 Seite pro Sekunde = 1 PPS
 - vergiss nicht, bei längeren Seiten mit Bild-Rauf / -Runter zu scrollen
 - stoppe die Aufnahme, sobald Du alle Datenprotokolle und Seiten durchgegangen bist
 - das sollte in etwa 3–4 Minuten brauchen

Bei mir erstellt OBS Studio dann eine Videodatei wie z.B. `2026-01-01_12-12-12.mkv`. Kopiere deine Videodatei hier in den Projektordner.<br>

Unterstützte Videohöhen sind `720`, `1080`, `1440` und `2560`.

Wenn du dein Video in einer anderen Auflösung/Höhe aufgenommen hast, musst du die Crop-Werte selbst angeben.<br>
Bearbeite `2 Run OCR.ps1` und ändere folgende Zeile:
```
# OCR script call
& $sVenvPython $sOcrScript
```
zu
```
# OCR script call
& $sVenvPython $sOcrScript --videoHeight 1234 --crop "X:Y:W:H"
```
- X:Y Startposition oben links des Datenprotokollbereichs
- W:H Breite & Höhe des Datenprotokollbereichs

Schau dir `crop_values_example.jpg` an, um ein Beispiel zu bekommen und zu sehen, wie man diese Werte mit `GIMP` ermittelt.


## Was hat es mit '1 Seite pro Sekunde' auf sich?
Ich benutze FFMPEG, um ein Bild pro Sekunde aus deiner Aufnahme zu extrahieren.<br>
Idealerweise wollen wir eine `eindeutige` Seite pro Bild, keine fehlenden Seiten und keine Duplikate.<br>
Fehlende Seiten wären schlecht. Doppelte Seiten sind kein großes Problem, da das LLM sie erkennen *sollte*.<br>
Wenn du sicher bist, dass du konstant 5 Seiten pro Sekunde schaffst – nur zu.

## LM Studio
[Hier](https://lmstudio.ai/) kannst du es herunterladen.<br>
Du kannst auch `Ollama`, `vLLM` oder etwas anderes verwenden, solange du die API-URL kennst, und die API ist kompatibel mit OpenAI's Standard.<br>
Für `LM Studio` wäre das `http://localhost:1234/v1/chat/completions` (für OCR), bzw. `http://localhost:1234/v1` (für LLM Chat).
Mach dir darüber aber keine Gedanken, das ist auch der Standard in meinem OCR-Skript.<br>
Du kannst eine andere API URL mit `--apiUrl ...` übergeben.<br>

Nachdem du LM Studio gestartet hast, klicke zuerst unten links auf `Power User`.
Du solltest nun vier neue Icons links sehen:
 - `Chat`
 - `Developer`
 - `My Models`
 - `Discover`

Klicke auf `Discover`.

Stand Ende 2025 solltest du eine Liste handverlesener Modelle sehen.<br>
Einige brauchbare OCR-Modelle:
 - `Glm 4.6v Flash`
 - `Qwen3 Vl 4B`
 - `Qwen3 Vl 8B` Standard in meinem OCR-Skript
 - `Qwen3 Vl 30B`
 
 Einige brauchbare Chat-Modelle:
 - `GPT OSS 20B` Standard im lokalen LLM-Chat-Skript
 - `Ministral 3 14B`
 - `LLama 3.1 8B`
 - `SmoLLM3 3B` falls du sehr wenig VRAM hast

Für OCR kannst du auch andere Modelle mit einem gelben `Auge`-Icon herunterladen.
Das bedeutet, dass das Modell `Vision`-Fähigkeiten hat bzw. den Inhalt eines Bildes erkennen kann.<br>

Es gibt auch explizite OCR-Modelle, z.B. `allenai/olmocr-2-7b`, allerdings habe ich damit aus irgendeinem Grund kein korrektes Textergebnis bekommen.

Für das Chatten kannst du fast alles herunterladen, was weder `OCR` noch `embed` im Namen hat.<br>

Wenn du ein Modell auswählst, zeigt LM Studio unter `Download Options` an, ob deine GPU es vollständig laden kann:
 - `Full GPU Offload Possible`    => am schnellsten, Modell passt komplett in den VRAM und die GPU erledigt die ganze Arbeit
 - `Partial GPU Offload Possible` => mittel, Modell wird zwischen VRAM und RAM aufgeteilt, GPU und CPU teilen sich die Arbeit
 - `Likely too Large`             => läuft sehr wahrscheinlich gar nicht

Normalerweise willst du `Full GPU Offload Possible` haben.

Nach dem Herunterladen eines Modells, gehe zu `Developer`.<br>
Aktiviere die LM Studio API, rechts neben `Status: Stopped`.<br>
Klicke oben auf `Select a model to load`, aktiviere `Manually choose model load parameters`, und wähle dein Modell.<br>
Du solltest jetzt eine Liste an Parametern sehen.<br>
Meine empfohlenen Einstellungen:
 - bei Modellen für OCR, setze `Context Length` auf 10000 (alle Qwen3 Vl Varianten)
 - bei Modellen zum chatten, setze `Context Length` auf 80000+ (bei GPT OSS 20B oder Ministral 3 14B)
 - für Chat-Modelle ist 60k das **absolute Minimum**, da der komplette Text aller Datenprotokolle schon ~50k hat
 - aktiviere `Show advanced settings`
 - aktiviere `Flash Attention`
 - aktiviere `Remember settings for ...`

Rechts siehst du `API Usage`, und `This model's API identifier` bzw. den Namen des Modells.<br>
Wenn du ein anderes Modell als `Qwen3 Vl 8B` nutzt, kopiere die Kennung und übergib sie mit `--modelName ...`.


## LM Studio Q3_K_L, Q4_K_M, Q8_0, F16, was zum T.. ?
Großes Thema, suche nach `GGUF Methoden zur Quantisierung`.

**Kurzfassung**: LLMs brauchen viel Speicher, und kluge Leute and ein paar kluge Wege gefunden den Speicherverbrauch zu reduzieren.<br>
Niedrigere Q-Zahl = weniger Speicher, evtl. aber geringere Qualität.<br>
Q8 bis Q4 ist meist okay.


## Automatisches Setup
Rechts-Klick auf `1 Setup Project.ps1` -> `Mit PowerShell ausführen`.<br>
Das lädt und entpackt Python 3.13 (+ benötigte Pakete) und FFMPEG im Projektordner.

**PowerShell fragt, ob du `1 Setup Project.ps1` und `config.ps1` vertraust.** (2 mal, da "1 Setup Project.ps1" "config.ps1" inkludiert)<br>
Nun ja ... da musst du mir vertrauen :)

Wenn du alles manuell selber machen willst oder mehr Kontrolle möchtest, geht es [hier](README_manual_steps.md) weiter (leider nur auf Englisch).


## OCR Prozess
Rechts-Klick auf `2 Run OCR.ps1` -> `Mit PowerShell ausführen`. (PowerShell fragt dich wieder 2 mal um Erlaubnis)<br>
`2 Run OCR.ps1` wird dich nach deiner Videodatei, Höhe und PPS Werten fragen.<br>
Dann werden die Einzelbilder aus dem Video extrahiert, an `LM Studio` gesendet und das Resultat in `VIDEO_FILENAME.ocr.txt` gespeichert.<br>
Je nach deiner Hardware und Modell dauert das 20 - 60 Minuten.<br>
Während dem OCR Prozess kannst du dir bereits die OCR-Text Datei `VIDEO_FILENAME.ocr.txt` durchsehen.

Vergiss nicht: `LM Studio` muss bereits laufen, die API muss aktiviert sein und das verwendete Modell bereits heruntergeladen.

Nach dem OCR Prozess, gehe zurück zu `LM Studio` und klicke auf `Eject`, um das Modell aus dem VRAM zu entfernen.


## LM Studio chat
Ok ... as I said in the beginning, LLMs are very memory hungry and for the final analysis we need a big context window (Context Length).<br>
We need at least 60k to fit the whole OCR text file.<br>
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
Keep in mind that most LLM models produce poorer results (hallucination/confabulation) the higher this % value gets.<br>
Below 60% **should** be ok.


## Online LLM Chat (nur mit API Keys möglich)
Kopiere `.env` zu `.env.local`, bearbeite die Datei und kopiere deinen API Key, entsprechend deinem Anbieter.

**Eventuell siehst du die Datei `.env` im Windows Explorer gar nicht.** 
 - oben-mittig solltest du 3 `...` sehen
 - klicke darauf
 - wähle `Optionen`
 - wähle `Ansicht`
 - bei `Versteckte Dateien und Ordner` wähle `Ausgeblendete Dateien, Ordner und Laufwerke anzeigen`
 - deaktiviere ausserdem `Erweiterungen bei bekannten Dateitypen ausblenden` 

Rechts-Klick `3 LLM chat.ps1` -> `Run in PowerShell`. (PowerShell fragt dich wieder 2 mal um Erlaubnis)<br>
Du wirst nach OCR-Text Datei, Anbieter und Modell gefragt.

> Aber wieso denn der ganze Aufwand mit Entwickler Accounts und API Keys?
> Kann ich nicht einfach meinen Prompt / meine Frage eingeben und dann den ganzen Inhalt der OCR-Text Datei kopieren und einzufügen?

Naja vielleicht funktioniert das bei dir, bei mir nicht ... keiner der grossen LLM Anbietern hat mir erlaubt, den kompletten Inhalt der OCR-Text Datei, in ihre WEb-GUI einzufügen.<br>
Was du machen kannst ist den Text in mehreren Teilen einzufügen, das *sollte* funktionieren.

Schreibe zuerst sowas wie `Ich kopiere die Datenprotokolle in mehreren Teilen. Hier kommt Teil 1: ...`<br>
1. Teil kopieren und einfügen, absenden.

`Hier kommt Teil 1: ...`<br>
2. Teil kopieren und einfügen, absenden.

Usw. und am Ende dann deine Fragen stellen.

Aber zugegeben ist das schon etwas umständlich, wenn man nicht gerade wie ich eh schon bei allen grossen Anbietern API Keys hat.<br>
Andererseits, habe ich schon erwähnt, dass du nur pro Token-Nutzung bezahlen musst, wenn du die API verwendest? :)<br>
Keine fixen monatlichen Abo-Gebühren.<br>


## So Long, and Thanks for All the Fish !
