#!/usr/bin/env python3
import argparse
import json
from faster_whisper import WhisperModel

def main():
p = argparse.ArgumentParser()
p.add_argument("--audio", required=True, help="Path do audio (wav/mp3)")
p.add_argument("--out", required=True, help="Path do JSON de saída (segments)")
p.add_argument("--language", default="pt", help="Ex.: pt")
p.add_argument("--model", default="small", help="tiny|base|small|medium|large-v3 (CPU: small/medium)")
p.add_argument("--device", default="cpu", help="cpu|cuda")
p.add_argument("--compute_type", default="int8", help="CPU: int8/int8_float16; CUDA: float16")
args = p.parse_args()

model = WhisperModel(args.model, device=args.device, compute_type=args.compute_type)
segments, info = model.transcribe(
    args.audio,
    language=args.language,
    vad_filter=True
)

out = []
for seg in segments:
    text = (seg.text or "").strip()
    if not text:
        continue
    out.append({
        "start": float(seg.start),
        "end": float(seg.end),
        "text": text
    })

with open(args.out, "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=2)

print(args.out)
if name == "main":
main()