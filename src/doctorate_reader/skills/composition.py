from datetime import date
from typing import List, Tuple

from doctorate_reader.schemas import Paper


def _format_date_es(d: date) -> str:
    meses = [
        "enero",
        "febrero",
        "marzo",
        "abril",
        "mayo",
        "junio",
        "julio",
        "agosto",
        "septiembre",
        "octubre",
        "noviembre",
        "diciembre",
    ]
    return f"{d.day} de {meses[d.month - 1]} de {d.year}"


def compose_newsletter_html(
    topic: str,
    today: date,
    summarized_top: List[Tuple[Paper, str]],
    summarized_others: List[Tuple[Paper, str]],
    intro_text: str | None = None,
) -> str:
    """Genera un HTML sencillo de newsletter listo para copiar y pegar.

    `summarized_top` y `summarized_others` son listas de tuplas
    (paper, resumen_generado).
    """

    fecha = _format_date_es(today)

    if intro_text is None:
        intro_text = (
            f"En este boletín recopilamos algunos de los papers recientes más "
            f"relevantes sobre '{topic}'. A continuación encontrarás una selección "
            "de trabajos destacados y, después, otros artículos que también "
            "pueden resultarte de interés."
        )

    def render_paper_card(paper: Paper, summary: str) -> str:
        authors = ", ".join(paper.authors) if paper.authors else "Autor/es desconocidos"
        meta_parts = []
        if paper.year:
            meta_parts.append(str(paper.year))
        if paper.journal:
            meta_parts.append(paper.journal)
        meta = " · ".join(meta_parts)

        link_html = ""
        if paper.link:
            link_html = f'<div><a href="{paper.link}" target="_blank" rel="noopener noreferrer">Enlace al paper</a></div>'

        return f"""
        <div class=\"paper-card\">
          <div class=\"paper-title\">{paper.title}</div>
          <div class=\"paper-meta\">{authors}{' · ' + meta if meta else ''}</div>
          <p>{summary}</p>
          {link_html}
        </div>
        """

    top_html = "\n".join(
        render_paper_card(p, s) for p, s in summarized_top
    )
    others_html = "\n".join(
        render_paper_card(p, s) for p, s in summarized_others
    )

    html = f"""<!DOCTYPE html>
<html lang=\"es\">
  <head>
    <meta charset=\"UTF-8\" />
    <title>Boletín de investigación – {topic}</title>
    <style>
      body {{ font-family: system-ui, -apple-system, BlinkMacSystemFont, sans-serif; line-height: 1.6; margin: 0; padding: 0; background: #f3f4f6; }}
      .container {{ max-width: 800px; margin: 0 auto; padding: 1.5rem; background: #ffffff; }}
      h1 {{ margin-top: 0; }}
      .paper-card {{ margin-bottom: 1.2rem; padding: 0.8rem 1rem; border-left: 3px solid #2563eb; background: #f9fafb; }}
      .paper-title {{ font-weight: 600; margin-bottom: 0.2rem; }}
      .paper-meta {{ font-size: 0.9rem; color: #4b5563; margin-bottom: 0.4rem; }}
      a {{ color: #2563eb; text-decoration: none; }}
      a:hover {{ text-decoration: underline; }}
    </style>
  </head>
  <body>
    <div class=\"container\">
      <h1>Boletín de investigación en {topic}</h1>
      <p><em>{fecha}</em></p>

      <p>{intro_text}</p>

      <h2>Top {len(summarized_top)} papers</h2>
      {top_html}

      <h2>Otros papers interesantes</h2>
      {others_html}
    </div>
  </body>
</html>
"""

    return html


