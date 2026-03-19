import argparse
import sys

from doctorate_reader.workflows.newsletter import build_newsletter_html


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generar newsletter HTML con los últimos papers sobre un tema dado.",
    )
    parser.add_argument(
        "topic",
        nargs="?",
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
    parser.add_argument(
        "--profile",
        metavar="PATH",
        default=None,
        help="Ruta a un perfil YAML de usuario para ranking semántico",
    )
    parser.add_argument(
        "--setup-profile",
        metavar="PATH",
        default=None,
        help="Crear perfil interactivo y guardarlo en PATH, luego salir",
    )

    args = parser.parse_args()

    if args.setup_profile:
        from doctorate_reader.skills.user_profile import (
            setup_profile_interactive,
            save_profile,
        )

        profile = setup_profile_interactive()
        save_profile(profile, args.setup_profile)
        print(f"Profile saved to {args.setup_profile}")
        sys.exit(0)

    if not args.topic:
        parser.error("topic is required unless --setup-profile is used")

    user_profile = None
    if args.profile:
        from doctorate_reader.skills.user_profile import load_profile

        user_profile = load_profile(args.profile)

    html = build_newsletter_html(
        topic=args.topic,
        num_results=args.num_results,
        top_n=args.top_n,
        min_year=args.min_year,
        only_open_access=args.only_open_access,
        user_profile=user_profile,
    )

    # Imprimimos el HTML para poder redirigirlo a un archivo o copiar/pegar
    print(html)


if __name__ == "__main__":
    main()


