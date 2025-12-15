"""
Validador Numérico de CNPJ
Responsável pela validação da estrutura numérica e dígitos verificadores
"""

import re


class NumericCNPJValidator:
    """
    Classe responsável pela validação numérica de CNPJ.
    Verifica formato, tamanho e dígitos verificadores.
    """

    @staticmethod
    def remove_formatting(cnpj: str) -> str:
        if not isinstance(cnpj, str):
            return ""
        return re.sub(r'[^0-9]', '', cnpj)

    @staticmethod
    def validate_length(cnpj: str) -> bool:
        return len(cnpj) == 14

    @staticmethod
    def validate_all_same_digits(cnpj: str) -> bool:
        return len(set(cnpj)) > 1

    @staticmethod
    def calculate_first_digit(cnpj: str) -> int:
        weights = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
        sum_result = sum(int(cnpj[i]) * weights[i] for i in range(12))
        remainder = sum_result % 11
        return 0 if remainder < 2 else 11 - remainder

    @staticmethod
    def calculate_second_digit(cnpj: str) -> int:
        weights = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
        sum_result = sum(int(cnpj[i]) * weights[i] for i in range(13))
        remainder = sum_result % 11
        return 0 if remainder < 2 else 11 - remainder

    @staticmethod
    def validate_check_digits(cnpj: str) -> bool:
        if len(cnpj) != 14:
            return False

        first_digit = NumericCNPJValidator.calculate_first_digit(cnpj[:12])
        second_digit = NumericCNPJValidator.calculate_second_digit(cnpj[:13])

        return int(cnpj[12]) == first_digit and int(cnpj[13]) == second_digit

    @staticmethod
    def validate(cnpj: str) -> dict:
        errors = []

        if not cnpj:
            errors.append("CNPJ não pode ser vazio")
            return {'valid': False, 'cnpj_clean': '', 'errors': errors}

        if not isinstance(cnpj, str):
            errors.append("CNPJ deve ser uma string")
            return {'valid': False, 'cnpj_clean': '', 'errors': errors}

        cnpj_clean = NumericCNPJValidator.remove_formatting(cnpj)

        if not cnpj_clean.isdigit():
            errors.append("CNPJ deve conter apenas números")
            return {'valid': False, 'cnpj_clean': cnpj_clean, 'errors': errors}

        if not NumericCNPJValidator.validate_length(cnpj_clean):
            errors.append(f"CNPJ deve ter 14 dígitos, possui {len(cnpj_clean)}")
            return {'valid': False, 'cnpj_clean': cnpj_clean, 'errors': errors}

        if not NumericCNPJValidator.validate_all_same_digits(cnpj_clean):
            errors.append("CNPJ não pode ter todos os dígitos iguais")
            return {'valid': False, 'cnpj_clean': cnpj_clean, 'errors': errors}

        if not NumericCNPJValidator.validate_check_digits(cnpj_clean):
            errors.append("Dígitos verificadores inválidos")
            return {'valid': False, 'cnpj_clean': cnpj_clean, 'errors': errors}

        return {'valid': True, 'cnpj_clean': cnpj_clean, 'errors': []}

    @staticmethod
    def format_cnpj(cnpj: str) -> str:
        cnpj_clean = NumericCNPJValidator.remove_formatting(cnpj)

        if len(cnpj_clean) != 14 or not cnpj_clean.isdigit():
            return ""

        parts = [
            cnpj_clean[:2], cnpj_clean[2:5], cnpj_clean[5:8],
            cnpj_clean[8:12], cnpj_clean[12:]
        ]
        return f"{parts[0]}.{parts[1]}.{parts[2]}/{parts[3]}-{parts[4]}"
