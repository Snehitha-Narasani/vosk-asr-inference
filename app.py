import vosk
import json
import wave
import gradio as gr

def load_model(model_path):
    vosk.SetLogLevel(-1)
    return vosk.Model(model_path)

def transcribe_audio(audio_path):
    if not audio_path:
        return "No audio file uploaded"

    try:
        model = load_model("vosk-model-small-en-us-0.15")
        wf = wave.open(audio_path, "rb")
        recognizer = vosk.KaldiRecognizer(model, wf.getframerate())
        
        results = []
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
        return f"Transcription error: {str(e)}"

def count_words_and_chars(text):
    words = len(text.split())
    chars = len(text)
    return f"Words: {words} | Characters: {chars}"

iface = gr.Blocks(theme='Nymbo/Nymbo_Theme')

with iface:
    gr.Markdown("# Speech Transcriber")
    
    gr.HTML("<style>footer {visibility: hidden;}</style>")
    
    with gr.Row():
        with gr.Column(scale=2):
            audio_input = gr.Audio(
                type="filepath", 
                label="Record or Upload Audio", 
                sources=["upload", "microphone"],
                interactive=True
            )
            
            transcribe_btn = gr.Button(
                "Transcribe", 
                variant="primary", 
                size="sm"
            )
        
        with gr.Column(scale=1):
            gr.Markdown("### Quick Stats")
            word_count = gr.Textbox(label="Word & Character Count")
    
    output_text = gr.Textbox(
        label="Transcription", 
        placeholder="Transcription will appear here...",
        lines=4
    )
    
    def reset_transcription():
        return "", ""
    
    audio_input.upload(
        fn=reset_transcription, 
        outputs=[output_text, word_count]
    )
    
    transcribe_btn.click(
        fn=transcribe_audio, 
        inputs=audio_input, 
        outputs=output_text
    ).then(
        fn=count_words_and_chars,
        inputs=output_text,
        outputs=word_count
    )

if __name__ == "__main__":
    iface.launch(share=True)