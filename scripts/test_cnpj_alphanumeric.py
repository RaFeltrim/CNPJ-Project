#!/usr/bin/env python3
"""Script simples para validar CNPJs (numéricos e alfanuméricos 2026)."""
import argparse
import json
from cnpj_validator.validators.new_alphanumeric_validator import NewAlphanumericCNPJValidator


def main():
    parser = argparse.ArgumentParser(description="Validador de CNPJ (inclui alfanumérico 2026)")
    parser.add_argument('cnpj', nargs='?', help='CNPJ a validar (pode vir formatado)')
    parser.add_argument('--generate', '-g', nargs='?', const='', help='Gera um CNPJ válido. Opcional: fornecer raiz (8 chars)')
    args = parser.parse_args()

    if args.generate is not None:
        root = args.generate or None
        cnpj = NewAlphanumericCNPJValidator.generate_valid_cnpj(root)
        print(cnpj)
        return

    if not args.cnpj:
        print('Informe um CNPJ para validar, ou use --generate para criar um exemplo válido.')
        return

    result = NewAlphanumericCNPJValidator.validate(args.cnpj)
    # Saída legível JSON
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
