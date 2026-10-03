"""NISE command line interface."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from .compiler import compile_schematic, inspect_schematic
from .contracts import validate_catalog, validate_query
from .io import load_json, save_new


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="nise",
        description="Construct and inspect bounded candidate inference schematics.",
    )
    commands = parser.add_subparsers(dest="command", required=True)

    compile_cmd = commands.add_parser("compile")
    compile_cmd.add_argument("catalog", type=Path)
    compile_cmd.add_argument("query", type=Path)
    compile_cmd.add_argument("--output", type=Path, required=True)

    inspect_cmd = commands.add_parser("inspect")
    inspect_cmd.add_argument("schematic", type=Path)

    validate_cmd = commands.add_parser("validate")
    validate_cmd.add_argument("kind", choices=("catalog", "query"))
    validate_cmd.add_argument("file", type=Path)

    args = parser.parse_args(argv)
    try:
        if args.command == "compile":
            result = compile_schematic(load_json(args.catalog), load_json(args.query))
            save_new(args.output, result)
            print(json.dumps({
                "status": "compiled",
                "schematic_id": result["schematic_id"],
                "output": str(args.output),
                "physical_truth_established": False,
                "execution_authority": False,
            }))
            return 0
        if args.command == "inspect":
            print(json.dumps(inspect_schematic(load_json(args.schematic)), indent=2))
            return 0
        value = load_json(args.file)
        result = validate_catalog(value) if args.kind == "catalog" else validate_query(value)
        print(json.dumps({"status": "valid", "schema": result["schema"]}))
        return 0
    except (OSError, ValueError, TypeError, KeyError, UnicodeError, json.JSONDecodeError) as exc:
        print(json.dumps({"status": "refused", "reason": str(exc)}), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
