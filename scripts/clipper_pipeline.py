#!/usr/bin/env python3
import argparse, json, os, subprocess, math, textwrap, re

def run(cmd):
    p = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if p.returncode != 0:
        raise SystemExit(f"Command failed: {cmd}\n\nSTDOUT:\n{p.stdout}\n\nSTDERR:\n{p.stderr}")
    return p.stdout.strip()

def srt_time(seconds: float) -> str:
    seconds = max(0.0, float(seconds))
    hh = int(seconds // 3600)
    mm = int((seconds % 3600) // 60)
    ss = int(seconds % 60)
    ms = int(round((seconds - math.floor(seconds)) * 1000))
    return f"{hh:02d}:{mm:02d}:{ss:02d},{ms:03d}"

def clean_text(t: str) -> str:
    t = re.sub(r"\s+", " ", (t or "")).strip()
    return t

def load_segments(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def build_blocks(segments, min_block=12, max_block=25):
    blocks = []
    cur_start = None
    cur_end = None
    parts = []
    for seg in segments:
        start = float(seg.get("start", 0))
        end = float(seg.get("end", 0))
        text = clean_text(seg.get("text", ""))
        if not text or end <= start:
            continue

        if cur_start is None:
            cur_start, cur_end, parts = start, end, [text]
            continue

        duration = end - cur_start
        if duration < min_block:
            cur_end = end
            parts.append(text)
        elif duration <= max_block:
            cur_end = end
            parts.append(text)
            blocks.append({"start_sec": round(cur_start,2), "end_sec": round(cur_end,2), "text": clean_text(" ".join(parts))})
            cur_start, cur_end, parts = None, None, []
        else:
            blocks.append({"start_sec": round(cur_start,2), "end_sec": round(cur_end,2), "text": clean_text(" ".join(parts))})
            cur_start, cur_end, parts = start, end, [text]

    if cur_start is not None and (cur_end - cur_start) >= min_block:
        blocks.append({"start_sec": round(cur_start,2), "end_sec": round(cur_end,2), "text": clean_text(" ".join(parts))})
    return blocks

def pick_clips_simple(blocks, clips_count=4, min_dur=20, max_dur=59):
    """
    MVP: escolhe blocos 'bons' por heurística simples:
    - texto maior
    - sem sobreposição (já são sequenciais)
    Depois ajusta duração para ficar no range.
    """
    scored = []
    for b in blocks:
        dur = b["end_sec"] - b["start_sec"]
        if dur <= 0:
            continue
        score = len(b["text"])
        scored.append((score, b))
    scored.sort(key=lambda x: x[0], reverse=True)

    clips = []
    used = []
    for _, b in scored:
        if len(clips) >= clips_count:
            break
        s, e = b["start_sec"], b["end_sec"]
        dur = e - s
        if dur < min_dur:
            continue
        if dur > max_dur:
            e = s + max_dur

        # check overlap
        ok = True
        for us, ue in used:
            if not (e <= us or s >= ue):
                ok = False
                break
        if not ok:
            continue

        used.append((s,e))
        clips.append({
            "start_sec": float(s),
            "end_sec": float(e),
            "title": "Corte",
            "description": "",
            "hashtags": []
        })

    # fallback: se não achou suficiente, pega do início sequencial
    if len(clips) < clips_count:
        for b in blocks:
            if len(clips) >= clips_count:
                break
            s, e = b["start_sec"], b["end_sec"]
            dur = e - s
            if dur < min_dur:
                continue
            if dur > max_dur:
                e = s + max_dur
            ok = True
            for us, ue in used:
                if not (e <= us or s >= ue):
                    ok = False
                    break
            if not ok:
                continue
            used.append((s,e))
            clips.append({
                "start_sec": float(s),
                "end_sec": float(e),
                "title": "Corte",
                "description": "",
                "hashtags": []
            })

    clips.sort(key=lambda x: x["start_sec"])
    return clips[:clips_count]

def write_srt_for_clip(segments, clip_start, clip_end, out_path):
    idx = 1
    lines = []
    for seg in segments:
        s = float(seg.get("start", 0))
        e = float(seg.get("end", 0))
        t = clean_text(seg.get("text",""))
        if not t or e <= clip_start or s >= clip_end:
            continue
        s2 = max(s, clip_start) - clip_start
        e2 = min(e, clip_end) - clip_start
        if e2 <= s2:
            continue
        lines.append(f"{idx}\n{srt_time(s2)} --> {srt_time(e2)}\n{t}\n")
        idx += 1

    if not lines:
        lines = ["1\n00:00:00,000 --> 00:00:01,000\n(sem legenda)\n"]

    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--youtube_url", required=True)
    p.add_argument("--job_dir", required=True)
    p.add_argument("--clips_count", type=int, default=4)
    p.add_argument("--min_duration", type=int, default=20)
    p.add_argument("--max_duration", type=int, default=59)
    args = p.parse_args()

    job_dir = args.job_dir
    clips_dir = os.path.join(job_dir, "clips")
    os.makedirs(clips_dir, exist_ok=True)

    source_mp4 = os.path.join(job_dir, "source.mp4")
    audio_wav = os.path.join(job_dir, "audio.wav")
    transcript_json = os.path.join(job_dir, "transcript.json")

    # 1) download
    run(f'yt-dlp -f "bv*+ba/b" --merge-output-format mp4 -o "{job_dir}/source.%(ext)s" "{args.youtube_url}"')

    # 2) audio
    run(f'ffmpeg -y -i "{source_mp4}" -ac 1 -ar 16000 "{audio_wav}"')

    # 3) transcribe
    run(f'python /opt/clipper/transcribe_faster_whisper.py --audio "{audio_wav}" --out "{transcript_json}" --language pt --model small --device cpu --compute_type int8')

    segments = load_segments(transcript_json)
    blocks = build_blocks(segments)
    clips = pick_clips_simple(blocks, clips_count=args.clips_count, min_dur=args.min_duration, max_dur=args.max_duration)

    rendered = []
    for i, c in enumerate(clips, start=1):
        start = c["start_sec"]
        end = c["end_sec"]
        name = f"clip_{i:02d}"
        out_mp4 = os.path.join(clips_dir, f"{name}.mp4")
        out_srt = os.path.join(clips_dir, f"{name}.srt")

        # 4) render vertical blur bg
        run(
            f'ffmpeg -y -ss {start} -to {end} -i "{source_mp4}" '
            f'-filter_complex '
            f'"[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=20:1[bg];'
            f'[0:v]scale=1080:1920:force_original_aspect_ratio=decrease[fg];'
            f'[bg][fg]overlay=(W-w)/2:(H-h)/2,format=yuv420p[v]" '
            f'-map "[v]" -map 0:a? -c:v libx264 -preset veryfast -crf 20 -c:a aac -b:a 128k "{out_mp4}"'
        )

        # 5) srt
        write_srt_for_clip(segments, start, end, out_srt)

        rendered.append({
            "index": i,
            "start_sec": start,
            "end_sec": end,
            "mp4_path": out_mp4,
            "srt_path": out_srt,
        })

    result = {
        "job_dir": job_dir,
        "source_mp4": source_mp4,
        "transcript_json": transcript_json,
        "clips": rendered
    }
    print(json.dumps(result, ensure_ascii=False))

if __name__ == "__main__":
    main()