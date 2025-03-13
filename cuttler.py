import argparse
import os
from pydub import AudioSegment
from pydub.silence import detect_silence


def cut_audio(input_file, output_dir, min_silence_len, silence_thresh, min_segment_len, max_segment_len):
    """
    Cuts an audio file into segments between 6 and 12 seconds, with cuts made during moments of silence.

    Parameters:
    - input_file (str): Path to the input audio file (e.g., 'input.wav').
    - output_dir (str): Directory where the output segments will be saved.
    - min_silence_len (int): Minimum length of silence (in milliseconds) to consider for cutting (default: 200 ms).
    - silence_thresh (int): Silence threshold in dBFS (default: -40 dBFS).
    - min_segment_len (int): Minimum segment length in milliseconds (default: 6000 ms = 6 seconds).
    - max_segment_len (int): Maximum segment length in milliseconds (default: 12000 ms = 12 seconds).
    """
    audio = AudioSegment.from_file(input_file)
    total_duration = len(audio)

    silences = detect_silence(audio, min_silence_len=min_silence_len, silence_thresh=silence_thresh)
    silences = sorted(silences, key=lambda x: x[0])

    cut_points = [0]
    t_current = 0
    i = 0

    while t_current < total_duration:
        while i < len(silences) and silences[i][1] <= t_current:
            i += 1

        if i >= len(silences):
            cut_points.append(total_duration)
            break

        s_start, s_end = silences[i]

        if s_start <= t_current + max_segment_len:
            t_next = max(t_current + min_segment_len, s_start)
            if t_next <= s_end:
                cut_points.append(t_next)
                t_current = t_next
            elif s_end >= t_current + min_segment_len:
                cut_points.append(s_end)
                t_current = s_end
            else:
                i += 1
        else:
            cut_points.append(s_start)
            t_current = s_start

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for j in range(len(cut_points) - 1):
        start = cut_points[j]
        end = cut_points[j + 1]
        segment = audio[start:end]
        segment_file = os.path.join(output_dir, f"segment_{j+1:03d}.wav")
        segment.export(segment_file, format="wav")
        print(f"Saved segment {j+1}: {start/1000:.1f}s to {end/1000:.1f}s ({(end-start)/1000:.1f}s)")

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Split an audio file into chunks based on silence.")
    parser.add_argument("input_file", help="Path to the input audio file.")
    parser.add_argument("--output_folder", default="audios/pieces", help="Folder where the split audio files will be saved.")
    parser.add_argument("--min", type=int, default=6000, help="Minimum duration of a chunk in milliseconds (default: 6000ms).")
    parser.add_argument("--max", type=int, default=12000, help="Maximum duration of a chunk in milliseconds (default: 12000ms).")
    parser.add_argument("--silence", type=int, default=-30, help="Silence threshold in dBFS (default: -30 dBFS).")
    parser.add_argument("--silence_len", type=int, default=600, help="Minimum length of silence (in milliseconds) to consider for cutting (default: 600ms).")
    
    args = parser.parse_args()
    cut_audio(args.input_file, args.output_folder, args.silence_len, args.silence, args.min, args.max)