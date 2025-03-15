from pathlib import Path
import argparse
import shutil
import csv
import os
import torch
import whisper

MODEL = None


def load_model(model_size: str) -> None:
    global MODEL
    if not MODEL:
        device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Using device: {device}")
        MODEL = whisper.load_model(model_size, device=device)
    return MODEL

def transcribe_audio(input_path: str, model_size: str, language: str) -> str:
    model = load_model(model_size)  
    audio = whisper.load_audio(input_path)
    audio = whisper.pad_or_trim(audio)
    result = model.transcribe(audio, language=language)
    
    return result['text']

def process_directory(input_dir: str, output_dir: str, language: str, model_size: str) -> None:
    wavs_dir = os.path.join(output_dir, "wavs")
    os.makedirs(wavs_dir, exist_ok=True)

    metadata_file = os.path.join(output_dir, "metadata.csv")
    files = Path(input_dir).glob("*.wav")
    for file in sorted(files):
        print(f"Processing file: {file.name}")
        
        transcription = transcribe_audio(file, model_size, language)
        output_audio_path = wavs_dir + "/" + file.name
        shutil.copy(file, output_audio_path)
        file_name = file.name.split('.')[0]

        with open(metadata_file, mode='a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f, delimiter='|')
            writer.writerow([file_name.strip(), transcription.strip(), transcription.strip()])

    print(f"Dataset saved at: {output_dir}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Audio transcription for a dataset in LJSpeech format")
    parser.add_argument("input", help="Path to the directory containing input .wav files")
    parser.add_argument("--output", default="dataset", help="Path to the output directory for the dataset")
    parser.add_argument("--language", default="pt", help="Language for transcription")
    parser.add_argument("--model_size", choices=["tiny", "base", "small", "medium", "large"], default="medium", 
                        help="Choose the Whisper model size (tiny, base, small, medium, large). Default: base")

    args = parser.parse_args()
    process_directory(
        input_dir=args.input, output_dir=args.output,
        language=args.language, model_size=args.model_size
    )