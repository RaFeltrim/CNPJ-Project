"""
Validador Alfanumérico de CNPJ
Responsável pela validação de padrões alfanuméricos e formatação
"""

import re


class AlphanumericCNPJValidator:
    CNPJ_PATTERN = re.compile(r'^\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}$')
    CNPJ_DIGITS_PATTERN = re.compile(r'^\d{14}$')

    @staticmethod
    def validate_format(cnpj: str) -> dict:
        errors = []
        if not isinstance(cnpj, str):
            errors.append("CNPJ deve ser uma string")
            return {'valid': False, 'errors': errors}

        if AlphanumericCNPJValidator.CNPJ_PATTERN.match(cnpj):
            return {'valid': True, 'errors': []}

        if AlphanumericCNPJValidator.CNPJ_DIGITS_PATTERN.match(cnpj):
            errors.append("CNPJ sem formatação - esperado: XX.XXX.XXX/XXXX-XX")
            return {'valid': False, 'errors': errors}

        errors.append("Formato inválido - esperado: XX.XXX.XXX/XXXX-XX")
        return {'valid': False, 'errors': errors}

    @staticmethod
    def validate_special_characters(cnpj: str) -> dict:
        errors = []
        if not isinstance(cnpj, str):
            errors.append("CNPJ deve ser uma string")
            return {'valid': False, 'errors': errors}

        valid_chars = set('0123456789./-')
        invalid_chars = set(cnpj) - valid_chars

        if invalid_chars:
            errors.append(f"Caracteres inválidos encontrados: {', '.join(sorted(invalid_chars))}")
            return {'valid': False, 'errors': errors}

        return {'valid': True, 'errors': []}

    @staticmethod
    def validate_separator_positions(cnpj: str) -> dict:
        errors = []
        if len(cnpj) != 18:
            errors.append(f"Tamanho incorreto: {len(cnpj)} caracteres, esperado: 18")
            return {'valid': False, 'errors': errors}

        if cnpj[2] != '.':
            errors.append(f"Esperado '.' na posição 3, encontrado '{cnpj[2]}'")
        if cnpj[6] != '.':
            errors.append(f"Esperado '.' na posição 7, encontrado '{cnpj[6]}'")
        if cnpj[10] != '/':
            errors.append(f"Esperado '/' na posição 11, encontrado '{cnpj[10]}'")
        if cnpj[15] != '-':
            errors.append(f"Esperado '-' na posição 16, encontrado '{cnpj[15]}'")

        if errors:
            return {'valid': False, 'errors': errors}
        return {'valid': True, 'errors': []}

    @staticmethod
    def validate_matriz_filial(cnpj: str) -> dict:
        errors = []
        info = {}
        if not AlphanumericCNPJValidator.CNPJ_PATTERN.match(cnpj):
            errors.append("CNPJ deve estar formatado corretamente")
            return {'valid': False, 'errors': errors, 'info': {}}

        filial_code = cnpj[11:15]
        if not filial_code.isdigit():
            errors.append(f"Código de matriz/filial inválido: {filial_code}")
            return {'valid': False, 'errors': errors, 'info': {}}

        filial_number = int(filial_code)
        if filial_number == 0:
            errors.append("Código de matriz/filial não pode ser 0000")
            info['type'] = 'inválido'
        elif filial_number == 1:
            info['type'] = 'matriz'
            info['code'] = filial_code
        else:
            info['type'] = 'filial'
            info['code'] = filial_code
            info['number'] = filial_number

        return {'valid': len(errors) == 0, 'errors': errors, 'info': info}

    @staticmethod
    def validate_whitespace(cnpj: str) -> dict:
        errors = []
        warnings = []
        if cnpj != cnpj.strip():
            warnings.append("CNPJ contém espaços no início ou fim")
        if ' ' in cnpj:
            errors.append("CNPJ contém espaços em branco")
        if '\t' in cnpj:
            errors.append("CNPJ contém tabulações")
        if '\n' in cnpj or '\r' in cnpj:
            errors.append("CNPJ contém quebras de linha")
        return {'valid': len(errors) == 0, 'errors': errors, 'warnings': warnings}

    @staticmethod
    def extract_parts(cnpj: str) -> dict:
        if not AlphanumericCNPJValidator.CNPJ_PATTERN.match(cnpj):
            return {'valid': False, 'error': 'CNPJ deve estar no formato XX.XXX.XXX/XXXX-XX'}

        return {
            'valid': True,
            'raiz': cnpj[0:2] + cnpj[3:6] + cnpj[7:10],
            'ordem': cnpj[11:15],
            'dv': cnpj[16:18],
            'formatted': cnpj
        }

    @staticmethod
    def validate(cnpj: str) -> dict:
        all_errors = []
        all_warnings = []
        if not cnpj:
            return {'valid': False, 'errors': ['CNPJ não pode ser vazio'], 'warnings': []}

        whitespace_result = AlphanumericCNPJValidator.validate_whitespace(cnpj)
        all_errors.extend(whitespace_result['errors'])
        all_warnings.extend(whitespace_result.get('warnings', []))

        cnpj_trimmed = cnpj.strip()

        chars_result = AlphanumericCNPJValidator.validate_special_characters(cnpj_trimmed)
        if not chars_result['valid']:
            all_errors.extend(chars_result['errors'])
            return {'valid': False, 'errors': all_errors, 'warnings': all_warnings}

        format_result = AlphanumericCNPJValidator.validate_format(cnpj_trimmed)
        if not format_result['valid']:
            all_errors.extend(format_result['errors'])
            return {'valid': False, 'errors': all_errors, 'warnings': all_warnings}

        separator_result = AlphanumericCNPJValidator.validate_separator_positions(cnpj_trimmed)
        if not separator_result['valid']:
            all_errors.extend(separator_result['errors'])

        filial_result = AlphanumericCNPJValidator.validate_matriz_filial(cnpj_trimmed)
        if not filial_result['valid']:
            all_errors.extend(filial_result['errors'])

        parts = AlphanumericCNPJValidator.extract_parts(cnpj_trimmed)

        return {
            'valid': len(all_errors) == 0,
            'errors': all_errors,
            'warnings': all_warnings,
            'parts': parts if parts.get('valid') else None,
            'filial_info': filial_result.get('info')
        }
