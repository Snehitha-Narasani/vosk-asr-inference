import vosk
import json
import wave
import gradio as gr
from textblob import TextBlob
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lex_rank import LexRankSummarizer
import tempfile
import time

# Initialize Vosk model (keep small English model in memory for quick start)
BASE_MODEL = vosk.Model("vosk-model-small-en-us-0.15")

def load_model(model_path):
    vosk.SetLogLevel(-1)
    return vosk.Model(model_path)

def transcribe_audio(audio_path, language):
    model_paths = {
        "English": "vosk-model-small-en-us-0.15",
        "Spanish": "vosk-model-small-es-0.42",
        "French": "vosk-model-small-fr-0.22",
    }
    
    try:
        model = load_model(model_paths.get(language, "vosk-model-small-en-us-0.15"))
        wf = wave.open(audio_path, "rb")
        recognizer = vosk.KaldiRecognizer(model, wf.getframerate())
        
        results = []
        total_frames = wf.getnframes()

        while True:
            data = wf.readframes(4000)
            if len(data) == 0:
                break
            if recognizer.AcceptWaveform(data):
                part = json.loads(recognizer.Result())
                results.append(part['text'])
        
        final_result = json.loads(recognizer.FinalResult())
        results.append(final_result['text'])

        return ' '.join(results)

    except Exception as e:
        return f"Error: {str(e)}"

def count_words_and_chars(text):
    word_count = len(text.split())
    char_count = len(text)
    return f"Words: {word_count}, Characters: {char_count}"

def analyze_sentiment(text):
    if not text.strip():
        return "N/A", "N/A", "😐"
    blob = TextBlob(text)
    polarity = blob.sentiment.polarity
    subjectivity = blob.sentiment.subjectivity
    
    if polarity > 0.2:
        emoji = "😊 Positive"
    elif polarity < -0.2:
        emoji = "😞 Negative"
    else:
        emoji = "😐 Neutral"
    
    return f"{polarity:.2f}", f"{subjectivity:.2f}", emoji

def summarize_text(text, sentences=3):
    if not text.strip():
        return "No text to summarize"
    
    try:
        parser = PlaintextParser.from_string(text, Tokenizer("english"))
        summarizer = LexRankSummarizer()
        summary = summarizer(parser.document, sentences)
        return '\n'.join([str(sentence) for sentence in summary])
    except:
        return "Summarization failed - text might be too short"

def save_transcription(text):
    if not text:
        return None
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as f:
        f.write(text)
        return f.name

iface = gr.Blocks(theme='Nymbo/Nymbo_Theme', css="footer {visibility: hidden}")

with iface:
    gr.Markdown("# 🎤 Smart Audio Analyzer")
    history_state = gr.State([])
    
    with gr.Row():
        with gr.Column(scale=2):
            gr.Markdown("## Upload & Settings")
            with gr.Group():
                audio_input = gr.Audio(
                    type="filepath",
                    label="Record/Upload Audio",
                    sources=["upload", "microphone"],
                    waveform_options={"sample_rate": 44100}
                )
                language_radio = gr.Radio(
                    ["English", "Spanish", "French"],
                    value="English",
                    label="Select Language",
                )
                transcribe_btn = gr.Button("🚀 Start Analysis", variant="primary")
            
            gr.Markdown("## Audio Preview")
            audio_visual = gr.Audio(label="Waveform Preview", interactive=False)  # FIXED

        with gr.Column(scale=3):
            gr.Markdown("## Analysis Results")
            output_text = gr.Textbox(
                label="Transcription",
                placeholder="Results will appear here...",
                lines=8,
                interactive=True
            )
            
            with gr.Row():
                download_btn = gr.File(label="Download Transcription", visible=False)
                word_count = gr.Textbox(label="Statistics", scale=2)
            
            with gr.Accordion("Advanced Analysis", open=False):
                with gr.Row():
                    sentiment_polarity = gr.Textbox(label="Sentiment Polarity")
                    sentiment_subjectivity = gr.Textbox(label="Subjectivity Score")
                    sentiment_emoji = gr.Textbox(label="Emotion Indicator")
                
                with gr.Group():
                    summary_slider = gr.Slider(1, 5, value=3, step=1, label="Summary Sentences")
                    summary_btn = gr.Button("📝 Generate Summary")
                    summary_output = gr.Textbox(label="Key Points", lines=3)
            
            gr.Markdown("## Session History")
            history_dropdown = gr.Dropdown(
                label="Previous Analyses (Last 5)",
                choices=[],
                interactive=True
            )

    # Event Handlers
    def update_visualization(audio_path):
        return audio_path  # FIXED - Pass directly to gr.Audio()

    def update_history(transcription, history):
        if transcription:
            new_history = [transcription] + history[:4]
            return new_history, { "choices": new_history }  # FIXED
        return history, { "choices": history }

    audio_input.change(
        fn=update_visualization,
        inputs=audio_input,
        outputs=audio_visual
    )

    transcribe_btn.click(
        fn=transcribe_audio,
        inputs=[audio_input, language_radio],
        outputs=output_text
    ).then(
        fn=count_words_and_chars,
        inputs=output_text,
        outputs=word_count
    ).then(
        fn=analyze_sentiment,
        inputs=output_text,
        outputs=[sentiment_polarity, sentiment_subjectivity, sentiment_emoji]
    ).then(
        fn=save_transcription,
        inputs=output_text,
        outputs=download_btn
    ).then(
        fn=update_history,
        inputs=[output_text, history_state],
        outputs=[history_state, history_dropdown]
    )

    output_text.change(
        fn=count_words_and_chars,
        inputs=output_text,
        outputs=word_count
    )

    summary_btn.click(
        fn=summarize_text,
        inputs=[output_text, summary_slider],
        outputs=summary_output
    )

    history_dropdown.select(
        fn=lambda x: x,
        inputs=history_dropdown,
        outputs=output_text
    ).then(
        fn=count_words_and_chars,
        inputs=output_text,
        outputs=word_count
    )

if __name__ == "__main__":
    iface.launch(share=True, server_port=7860)
