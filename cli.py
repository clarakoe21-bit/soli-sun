from __future__ import annotations

import argparse
import os
from pathlib import Path

from .alpha_verify import verify
from .live_runtime import process_live_turn
from .model_adapter import DeterministicReferenceModel, OpenAIResponsesModel, ModelError
from .p6_stateful import run_stateful_p6
from .red_team import run_red_team
from .traceability import coverage_summary
from .web_app import serve


def cmd_demo() -> int:
    rows = run_stateful_p6()
    print("SOLI SUN — P6 STATEFUL DEMO")
    for row in rows:
        print(f"T{row.turn:02d} {row.name:<28} {row.status}")
    passed = sum(row.status == "PASS" for row in rows)
    print(f"\nP6: {passed}/{len(rows)} PASS")
    return 0 if passed == len(rows) else 1



def cmd_redteam() -> int:
    rows = run_red_team()
    print("SOLI SUN — REFERENCE RED TEAM")
    for row in rows:
        print(f"{row.case_id:<8} {row.status:<4} {row.detail}")
    passed = sum(row.status == "PASS" for row in rows)
    print(f"\nRED TEAM: {passed}/{len(rows)} PASS")
    return 0 if passed == len(rows) else 1

def cmd_traceability() -> int:
    summary = coverage_summary()
    print("SOLI SUN — TRACEABILITY")
    print(f"Constitution: {summary['constitution_covered']}/{summary['constitution_total']} covered")
    print(f"Status: {summary['status']}")
    return 0 if summary["status"] == "PASS" else 1


def _model(provider: str):
    if provider == "openai":
        return OpenAIResponsesModel.from_env()
    return DeterministicReferenceModel()


def cmd_chat(provider: str) -> int:
    try:
        model = _model(provider)
    except ModelError as exc:
        print(f"Model configuration error: {exc}")
        return 2
    print(f"SOLI SUN Alpha — chat ({model.name})")
    print("/quit beendet.\n")
    while True:
        try:
            text = input("Du > ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            return 0
        if text in {"/quit", "/exit"}:
            return 0
        if not text:
            continue
        result = process_live_turn(text, model, build_requested=text.casefold() in {"los", "weiter", "mach weiter"})
        print(f"Soli > {result.final_response}")
        print(f"       [{result.personality.mode.value} · {result.validation.status}]\n")


def cmd_verify(repo: str) -> int:
    result = verify(repo)
    print("SOLI SUN — ALPHA VERIFY")
    print(f"pytest:       {'PASS' if result.pytest_ok else 'FAIL'}")
    print(f"P6:           {result.p6_passed}/{result.p6_total}")
    print(f"Traceability: {result.traceability_status}")
    print(f"ALPHA GATE:   {result.status}")
    return 0 if result.status == "PASS" else 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="soli-sun", description="SOLI SUN alpha integrity reference CLI")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("demo", help="Run the 25-turn stateful P6 reference demo")
    sub.add_parser("traceability", help="Show constitution-to-test traceability coverage")
    sub.add_parser("redteam", help="Run the local reference adversarial suite")

    chat = sub.add_parser("chat", help="Interactive SOLI SUN alpha chat")
    chat.add_argument("--provider", choices=["reference", "openai"], default="reference")

    server = sub.add_parser("serve", help="Run the local alpha web UI")
    server.add_argument("--provider", choices=["reference", "openai"], default="reference")
    server.add_argument("--host", default="127.0.0.1")
    server.add_argument("--port", type=int, default=8765)
    server.add_argument("--db", default=None, help="SQLite database path (or SOLI_DB_PATH)")

    v = sub.add_parser("verify", help="Run the local alpha verification gate")
    v.add_argument("--repo", default=str(Path(__file__).resolve().parents[2]))

    args = parser.parse_args(argv)
    if args.command == "demo":
        return cmd_demo()
    if args.command == "traceability":
        return cmd_traceability()
    if args.command == "redteam":
        return cmd_redteam()
    if args.command == "chat":
        return cmd_chat(args.provider)
    if args.command == "serve":
        try:
            serve(args.host, args.port, args.provider, db_path=args.db)
            return 0
        except ModelError as exc:
            print(f"Model configuration error: {exc}")
            return 2
    if args.command == "verify":
        return cmd_verify(args.repo)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
