# YT Summariser
YouTube Summary with Whisper API, ChatGPT API + Eleven Labs Voice

## Purpose

- To let users consume content in the forms they want, not necessarily the forms they are uploaded in
- To reclaim time spent watching long form content when not necessary, summarisation helps understand whether longer content is worth your time
- Proof of concept for a larger suite of personalised content summarisation tools
- Learning more about user cases for AI & the ease of developing helpful micro tools with ChatGPT 

## Plugs

[Find me @ Linkedin](https://www.linkedin.com/in/danieltmcgee/)

[I'm building a platform for devs to share their projects - come join!](https://www.gitconnect.dev/landing)


## Personalisation

Note: the Eleven Labs Voice Summary is optional ( Can be removed or #commented out )

- You can choose from different OpenAI models in models.py - GPT3.5-turbo is default
- The current prompts are just experiments and you are encouraged to try variations to find something that works for you
- systembot.txt will set a system message for the gpt functions - leaving this blank has worked well so far

## Running in colab

1. Open colab file from [colab](https://colab.research.google.com/) - you likely need to create a new notebook and upload to your drive
2. Browse to colab hosted resources from the folder icon on the left pane
3. Upload all necessary local files (can copy contents of the 'copy-my-contents' folder)
4. Set your keys in the openai and elevenlabs txt files - note this is not safe to share, feel free to secure colab api keys in other ways
5. Set intended Youtube URL in "URL.txt"
6. Run colab sections

## Running locally

1. Copy .env.template & rename to .env
2. Set Your OpenAI Key and in .env
3. (optional) Set Your Eleven Labs API in .env - for voiced transcripts
4. Set the desired YouTube URL in "URL.txt"
5. Edit local path folders in podsummariser.py as needed
6. May need to ```pip -r requirements.txt```
7. Run ```python podsummariser.py```

## How it works

Note: All summarised files are placed in a './summary/' subfolder

1. Downloads high quality version of youtube video via pytube
2. Extracts audio into segment files via pydub so it can be transcribed to text via Whisper API
3. Uses Whisper API to transcribe segments
4. Joins segments back up - full transcription can be found in 'podscript.txt'
5. 'podscript.txt' fed to GPT in chunks with the task in 'prompt1.txt' to make a full summary, summarised to 'initialsummary.txt'
6. 'initialsummary.txt' is broken into chunks and put through GPT with the task 'prompt2.txt' to make bulletpoints and 'prompt23txt' to make a concise summary, summaries saved in 'bulletpoints.txt' and 'shortsummary.txt'
7. 'bulletpoints.txt' fed into gpt to generate a narration synopsis - 'synopsis.txt'
8. 'synopsis.txt' is sent to elevenlabs API to be transcribed to an audio spoken file - audiosynopsis.mp3

## Troubleshooting

1. If you run into errors with ffmpeg - run ```brew install ffmpeg```

## Credits

Credit for initial codebase that has been a key building block for further development goes to allaboutai on Youtube

## Legal stuff

User assumes all responsibility in using the tool in ways that comply with their local and federal laws. 