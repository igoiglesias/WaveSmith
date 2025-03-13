from pathlib import Path
import argparse
import shutil
import csv
import os
import torch
import whisper

device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Using device: {device}")


def transcribe_audio(input_path: str, model_size: str, language: str) -> str:
    model = whisper.load_model(model_size, device=device)    
    audio = whisper.load_audio(input_path)
    audio = whisper.pad_or_trim(audio)
    result = model.transcribe(audio, language=language)
    
    return result['text']

def process_directory(input_dir: str, output_dir: str, language: str, model_size: str) -> None:
    wavs_dir = os.path.join(output_dir, "wavs")
    os.makedirs(wavs_dir, exist_ok=True)

    metadata_file = os.path.join(output_dir, "metadata.csv")
    for file in Path(input_dir).glob("*.wav"):
        print(f"Processing file: {file.name}")
        
        transcription = transcribe_audio(file, model_size, language)
        output_audio_path = wavs_dir + "/" + file.name
        shutil.copy(file, output_audio_path)
        file_name = file.name.split('.')[0]

        with open(metadata_file, mode='a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f, delimiter='|')
            writer.writerow([file_name, transcription, transcription])

    print(f"Dataset saved at: {output_dir}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Transcrição de áudio para dataset no padrão LJSpeech")
    parser.add_argument("input", help="Caminho do diretório com arquivos .wav de entrada")
    parser.add_argument("--output", default="dataset", help="Caminho do diretório de saída para o dataset")
    parser.add_argument("--language", default="pt", help="Idioma para transcrição")
    parser.add_argument("--model_size", choices=["tiny", "base", "small", "medium", "large"], default="medium", 
                        help="Escolha o tamanho do modelo Whisper (tiny, base, small, medium, large). Padrão: base")

    args = parser.parse_args()
    process_directory(
        input_dir=args.input, output_dir=args.output,
        language=args.language, model_size=args.model_size
    )