#!/usr/bin/env python3
"""
CNPJ Validator CLI - Interface de Linha de Comando (cópia simplificada)
"""

import argparse
import sys
import json
from typing import List, Optional

try:
    from cnpj_validator import CNPJValidator
    from cnpj_validator.validators.new_alphanumeric_validator import NewAlphanumericCNPJValidator
except Exception:
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from cnpj_validator import CNPJValidator
    from cnpj_validator.validators.new_alphanumeric_validator import NewAlphanumericCNPJValidator


class CNPJValidatorCLI:
    def __init__(self):
        self.validator = CNPJValidator()
        self.alphanumeric_validator = NewAlphanumericCNPJValidator()

    def validate(self, cnpj: str, verbose: bool = False) -> dict:
        result = self.validator.validate(cnpj)
        if verbose:
            return result
        return {'valid': result['valid'], 'cnpj': result.get('cnpj_formatted', cnpj), 'errors': result.get('errors', [])}

    def generate(self, count: int = 1, alphanumeric: bool = False, root: Optional[str] = None, formatted: bool = True) -> List[str]:
        cnpjs = []
        for _ in range(count):
            if root:
                cnpj = self.alphanumeric_validator.generate_valid_cnpj(root)
            elif alphanumeric:
                import random, string
                chars = string.ascii_uppercase + string.digits
                random_root = ''.join(random.choices(chars, k=8))
                cnpj = self.alphanumeric_validator.generate_valid_cnpj(random_root)
            else:
                import random
                random_root = ''.join([str(random.randint(0, 9)) for _ in range(8)])
                cnpj = self.alphanumeric_validator.generate_valid_cnpj(random_root)

            if formatted:
                cnpj = self._format_cnpj(cnpj)
            cnpjs.append(cnpj)
        return cnpjs

    def _format_cnpj(self, cnpj: str) -> str:
        cnpj = cnpj.replace('.', '').replace('/', '').replace('-', '').upper()
        if len(cnpj) != 14:
            return cnpj
        return f"{cnpj[:2]}.{cnpj[2:5]}.{cnpj[5:8]}/{cnpj[8:12]}-{cnpj[12:14]}"

    def format(self, cnpj: str) -> str:
        return self._format_cnpj(cnpj)

    def info(self, cnpj: str) -> dict:
        return self.validator.get_info(cnpj)

    def batch_validate(self, file_path: str) -> List[dict]:
        results = []
        with open(file_path, 'r') as f:
            for line in f:
                cnpj = line.strip()
                if cnpj:
                    result = self.validate(cnpj)
                    results.append(result)
        return results


def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog='cnpj-validator', description='Validador de CNPJ brasileiro')
    parser.add_argument('--version', '-v', action='version', version='%(prog)s 2.0.0')
    subparsers = parser.add_subparsers(dest='command', help='Comandos')
    validate_parser = subparsers.add_parser('validate', help='Valida um CNPJ')
    validate_parser.add_argument('cnpj', help='CNPJ a ser validado')
    validate_parser.add_argument('--verbose', '-V', action='store_true')
    validate_parser.add_argument('--json', '-j', action='store_true')
    generate_parser = subparsers.add_parser('generate', help='Gera CNPJs')
    generate_parser.add_argument('--count', '-n', type=int, default=1)
    generate_parser.add_argument('--alphanumeric', '-a', action='store_true')
    generate_parser.add_argument('--root', '-r', type=str)
    generate_parser.add_argument('--no-format', action='store_true')
    generate_parser.add_argument('--json', '-j', action='store_true')
    format_parser = subparsers.add_parser('format', help='Formata um CNPJ')
    format_parser.add_argument('cnpj', help='CNPJ a ser formatado')
    info_parser = subparsers.add_parser('info', help='Mostra informações do CNPJ')
    info_parser.add_argument('cnpj', help='CNPJ a consultar')
    batch_parser = subparsers.add_parser('batch', help='Valida CNPJs em lote')
    batch_parser.add_argument('file', help='Arquivo com CNPJs')
    return parser


def main():
    parser = create_parser()
    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(0)

    cli = CNPJValidatorCLI()
    try:
        if args.command == 'validate':
            result = cli.validate(args.cnpj, verbose=args.verbose)
            if args.json:
                print(json.dumps(result, indent=2, ensure_ascii=False))
            else:
                if result['valid']:
                    print(f"✅ CNPJ válido: {result['cnpj']}")
                else:
                    print(f"❌ CNPJ inválido: {args.cnpj}")
                    for error in result.get('errors', []):
                        print(f"   └─ {error}")
                sys.exit(0 if result['valid'] else 1)
    except Exception as e:
        print(f"❌ Erro: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
