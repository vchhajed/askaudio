import openai
import streamlit as st
from audio_recorder_streamlit import audio_recorder
import os 
import requests
import whisper

# st.title("ChatGPT-like clone")
# with st.expander("ℹ️ Disclaimer"):
#     st.caption(
#         "We appreciate your engagement! Please note, this demo is designed to process a maximum of 10 interactions. Thank you for your understanding."
#     )

openai.api_key = st.secrets["OPENAI_API_KEY"]

if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-3.5-turbo"

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Maximum allowed messages
max_messages = (
    20  # Counting both user and assistant messages, so 10 iterations of conversation
)

if "transcribe_message" not in st.session_state:
    st.session_state["transcribe_message"] = ""

if "voice_prompt" not in st.session_state:
    st.session_state["voice_prompt"] = ""

model = whisper.load_model("base")
def text_to_speech(text):
    print(text)
    CHUNK_SIZE = 1024
    url = "https://api.elevenlabs.io/v1/text-to-speech/21m00Tcm4TlvDq8ikWAM"

    headers = {
    "Accept": "audio/mpeg",
    "Content-Type": "application/json",
    "xi-api-key": st.secrets["ELEVEN_LABS_KEY"]
    }

    data = {
    "text": text,
    "model_id": "eleven_monolingual_v1",
    "voice_settings": {
        "stability": 0.5,
        "similarity_boost": 0.5
    }
    }

    response = requests.post(url, json=data, headers=headers)

    with open('output.wav', 'wb') as f:
        for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
            if chunk:
                f.write(chunk)
    if os.path.exists('output.wav'):
        os.write(1,b"file uploaded successfully!!!")


# from transcriber import Transcription

def transcribe_audio(audio_file):

    # Recognize speech using Google Web Speech API
    try:
        data = whisper.load_audio(audio_file)
        result = model.transcribe(data)
        return result["text"]
    except Exception as e:
        return f"Errors; {e}"


with st.sidebar:
    audio_file = "myfile.wav"
    output_file = "output.wav"
    audio_bytes = audio_recorder(text="",
    recording_color="#e8b62c",
    neutral_color="#6aa36f",
    icon_name="user",
    icon_size="6x")
    if audio_bytes:
        st.audio(audio_bytes, format="audio/wav")
        if os.path.exists(audio_file):
            os.remove(audio_file)
        with open(audio_file, mode='wb') as f:
            f.write(audio_bytes)
        st.session_state["voice_prompt"] = transcribe_audio("./myfile.wav")

# system_message = {
#             "role": "assistant",
#             "content": "Welcome! I'm here to listen and support you. Please feel free to share your thoughts and emotions.",
#         }
# with st.chat_message("assistant"):
#     st.markdown(system_message["content"])



if len(st.session_state.messages) >= max_messages:
    st.info(
        """Notice: The maximum message limit for this demo version has been reached. We value your interest!
        We encourage you to experience further interactions by building your own application with instructions
        from Streamlit's [Build conversational apps](https://docs.streamlit.io/knowledge-base/tutorials/build-conversational-apps)
        tutorial. Thank you for your understanding."""
    )


else:
    if prompt := ( st.chat_input("What is up?") or st.session_state["voice_prompt"] ):
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            system_messages = [{"role": "system", "content": "You are a helpful and empathetic assistant."},
            {"role": "system", "content": "Remember to be supportive and understanding."}, {"role": "system", "content": "Keep it short less than 100 words."}]
            all_messages = [ {"role": m["role"], "content": m["content"]} for m in st.session_state.messages ]
            all_messages.extend(system_messages)
            response = openai.ChatCompletion.create(
                model=st.session_state["openai_model"],
                messages=all_messages
            )
            full_response = response.choices[0]['message']['content']
            message_placeholder.markdown(full_response)
        
        print(full_response)
        os.write(1,bytes(full_response, 'utf-8'))
        text_to_speech(full_response)
        str = f'{os.listdir()}'
        os.write(1,bytes(str, 'utf-8'))
        if os.path.exists('output.wav'):
            audio_file = open('output.wav', 'rb')
            audio_bytes = audio_file.read()
            os.write(1,b'Something was executed.\n')
            st.audio(audio_bytes, format='audio/wav')
        # play(audio)
        st.session_state.messages.append(
            {"role": "assistant", "content": full_response}
        )