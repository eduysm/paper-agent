import argparse

from doctorate_reader.workflows.newsletter import build_newsletter_html


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generar newsletter HTML con los últimos papers sobre un tema dado.",
    )
    parser.add_argument(
        "topic",
        help="Tema de la newsletter, por ejemplo: 'política económica'",
    )
    parser.add_argument(
        "--top-n",
        type=int,
        default=5,
        help="Número de papers destacados en la sección Top (por defecto 5)",
    )
    parser.add_argument(
        "--num-results",
        type=int,
        default=20,
        help="Número total de resultados a recuperar de OpenAlex (por defecto 20)",
    )
    parser.add_argument(
        "--min-year",
        type=int,
        default=None,
        help="Año mínimo de publicación para filtrar resultados (opcional)",
    )
    parser.add_argument(
        "--only-open-access",
        action="store_true",
        help="Si se indica, solo incluye papers open access",
    )

    args = parser.parse_args()

    html = build_newsletter_html(
        topic=args.topic,
        num_results=args.num_results,
        top_n=args.top_n,
        min_year=args.min_year,
        only_open_access=args.only_open_access,
    )

    # Imprimimos el HTML para poder redirigirlo a un archivo o copiar/pegar
    print(html)


if __name__ == "__main__":
    main()


