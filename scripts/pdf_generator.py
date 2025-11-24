"""CLI entry point for PDF generation using `src.pdf_generator.PDFGenerator`.

This script is the public CLI wrapper; the core implementation lives in `src/pdf_generator.py`.
"""

from pathlib import Path
import argparse
import sys

from src.pdf_generator import PDFGenerator


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate beautiful PDFs from markdown files."
    )
    parser.add_argument(
        "--input",
        "-i",
        dest="input_file",
        required=False,
        help="Path to markdown file (or versioned PDF when using --finalize).",
    )
    parser.add_argument(
        "--content-type",
        choices=["chapter", "jam_plan"],
        default="chapter",
        help="Type of content (default: chapter).",
    )
    parser.add_argument(
        "--theme",
        required=False,
        help="Theme name for output filename (e.g., BaseReality, CommitmentAndListening).",
    )
    parser.add_argument(
        "--language",
        choices=["ru", "en"],
        default="ru",
        help="Language code (default: ru).",
    )
    parser.add_argument(
        "--title",
        required=False,
        help="Optional title override for PDF.",
    )
    parser.add_argument(
        "--finalize",
        metavar="PDF_PATH",
        help="Finalize a versioned PDF: remove version suffix and clean up temp versions.",
    )
    parser.add_argument(
        "--keep-versions",
        action="store_true",
        help="When finalizing, keep other versioned files (default: remove them).",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    project_root = Path.cwd()
    assets_dir = project_root / "assets"
    logs_dir = project_root / "logs"

    try:
        pdf_gen = PDFGenerator(assets_dir=assets_dir, logs_dir=logs_dir)
    except ImportError as exc:
        print(f"❌ Error: {exc}", file=sys.stderr)
        return 1

    # Finalize mode
    if args.finalize:
        finalize_path = Path(args.finalize)
        if not finalize_path.exists():
            print(f"❌ Error: PDF file not found: {finalize_path}", file=sys.stderr)
            return 1
        if finalize_path.suffix.lower() != ".pdf":
            print(f"❌ Error: File must be a PDF: {finalize_path}", file=sys.stderr)
            return 1

        try:
            print(f"📄 Finalizing PDF: {finalize_path}")
            final_path = pdf_gen.finalize_pdf(
                versioned_pdf_path=finalize_path,
                remove_other_versions=not args.keep_versions,
            )
            print(f"🎉 Success! Finalized PDF: {final_path.name}")
            return 0
        except Exception as exc:  # noqa: BLE001
            print(f"❌ Error finalizing PDF: {exc}", file=sys.stderr)
            return 1

    # Generate PDF mode
    if not args.input_file:
        print("❌ --input is required for PDF generation (or use --finalize).", file=sys.stderr)
        return 1
    if not args.theme:
        print("❌ --theme is required for PDF generation.", file=sys.stderr)
        return 1

    input_path = Path(args.input_file)
    if not input_path.exists():
        print(f"❌ Error: Input file not found: {input_path}", file=sys.stderr)
        return 1
    if input_path.suffix.lower() != ".md":
        print(f"❌ Error: Input file must be a markdown file (.md): {input_path}", file=sys.stderr)
        return 1

    try:
        print(f"📄 Generating PDF from: {input_path}")
        print(f"📋 Content type: {args.content_type}")
        print(f"🎨 Theme: {args.theme}")

        output_path = pdf_gen.generate_pdf(
            input_file=input_path,
            content_type=args.content_type,
            theme_name=args.theme,
            language=args.language,
            title=args.title,
        )
        print(f"🎉 Success! PDF created: {output_path.name}")
        return 0
    except Exception as exc:  # noqa: BLE001
        print(f"❌ Error generating PDF: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())


