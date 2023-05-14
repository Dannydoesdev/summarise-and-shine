import os
import openai
from time import time,sleep
import textwrap
from pytube import YouTube
from pydub import AudioSegment
import requests
from fpdf import FPDF
from dotenv import load_dotenv
from models import chatgpt3, chatgpt4


# Initialise environment variables
load_dotenv()

# Eleven labs is optional
elapikey = os.getenv('ELEVEN_API_KEY')


def open_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as infile:
        return infile.read()

def save_file(filepath, content):
    with open(filepath, 'w', encoding='utf-8') as outfile:
        outfile.write(content)


# PDF conversion is optional
def save_pdf(filepath, newname):
    pdf = FPDF('P', 'mm', 'A4')  
    pdf.add_page()
    pdf.set_font("Arial", size = 12)
    with open(filepath, 'rb') as fh:
      txt = fh.read().decode('latin-1')
    pdf.multi_cell(180, 10, txt, align='L')
    pdf.ln()
    pdf.output(newname)


# paste the YouTube video link in URL.txt
video_url = open_file("URL.txt")

# create a YouTube object
youtube = YouTube(video_url)

# get the highest resolution video stream
video_stream = youtube.streams.get_highest_resolution()

# Your relative or absolute path - files will default to /summary subfolder of this path
pathfolder = './'
   
# download the video to the pathfolder directory with the filename ytvideo.mp4
video_file_path = video_stream.download(output_path=os.path.join(pathfolder, 'summary'), filename='ytvideo.mp4')

# split the audio from the video file into 10-minute segments
segment_duration = 10 * 60 * 1000  # 10 minutes in milliseconds
audio = AudioSegment.from_file(video_file_path, "mp4")
num_segments = int(len(audio) / segment_duration) + 1
for i in range(num_segments):
    segment = audio[i*segment_duration:(i+1)*segment_duration]
    segment_file_path = os.path.join(pathfolder, "summary", f"segment_{i}.mp3")
    segment.export(segment_file_path, format='mp3')

    # transcribe each segment of audio separately via whisper-1 API
    transcripts = []
for i in range(num_segments):
    segment_path = os.path.join(pathfolder, "summary", f"segment_{i}.mp3")
    with open(segment_path, "rb") as f:
        transcript = openai.Audio.transcribe("whisper-1", f)
        print(transcript)
        transcripts.append(transcript.text)

    # concatenate the transcripts and save to a file in the same directory as the video file
    full_transcript = "\n".join(transcripts)
    save_file(os.path.join(pathfolder, "summary", "podscript.txt"), full_transcript)
    
save_pdf(os.path.join(pathfolder, "summary", "podscript.txt"), os.path.join(pathfolder, "summary", "podscript.pdf"))

if __name__ == '__main__':

    # get the text in the full script
    files = ["./summary/podscript.txt"]
    
    # initialize an empty string to store the contents of text
    alltext = ""
    
    # iterate over the text to split it into chunks of 5000 characters - to keep within the GPT-3 limit
    for file in files:
        with open(file, 'r', encoding='utf-8') as infile:  # open the file
            alltext += infile.read()  # read the contents of the file and append it to the alltext string
    chunks = textwrap.wrap(alltext, 5000) # split the text into chunks of 5000 characters for GPT-3 to process - open to experimentation
    result = list()
    count = 0
    
    # Prompt GPT to write an initial summary of each chunk to initialsummary.txt - open to experimentation
    for chunk in chunks:
        count = count + 1
        prompt = open_file('prompt1-scriptsum.txt').replace('<<SUMMARY>>', chunk).replace('<<SECTION>>', str(count)) # Section placeholder set to give gpt a context reference
        prompt = prompt.encode(encoding='ASCII',errors='ignore').decode()
        summary = chatgpt3(prompt)
        print('\n\n\n', count, 'out of', len(chunks), 'Compressions', ' : ', summary)
        result.append(summary)
        save_file(os.path.join(pathfolder, "summary", "initialsummary.txt"), '\n\n'.join(result)) # join all summarised chunks together and save the results


    # Split the contents of initialsummary.txt into chunks of 5000 characters
    with open(os.path.join(pathfolder, "summary", "initialsummary.txt"), 'r', encoding='utf-8') as infile:
        summary = infile.read()
        chunks = textwrap.wrap(summary, 5000)

    #Initialize empty lists to store the results
    result = []
    result2 = []

    # Send the chunks through GPT-3 with both prompt2 and prompt3 - product bullet points and more concise summary
    for i, chunk in enumerate(chunks):

        # Read the contents of prompt2-bulletpts.txt
        with open("prompt2-bulletpts.txt", 'r', encoding='utf-8') as infile:
            prompt = infile.read()

        # Replace the placeholder in the prompt with the current chunk
        prompt = prompt.replace("<<NOTES>>", chunk).replace('<<SECTION>>', str(i))

        # Run the chunk through the gpt_3 function
        points = chatgpt3(prompt)
        
        # Write a summary for each chunk using prompt3-shortsum.txt
        notes = open_file('prompt3-shortsum.txt').replace('<<NOTES>>', chunk).replace('<<SECTION>>', str(i))
        sumnotes = chatgpt3(notes)

        # Print the result
        print(f"\n\n\n{i+1} out of {len(chunks)} Compressions: {points}")

        # Append the results to the lists
        result.append(points)
        result2.append(sumnotes)

    
    #Save the results to a file
    save_file(os.path.join(pathfolder, "summary", "bulletpoints.txt"), "\n\n".join(result))
   
    save_file(os.path.join(pathfolder, "summary", "shortsummary.txt"), "\n\n".join(result2))


    # Summarise notes into bullet points
    sumnotes = open_file(os.path.join(pathfolder, "summary", "bulletpoints.txt"))

    # Write a narrated synopsis of the bullet points
    synopsis = open_file('prompt4-synopsis.txt').replace('<<NOTES>>', sumnotes)
    synopsis_output = chatgpt3(synopsis)
    print(synopsis_output)
    save_file(os.path.join(pathfolder, "summary", "synopsis.txt"), synopsis_output)


    # Convert the synopsis to speech via Elevenlabs API - OPTIONAL

    # Voice: Bella
    url = 'https://api.elevenlabs.io/v1/text-to-speech/EXAVITQu4vr4xnSDxMaL'

    headers = {
        'accept': 'audio/mpeg',
        'xi-api-key': elapikey,
        'Content-Type': 'application/json'
    }
    data = {
        'text': synopsis_output,
        'voice_settings': {
            'stability': 0.6,
            'similarity_boost': 0.85
        }
    }
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        with open(os.path.join(pathfolder, "summary",'voicedsynopsis.mp3'), 'wb') as f:
            f.write(response.content)
        print('Text-to-speech conversion successful')
    else:
        print('Error:', response.text)
    

    # Save a copy of the txt results to a PDF file - optional
    save_pdf(os.path.join(pathfolder, "summary", "initialsummary.txt"), os.path.join(pathfolder, "summary", "initialsummary.pdf"))
    save_pdf(os.path.join(pathfolder, "summary", "bulletpoints.txt"), os.path.join(pathfolder, "summary", "bulletpoints.pdf"))
    save_pdf(os.path.join(pathfolder, "summary", "shortsummary.txt"), os.path.join(pathfolder, "summary", "shortsummary.pdf"))
    save_pdf(os.path.join(pathfolder, "summary", "synopsis.txt"), os.path.join(pathfolder, "summary", "synopsis.pdf"))