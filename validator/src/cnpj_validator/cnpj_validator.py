"""
CNPJ Validator - Módulo Principal
Integra validações numéricas e alfanuméricas de CNPJ
"""

from .validators.numeric_validator import NumericCNPJValidator
from .validators.alphanumeric_validator import AlphanumericCNPJValidator


class CNPJValidator:
    def __init__(self):
        self.numeric_validator = NumericCNPJValidator()
        self.alphanumeric_validator = AlphanumericCNPJValidator()

    def validate(self, cnpj: str, validate_format: bool = True) -> dict:
        result = {
            'valid': False,
            'cnpj_input': cnpj,
            'cnpj_clean': '',
            'cnpj_formatted': '',
            'numeric_validation': {},
            'alphanumeric_validation': {},
            'errors': [],
            'warnings': []
        }

        numeric_result = self.numeric_validator.validate(cnpj)
        result['numeric_validation'] = numeric_result
        result['cnpj_clean'] = numeric_result.get('cnpj_clean', '')

        if not numeric_result['valid']:
            result['errors'].extend(numeric_result['errors'])
            return result

        result['cnpj_formatted'] = self.numeric_validator.format_cnpj(result['cnpj_clean'])

        if validate_format:
            if '.' in cnpj or '/' in cnpj or '-' in cnpj:
                alphanumeric_result = self.alphanumeric_validator.validate(cnpj)
            else:
                alphanumeric_result = self.alphanumeric_validator.validate(result['cnpj_formatted'])
                result['warnings'].append("CNPJ fornecido sem formatação")

            result['alphanumeric_validation'] = alphanumeric_result

            if not alphanumeric_result['valid']:
                result['errors'].extend(alphanumeric_result['errors'])

            if alphanumeric_result.get('warnings'):
                result['warnings'].extend(alphanumeric_result['warnings'])

        if validate_format:
            result['valid'] = numeric_result['valid'] and result['alphanumeric_validation'].get('valid', False)
        else:
            result['valid'] = numeric_result['valid']

        return result

    def validate_numeric_only(self, cnpj: str) -> dict:
        return self.numeric_validator.validate(cnpj)

    def validate_alphanumeric_only(self, cnpj: str) -> dict:
        return self.alphanumeric_validator.validate(cnpj)

    def format(self, cnpj: str) -> str:
        validation = self.numeric_validator.validate(cnpj)
        if not validation['valid']:
            return f"Erro: {', '.join(validation['errors'])}"
        return self.numeric_validator.format_cnpj(validation['cnpj_clean'])

    def clean(self, cnpj: str) -> str:
        return self.numeric_validator.remove_formatting(cnpj)

    def get_info(self, cnpj: str) -> dict:
        validation = self.validate(cnpj, validate_format=True)
        if not validation['valid']:
            return {'valid': False, 'errors': validation['errors']}

        info = {
            'valid': True,
            'cnpj_formatted': validation['cnpj_formatted'],
            'cnpj_clean': validation['cnpj_clean']
        }

        alphanumeric = validation.get('alphanumeric_validation', {})
        if alphanumeric.get('filial_info'):
            info['matriz_filial'] = alphanumeric['filial_info']

        if alphanumeric.get('parts'):
            info['parts'] = alphanumeric['parts']

        return info

    @staticmethod
    def is_valid(cnpj: str) -> bool:
        validator = CNPJValidator()
        result = validator.validate(cnpj, validate_format=False)
        return result['valid']
