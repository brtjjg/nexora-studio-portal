import argparse
from pathlib import Path
from core.production_brain import ProductionBrain

def main():
    parser = argparse.ArgumentParser(description="Generate a narrated lesson video locally.")
    parser.add_argument("--title", required=True)
    parser.add_argument("--notes")
    parser.add_argument("--notes-file")
    parser.add_argument("--lesson-id", default="local-demo")
    parser.add_argument("--output", default="output")
    args = parser.parse_args()

    if args.notes_file:
        notes = Path(args.notes_file).read_text(encoding="utf-8")
    elif args.notes:
        notes = args.notes
    else:
        parser.error("Provide either --notes or --notes-file.")

    brain = ProductionBrain(output_root=args.output)
    result = brain.produce(args.lesson_id, args.title, notes)
    print(result)

if __name__ == "__main__":
    main()
