#!/usr/bin/env python3
"""Transcribe a local audio/video into timestamped TSV/SRT/TXT; never alters source media."""
import argparse
import csv
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile


def srt_time(seconds):
    ms = round(seconds*1000)
    h, ms = divmod(ms, 3_600_000)
    m, ms = divmod(ms, 60_000)
    s, ms = divmod(ms, 1000)
    return f'{h:02}:{m:02}:{s:02},{ms:03}'


def write_segment(txt, writer, srt, index, start, end, text):
    txt.write(text+'\n')
    writer.writerow([f'{start:.2f}', f'{end:.2f}', text])
    srt.write(f'{index}\n{srt_time(start)} --> {srt_time(end)}\n{text}\n\n')


def transcribe(source, output, model='medium', language='zh', offline=False, device='cpu', compute_type='int8'):
    source, output = Path(source).resolve(), Path(output).resolve()
    if not source.is_file():
        raise ValueError('Input must be a local file')
    if output.exists():
        raise FileExistsError('Choose a new output directory')
    if not shutil.which('ffmpeg'):
        raise ValueError('ffmpeg is missing')
    from faster_whisper import WhisperModel
    # Local inference after model download; no hosted transcription API.
    engine = WhisperModel(model, device=device, compute_type=compute_type, local_files_only=offline)
    output.mkdir(parents=True, mode=0o700)
    with tempfile.TemporaryDirectory(prefix='recap-audio-', dir=output) as work:
        wav = Path(work)/'audio.wav'
        subprocess.run(['ffmpeg', '-nostdin', '-v', 'error', '-i', str(source), '-ar', '16000', '-ac', '1', str(wav)], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        segments, _ = engine.transcribe(str(wav), language=language, vad_filter=True, beam_size=5, condition_on_previous_text=False)
        n = 0
        # Keep partial results with an explicit suffix if transcription fails.
        with (output/'transcript.txt.partial').open('w', encoding='utf-8') as txt, (output/'transcript.tsv.partial').open('w', encoding='utf-8') as tsv, (output/'transcript.srt.partial').open('w', encoding='utf-8') as srt:
            writer = csv.writer(tsv, delimiter='\t', lineterminator='\n')
            writer.writerow(['start', 'end', 'text'])
            for seg in segments:
                text = seg.text.strip().replace('\t', ' ').replace('\n', ' ')
                if not text:
                    continue
                n += 1
                write_segment(txt, writer, srt, n, seg.start, seg.end, text)
                if n % 50 == 0:
                    print(f'Transcribed {n} segments, audio position {seg.end:.0f}s', flush=True)
        if not n:
            raise ValueError('No speech detected; check the source audio')
        for path in output.glob('*.partial'):
            path.chmod(0o600)
            path.rename(path.with_suffix(''))
    return n


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('input');p.add_argument('--output', required=True)
    p.add_argument('--model', default='medium', help='Model name or a local model directory')
    p.add_argument('--language', default='zh')
    p.add_argument('--offline', action='store_true', help='Use cached model only; do not download')
    p.add_argument('--device', default='cpu');p.add_argument('--compute-type', default='int8')
    a = p.parse_args()
    count = transcribe(a.input, a.output, a.model, a.language, a.offline, a.device, a.compute_type)
    print(f'Completed {count} segments. Pass {Path(a.output)/"transcript.tsv"} to prepare.py. Speakers are NOT diarized; correct labels before relying on them.')

if __name__ == '__main__':
    try:
        main()
    except Exception as exc:
        print(f'Transcription failed ({type(exc).__name__}). Check ffmpeg, faster-whisper, model availability and use a new output directory; source media is unchanged.', file=sys.stderr)
        sys.exit(1)
