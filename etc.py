from pathlib import Path
import pandas as pd

from pygments import highlight
from pygments.lexers.rdf import TurtleLexer
from pygments.formatters import HtmlFormatter
from IPython.display import HTML


def output_pretty_rdf(ttl: str):
    formatter = HtmlFormatter(style="friendly")
    html = (
        f"<style>{formatter.get_style_defs('.highlight')}</style>"
        + highlight(ttl, TurtleLexer(), formatter)
    )
    return HTML(html)


def export_sheets_to_csv(excel_file: str, output_dir: str = ".") -> None:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    with pd.ExcelFile(excel_file) as workbook:
        for sheet in workbook.sheet_names:
            df = pd.read_excel(workbook, sheet_name=sheet)

            safe_name = "".join(
                c if c.isalnum() or c in ("-", "_") else "_"
                for c in sheet
            )

            csv_path = output_path / f"{safe_name}.csv"
            df.to_csv(csv_path, index=False)

            print(f"Exported {sheet} -> {csv_path}")


