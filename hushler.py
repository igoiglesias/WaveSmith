from datetime import datetime
import subprocess
import argparse
import os


def process_audio(
    input_file: str, output_folder: str, i_level: int,
    tp_level: float, lra: int, nr_value: int,
    highpass_freq: int, lowpass_freq: int, dynaudnorm_f: int,
    dynaudnorm_g: int
):
    output_file = name_audio(input_file, output_folder)
    ffmpeg_command = [
        'ffmpeg', '-y',
        '-i', input_file, '-vn', 
        '-acodec', 'pcm_s16le', '-ar', '22050', '-ac', '1', 
        '-af', f"afftdn=nr={nr_value}:nt=white:bn=-25:tn=1, highpass=f={highpass_freq}, lowpass=f={lowpass_freq}, dynaudnorm=f={dynaudnorm_f}:g={dynaudnorm_g}, loudnorm=I={i_level}:TP={tp_level}:LRA={lra}",
        output_file
    ]

    subprocess.run(ffmpeg_command)

def name_audio(input_file: str, output_folder: str) -> str:
    output_folder = os.path.abspath(output_folder)
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    data_string = datetime.now().strftime("-%d-%m-%y-%H:%M:%S")
    return f"{output_folder}/{input_file.split('/')[-1].split('.')[0]+data_string}.wav"

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Processa áudio de vídeo com FFmpeg.")
    parser.add_argument("input", help="Caminho para o arquivo de entrada (ex: 'video.mp4')")
    parser.add_argument("--output_folder", default="audios", help="Caminho para o arquivo de saída (ex: 'audio.wav')")
    parser.add_argument("--i_level", type=int, default=-16, help="Nível de Loudness Target (I), padrão -16")
    parser.add_argument("--tp_level", type=float, default=-1.5, help="True Peak (TP), padrão -1.5")
    parser.add_argument("--lra", type=int, default=9, help="Loudness Range (LRA), padrão 9")
    parser.add_argument("--nr_value", type=int, default=30, help="Noise reduction (nr), padrão 30")
    parser.add_argument("--highpass_freq", type=int, default=100, help="Frequência de Highpass (Hz), padrão 100")
    parser.add_argument("--lowpass_freq", type=int, default=10000, help="Frequência de Lowpass (Hz), padrão 10000")
    parser.add_argument("--dynaudnorm_f", type=int, default=150, help="Dynamic audio normalization (f), padrão 150")
    parser.add_argument("--dynaudnorm_g", type=int, default=15, help="Dynamic audio normalization (g), padrão 15")

    args = parser.parse_args()
    process_audio(
        args.input, args.output_folder, 
        args.i_level, args.tp_level, args.lra, 
        args.nr_value, args.highpass_freq, args.lowpass_freq,
        args.dynaudnorm_f, args.dynaudnorm_g
    )
