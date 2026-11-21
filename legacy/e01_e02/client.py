#!/usr/bin/env python3
"""GEA Latido E01: synthetic packets from Kali, with sequential/concurrent runs."""
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import csv
from datetime import datetime, timezone
import hashlib
from pathlib import Path
import struct
import time
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

HEADER = "!BBIIIB6s"  # 21 bytes
assert struct.calcsize(HEADER) == 21
SIZES = [168, 336, 672, 1344, 8192, 32768]


def build_packet(bits: int, sequence: int):
    if bits < 168 or bits > 524288 or bits % 8:
        raise ValueError("bits debe ser múltiplo de 8 entre 168 y 524288")
    header = struct.pack(HEADER, 1, 2, 424242, sequence, int(time.time()), 0, b"\0" * 6)
    extra = bits // 8 - 21
    return header + bytes((i % 251 for i in range(extra)))


def send_one(server, bits, sequence, scenario, timeout):
    packet = build_packet(bits, sequence)
    url = f"{server.rstrip('/')}/api/alert?scenario={scenario}"
    request = Request(url, data=packet, headers={"Content-Type": "application/octet-stream"}, method="POST")
    start = time.perf_counter()
    try:
        with urlopen(request, timeout=timeout) as response:
            import json
            ack = json.load(response)
        if not ack.get("ok") or ack.get("sequence") != sequence or ack.get("bits") != bits:
            raise ValueError("ACK no coincide")
        state, error = "OK", ""
    except (URLError, HTTPError, ValueError, TimeoutError, OSError) as exc:
        state, error = "FALLO", str(exc)[:120]
    elapsed = (time.perf_counter() - start) * 1000
    return [datetime.now(timezone.utc).isoformat(), scenario, bits, sequence,
            state, round(elapsed, 2), error]


def main():
    p = argparse.ArgumentParser(description="Generador de alertas ficticias para red local")
    p.add_argument("--server", default="http://127.0.0.1:8080")
    p.add_argument("--bits", default="168,336,672,1344,8192", help="Enteros separados por coma; múltiplos de 8")
    p.add_argument("--n", type=int, default=10, help="Repeticiones por tamaño")
    p.add_argument("--workers", type=int, default=1, help="1 = secuencial; 2/4 = concurrencia experimental")
    p.add_argument("--scenario", choices=["hot", "cold", "repeater", "mesh", "local", "cli"], default="cli")
    p.add_argument("--timeout", type=float, default=5)
    p.add_argument("--output", default="data/gea_envios.csv")
    args = p.parse_args()
    sizes = [int(x) for x in args.bits.split(",")]
    if args.n < 1 or args.n > 10000 or not 1 <= args.workers <= 16:
        p.error("n debe estar entre 1 y 10000; workers entre 1 y 16")
    for b in sizes:
        build_packet(b, 1)
    sequence = 1
    jobs = []
    for bits in sizes:
        for _ in range(args.n):
            jobs.append((args.server, bits, sequence, args.scenario, args.timeout))
            sequence += 1
    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        futures = [ex.submit(send_one, *job) for job in jobs]
        rows = [f.result() for f in as_completed(futures)]
    rows.sort(key=lambda r: r[3])
    target = Path(args.output)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("w", newline="", encoding="utf-8") as fp:
        w = csv.writer(fp)
        w.writerow(["measured_utc", "scenario", "bits", "sequence", "result", "rtt_ms", "error"])
        w.writerows(rows)
    print("Escenario:", args.scenario, "Enviados:", len(rows),
          "OK:", sum(r[4] == "OK" for r in rows), "Fallo:", sum(r[4] != "OK" for r in rows))
    for b in sizes:
        cohort = [r for r in rows if r[2] == b]
        ok = [r for r in cohort if r[4] == "OK"]
        avg = round(sum(r[5] for r in ok) / len(ok), 2) if ok else "NA"
        print(f"{b:>7} bits: entrega={len(ok)}/{len(cohort)} RTT_media={avg}ms")
    print("CSV enviado:", target.resolve())

if __name__ == "__main__":
    main()
