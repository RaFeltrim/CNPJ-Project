"""
Validador de CNPJ Alfanumérico (Novo Formato)

A Receita Federal anunciou que a partir de 2026, os CNPJs poderão conter
letras e números no bloco da raiz (8 primeiros caracteres).

Formato: AA.AAA.AAA/NNNN-DD
- AA.AAA.AAA = Raiz (8 caracteres alfanuméricos: letras A-Z e números 0-9)
- NNNN = Ordem do estabelecimento (4 dígitos numéricos)
- DD = Dígitos verificadores (2 dígitos numéricos)

Referência: https://www.gov.br/receitafederal/pt-br
"""

import re
from typing import Optional


class NewAlphanumericCNPJValidator:
    """
    Validador para o novo formato de CNPJ alfanumérico.

    O novo formato permite letras (A-Z) nos 8 primeiros caracteres (raiz),
    mantendo os 6 últimos apenas numéricos (ordem + DV).
    """

    # Caracteres válidos para a raiz (A-Z e 0-9)
    VALID_ROOT_CHARS = set('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789')

    # Mapeamento de caracteres para valores no cálculo do DV
    # Letras são convertidas para números: A=10, B=11, ..., Z=35
    CHAR_VALUES = {chr(i): i - 55 for i in range(65, 91)}  # A-Z -> 10-35
    CHAR_VALUES.update({str(i): i for i in range(10)})      # 0-9 -> 0-9

    # Pesos para cálculo dos dígitos verificadores (mesmo algoritmo do CNPJ tradicional)
    WEIGHTS_FIRST = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    WEIGHTS_SECOND = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]

    @staticmethod
    def remove_formatting(cnpj: str) -> str:
        """
        Remove formatação do CNPJ (pontos, traços e barras).
        Mantém letras e números.

        Args:
            cnpj: String com CNPJ formatado ou não

        Returns:
            String contendo apenas letras e números do CNPJ (uppercase)
        """
        if not isinstance(cnpj, str):
            return ""
        # Remove tudo exceto letras e números, converte para maiúsculo
        return re.sub(r'[^A-Za-z0-9]', '', cnpj).upper()

    @staticmethod
    def validate_length(cnpj: str) -> dict:
        """
        Valida se o CNPJ possui exatamente 14 caracteres.

        Args:
            cnpj: String com CNPJ sem formatação

        Returns:
            Dict com resultado da validação
        """
        is_valid = len(cnpj) == 14
        return {
            'valid': is_valid,
            'length': len(cnpj),
            'errors': [] if is_valid else [f"CNPJ deve ter 14 caracteres, possui {len(cnpj)}"]
        }

    @staticmethod
    def validate_root_chars(cnpj: str) -> dict:
        """
        Valida se a raiz (8 primeiros caracteres) contém apenas letras A-Z e números 0-9.

        Args:
            cnpj: String com CNPJ sem formatação (14 caracteres)

        Returns:
            Dict com resultado da validação
        """
        if len(cnpj) < 8:
            return {'valid': False, 'errors': ["CNPJ muito curto para validar raiz"]}

        root = cnpj[:8].upper()
        invalid_chars = [c for c in root if c not in NewAlphanumericCNPJValidator.VALID_ROOT_CHARS]

        is_valid = len(invalid_chars) == 0
        return {
            'valid': is_valid,
            'root': root,
            'has_letters': any(c.isalpha() for c in root),
            'has_numbers': any(c.isdigit() for c in root),
            'invalid_chars': invalid_chars,
            'errors': [] if is_valid else [f"Raiz contém caracteres inválidos: {invalid_chars}"]
        }

    @staticmethod
    def validate_order_digits(cnpj: str) -> dict:
        """
        Valida se a ordem (posições 9-12) contém apenas números.

        Args:
            cnpj: String com CNPJ sem formatação (14 caracteres)

        Returns:
            Dict com resultado da validação
        """
        if len(cnpj) < 12:
            return {'valid': False, 'errors': ["CNPJ muito curto para validar ordem"]}

        order = cnpj[8:12]
        is_valid = order.isdigit()

        return {
            'valid': is_valid,
            'order': order,
            'is_matriz': order == '0001' if is_valid else None,
            'errors': [] if is_valid else [f"Ordem deve conter apenas números, recebido: {order}"]
        }

    @staticmethod
    def validate_check_digits_format(cnpj: str) -> dict:
        """
        Valida se os dígitos verificadores (posições 13-14) são numéricos.

        Args:
            cnpj: String com CNPJ sem formatação (14 caracteres)

        Returns:
            Dict com resultado da validação
        """
        if len(cnpj) < 14:
            return {'valid': False, 'errors': ["CNPJ muito curto para validar DV"]}

        dv = cnpj[12:14]
        is_valid = dv.isdigit()

        error_msg = f"Dígitos verificadores devem ser numéricos, recebido: {dv}"
        return {
            'valid': is_valid,
            'dv': dv,
            'errors': [] if is_valid else [error_msg]
        }

    @staticmethod
    def get_char_value(char: str) -> int:
        """
        Retorna o valor numérico de um caractere para cálculo do DV.

        Args:
            char: Caractere (letra ou número)

        Returns:
            Valor numérico (0-9 para números, 10-35 para letras A-Z)
        """
        return NewAlphanumericCNPJValidator.CHAR_VALUES.get(char.upper(), 0)

    @staticmethod
    def calculate_first_digit(cnpj: str) -> int:
        """
        Calcula o primeiro dígito verificador do CNPJ alfanumérico.

        Args:
            cnpj: String com os primeiros 12 caracteres do CNPJ

        Returns:
            Primeiro dígito verificador calculado
        """
        weights = NewAlphanumericCNPJValidator.WEIGHTS_FIRST
        total = 0

        for i, char in enumerate(cnpj[:12]):
            value = NewAlphanumericCNPJValidator.get_char_value(char)
            total += value * weights[i]

        remainder = total % 11
        return 0 if remainder < 2 else 11 - remainder

    @staticmethod
    def calculate_second_digit(cnpj: str) -> int:
        """
        Calcula o segundo dígito verificador do CNPJ alfanumérico.

        Args:
            cnpj: String com os primeiros 13 caracteres do CNPJ

        Returns:
            Segundo dígito verificador calculado
        """
        weights = NewAlphanumericCNPJValidator.WEIGHTS_SECOND
        total = 0

        for i, char in enumerate(cnpj[:13]):
            value = NewAlphanumericCNPJValidator.get_char_value(char)
            total += value * weights[i]

        remainder = total % 11
        return 0 if remainder < 2 else 11 - remainder

    @staticmethod
    def validate_check_digits(cnpj: str) -> dict:
        """
        Valida os dígitos verificadores do CNPJ alfanumérico.

        Args:
            cnpj: String com CNPJ completo (14 caracteres)

        Returns:
            Dict com resultado da validação
        """
        if len(cnpj) != 14:
            return {'valid': False, 'errors': ["CNPJ deve ter 14 caracteres"]}

        # Verifica se os últimos 2 caracteres são numéricos
        if not cnpj[12:14].isdigit():
            return {'valid': False, 'errors': ["Dígitos verificadores devem ser numéricos"]}

        first_digit = NewAlphanumericCNPJValidator.calculate_first_digit(cnpj[:12])
        second_digit = NewAlphanumericCNPJValidator.calculate_second_digit(
            cnpj[:12] + str(first_digit))

        expected_dv = f"{first_digit}{second_digit}"
        actual_dv = cnpj[12:14]

        is_valid = expected_dv == actual_dv

        error_msg = f"DV inválido. Esperado: {expected_dv}, Recebido: {actual_dv}"
        return {
            'valid': is_valid,
            'expected_dv': expected_dv,
            'actual_dv': actual_dv,
            'first_digit_calc': first_digit,
            'second_digit_calc': second_digit,
            'errors': [] if is_valid else [error_msg]
        }

    @staticmethod
    def validate_not_all_same(cnpj: str) -> dict:
        """
        Verifica se o CNPJ não possui todos os caracteres iguais.

        Args:
            cnpj: String com CNPJ sem formatação

        Returns:
            Dict com resultado da validação
        """
        is_valid = len(set(cnpj)) > 1
        return {
            'valid': is_valid,
            'errors': [] if is_valid else ["CNPJ não pode ter todos os caracteres iguais"]
        }

    @staticmethod
    def validate_format(cnpj: str) -> dict:
        """
        Valida se o CNPJ está no formato correto: AA.AAA.AAA/NNNN-DD

        Args:
            cnpj: String com CNPJ formatado

        Returns:
            Dict com resultado da validação
        """
        # Padrão: 2 alfanum, ponto, 3 alfanum, ponto, 3 alfanum, barra, 4 num, hífen, 2 num
        pattern = r'^[A-Za-z0-9]{2}\.[A-Za-z0-9]{3}\.[A-Za-z0-9]{3}/[0-9]{4}-[0-9]{2}$'

        is_valid = bool(re.match(pattern, cnpj))

        format_error = "Formato inválido. Use: AA.AAA.AAA/NNNN-DD (A=letra ou número, N=número)"
        return {
            'valid': is_valid,
            'format': 'AA.AAA.AAA/NNNN-DD',
            'errors': [] if is_valid else [format_error]
        }

    @staticmethod
    def format_cnpj(cnpj: str) -> str:
        """
        Formata o CNPJ no padrão AA.AAA.AAA/NNNN-DD.

        Args:
            cnpj: String com CNPJ sem formatação (14 caracteres)

        Returns:
            String com CNPJ formatado ou vazio se inválido
        """
        cnpj_clean = NewAlphanumericCNPJValidator.remove_formatting(cnpj)

        if len(cnpj_clean) != 14:
            return ""

        parts = [
            cnpj_clean[:2], cnpj_clean[2:5], cnpj_clean[5:8],
            cnpj_clean[8:12], cnpj_clean[12:]
        ]
        return f"{parts[0]}.{parts[1]}.{parts[2]}/{parts[3]}-{parts[4]}"

    @staticmethod
    def extract_parts(cnpj: str) -> Optional[dict]:
        """
        Extrai as partes do CNPJ alfanumérico.

        Args:
            cnpj: String com CNPJ (com ou sem formatação)

        Returns:
            Dict com as partes ou None se inválido
        """
        cnpj_clean = NewAlphanumericCNPJValidator.remove_formatting(cnpj)

        if len(cnpj_clean) != 14:
            return None

        return {
            'raiz': cnpj_clean[:8],
            'ordem': cnpj_clean[8:12],
            'dv': cnpj_clean[12:14],
            'is_matriz': cnpj_clean[8:12] == '0001',
            'has_letters': any(c.isalpha() for c in cnpj_clean[:8])
        }

    @staticmethod
    def validate(cnpj: str) -> dict:
        """
        Realiza validação completa do CNPJ alfanumérico.

        Args:
            cnpj: String com CNPJ (com ou sem formatação)

        Returns:
            Dict com resultado completo da validação
        """
        errors = []

        if not cnpj:
            return {
                'valid': False,
                'cnpj_clean': '',
                'cnpj_formatted': '',
                'errors': ["CNPJ não pode ser vazio"]
            }

        if not isinstance(cnpj, str):
            return {
                'valid': False,
                'cnpj_clean': '',
                'cnpj_formatted': '',
                'errors': ["CNPJ deve ser uma string"]
            }

        cnpj_clean = NewAlphanumericCNPJValidator.remove_formatting(cnpj)

        # Validação de tamanho
        length_result = NewAlphanumericCNPJValidator.validate_length(cnpj_clean)
        if not length_result['valid']:
            errors.extend(length_result['errors'])
            return {
                'valid': False,
                'cnpj_clean': cnpj_clean,
                'cnpj_formatted': '',
                'errors': errors
            }

        # Validação de caracteres da raiz
        root_result = NewAlphanumericCNPJValidator.validate_root_chars(cnpj_clean)
        if not root_result['valid']:
            errors.extend(root_result['errors'])

        # Validação da ordem
        order_result = NewAlphanumericCNPJValidator.validate_order_digits(cnpj_clean)
        if not order_result['valid']:
            errors.extend(order_result['errors'])

        # Validação do formato dos DVs
        dv_format_result = NewAlphanumericCNPJValidator.validate_check_digits_format(cnpj_clean)
        if not dv_format_result['valid']:
            errors.extend(dv_format_result['errors'])

        # Validação de todos iguais
        same_result = NewAlphanumericCNPJValidator.validate_not_all_same(cnpj_clean)
        if not same_result['valid']:
            errors.extend(same_result['errors'])

        # Validação dos dígitos verificadores
        if not errors:  # Só valida DV se não houver erros anteriores
            dv_result = NewAlphanumericCNPJValidator.validate_check_digits(cnpj_clean)
            if not dv_result['valid']:
                errors.extend(dv_result['errors'])

        cnpj_formatted = NewAlphanumericCNPJValidator.format_cnpj(cnpj_clean)
        parts = NewAlphanumericCNPJValidator.extract_parts(cnpj_clean)

        return {
            'valid': len(errors) == 0,
            'cnpj_clean': cnpj_clean,
            'cnpj_formatted': cnpj_formatted,
            'is_alphanumeric': parts.get('has_letters', False) if parts else False,
            'is_matriz': parts.get('is_matriz') if parts else None,
            'parts': parts,
            'errors': errors
        }

    @staticmethod
    def generate_valid_cnpj(root: str = None) -> str:
        """
        Gera um CNPJ alfanumérico válido.

        Args:
            root: Raiz do CNPJ (8 caracteres). Se não fornecido, gera aleatório.

        Returns:
            CNPJ alfanumérico válido formatado
        """
        import random
        import string

        if root:
            root = root.upper()[:8].ljust(8, '0')
        else:
            # Gera raiz aleatória com letras e números
            chars = string.ascii_uppercase + string.digits
            root = ''.join(random.choices(chars, k=8))

        # Ordem (usar 0001 para matriz)
        order = '0001'

        # Calcula os dígitos verificadores
        base = root + order
        first_digit = NewAlphanumericCNPJValidator.calculate_first_digit(base)
        second_digit = NewAlphanumericCNPJValidator.calculate_second_digit(base + str(first_digit))

        cnpj = base + str(first_digit) + str(second_digit)

        return NewAlphanumericCNPJValidator.format_cnpj(cnpj)