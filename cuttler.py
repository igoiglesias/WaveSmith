import argparse
import os
from pydub import AudioSegment
from pydub.silence import split_on_silence


def cut_audio(input_file, output_dir, min_silence_len, silence_thresh, silence_tails):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    audio = AudioSegment.from_file(input_file)
    pieces = split_on_silence(audio, min_silence_len=min_silence_len, silence_thresh=silence_thresh, keep_silence=silence_tails)

    for idx, piece in enumerate(pieces):
        if piece.duration_seconds < 0.7:
            continue
        piece_name = os.path.join(output_dir, f"piece_{idx+1:03d}.wav")
        piece.export(piece_name, format="wav")
        print(f"Saved {piece_name} ({round(piece.duration_seconds, 2)} seconds)")

    print(f"Total number of pieces: {len(pieces)}")

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Split an audio file into chunks based on silence.")
    parser.add_argument("input_file", help="Path to the input audio file.")
    parser.add_argument("--output_folder", default="audios/pieces", help="Folder where the split audio files will be saved.")
    parser.add_argument("--silence_tails", type=int, default=200, help="Minimum silence left at the end of a segment (in milliseconds) (default: 200 ms).")
    parser.add_argument("--silence", type=int, default=-54, help="Silence threshold in dBFS (default: -54 dBFS).")
    parser.add_argument("--silence_len", type=int, default=500, help="Minimum length of silence (in milliseconds) to consider for cutting (default: 500ms).")
    
    args = parser.parse_args()
    cut_audio(args.input_file, args.output_folder, args.silence_len, args.silence, args.silence_tails)