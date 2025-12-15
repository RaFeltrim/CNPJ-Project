"""
Testes para o validador de CNPJ Alfanumérico (Novo Formato)

Testa a validação de CNPJs com letras na raiz, conforme previsto
pela Receita Federal para implementação a partir de 2026.
"""

import pytest
from cnpj_validator.validators.new_alphanumeric_validator import NewAlphanumericCNPJValidator


class TestNewAlphanumericCNPJValidator:
    """Testes para o validador de CNPJ alfanumérico"""

    def test_remove_formatting_with_dots_and_slash(self):
        result = NewAlphanumericCNPJValidator.remove_formatting("AB.CDE.123/0001-45")
        assert result == "ABCDE123000145"

    def test_remove_formatting_preserves_letters(self):
        result = NewAlphanumericCNPJValidator.remove_formatting("ab.cde.xyz/0001-00")
        assert result == "ABCDEXYZ000100"

    def test_remove_formatting_with_numbers_only(self):
        result = NewAlphanumericCNPJValidator.remove_formatting("11.222.333/0001-81")
        assert result == "11222333000181"

    def test_remove_formatting_with_none(self):
        result = NewAlphanumericCNPJValidator.remove_formatting(None)
        assert result == ""

    def test_remove_formatting_with_empty_string(self):
        result = NewAlphanumericCNPJValidator.remove_formatting("")
        assert result == ""

    def test_validate_length_valid(self):
        result = NewAlphanumericCNPJValidator.validate_length("ABCDE123000145")
        assert result['valid'] is True
        assert result['length'] == 14

    def test_validate_length_too_short(self):
        result = NewAlphanumericCNPJValidator.validate_length("ABCDE12300014")
        assert result['valid'] is False
        assert result['length'] == 13
        assert len(result['errors']) > 0

    def test_validate_length_too_long(self):
        result = NewAlphanumericCNPJValidator.validate_length("ABCDE1230001456")
        assert result['valid'] is False
        assert result['length'] == 15

    def test_validate_root_with_letters_only(self):
        result = NewAlphanumericCNPJValidator.validate_root_chars("ABCDEFGH000100")
        assert result['valid'] is True
        assert result['has_letters'] is True
        assert result['has_numbers'] is False

    def test_validate_root_with_numbers_only(self):
        result = NewAlphanumericCNPJValidator.validate_root_chars("12345678000100")
        assert result['valid'] is True
        assert result['has_letters'] is False
        assert result['has_numbers'] is True

    def test_validate_root_with_mixed(self):
        result = NewAlphanumericCNPJValidator.validate_root_chars("AB12CD34000100")
        assert result['valid'] is True
        assert result['has_letters'] is True
        assert result['has_numbers'] is True

    def test_validate_root_with_invalid_chars(self):
        result = NewAlphanumericCNPJValidator.validate_root_chars("AB@DE!23000100")
        assert result['valid'] is False
        assert '@' in result['invalid_chars'] or '!' in result['invalid_chars']

    def test_validate_order_matriz(self):
        result = NewAlphanumericCNPJValidator.validate_order_digits("ABCDE123000100")
        assert result['valid'] is True
        assert result['order'] == "0001"
        assert result['is_matriz'] is True

    def test_validate_order_filial(self):
        result = NewAlphanumericCNPJValidator.validate_order_digits("ABCDE123000200")
        assert result['valid'] is True
        assert result['order'] == "0002"
        assert result['is_matriz'] is False

    def test_validate_order_with_letters(self):
        result = NewAlphanumericCNPJValidator.validate_order_digits("ABCDE123ABC100")
        assert result['valid'] is False

    def test_char_value_for_numbers(self):
        assert NewAlphanumericCNPJValidator.get_char_value('0') == 0
        assert NewAlphanumericCNPJValidator.get_char_value('5') == 5
        assert NewAlphanumericCNPJValidator.get_char_value('9') == 9

    def test_char_value_for_letters(self):
        assert NewAlphanumericCNPJValidator.get_char_value('A') == 10
        assert NewAlphanumericCNPJValidator.get_char_value('B') == 11
        assert NewAlphanumericCNPJValidator.get_char_value('Z') == 35

    def test_char_value_lowercase(self):
        assert NewAlphanumericCNPJValidator.get_char_value('a') == 10
        assert NewAlphanumericCNPJValidator.get_char_value('z') == 35

    def test_calculate_first_digit(self):
        first = NewAlphanumericCNPJValidator.calculate_first_digit("112223330001")
        assert first == 8

    def test_calculate_second_digit(self):
        second = NewAlphanumericCNPJValidator.calculate_second_digit("1122233300018")
        assert second == 1

    def test_validate_check_digits_traditional_cnpj(self):
        result = NewAlphanumericCNPJValidator.validate_check_digits("11222333000181")
        assert result['valid'] is True
        assert result['expected_dv'] == "81"

    def test_validate_traditional_cnpj(self):
        result = NewAlphanumericCNPJValidator.validate("11.222.333/0001-81")
        assert result['valid'] is True
        assert result['is_alphanumeric'] is False
        assert result['is_matriz'] is True

    def test_validate_empty_string(self):
        result = NewAlphanumericCNPJValidator.validate("")
        assert result['valid'] is False
        assert "vazio" in result['errors'][0].lower()

    def test_validate_none(self):
        result = NewAlphanumericCNPJValidator.validate(None)
        assert result['valid'] is False

    def test_validate_wrong_length(self):
        result = NewAlphanumericCNPJValidator.validate("ABCDE123")
        assert result['valid'] is False
        assert any("14" in e for e in result['errors'])

    def test_validate_all_same_chars(self):
        result = NewAlphanumericCNPJValidator.validate("AAAAAAAAAAAAAA")
        assert result['valid'] is False

    def test_format_cnpj_alphanumeric(self):
        result = NewAlphanumericCNPJValidator.format_cnpj("ABCDE123000145")
        assert result == "AB.CDE.123/0001-45"

    def test_format_cnpj_traditional(self):
        result = NewAlphanumericCNPJValidator.format_cnpj("11222333000181")
        assert result == "11.222.333/0001-81"

    def test_format_cnpj_invalid_length(self):
        result = NewAlphanumericCNPJValidator.format_cnpj("ABCDE")
        assert result == ""

    def test_extract_parts_alphanumeric(self):
        result = NewAlphanumericCNPJValidator.extract_parts("AB.CDE.123/0001-45")
        assert result is not None
        assert result['raiz'] == "ABCDE123"
        assert result['ordem'] == "0001"
        assert result['dv'] == "45"
        assert result['is_matriz'] is True
        assert result['has_letters'] is True

    def test_extract_parts_filial(self):
        result = NewAlphanumericCNPJValidator.extract_parts("ABCDE123000245")
        assert result is not None
        assert result['ordem'] == "0002"
        assert result['is_matriz'] is False

    def test_extract_parts_invalid(self):
        result = NewAlphanumericCNPJValidator.extract_parts("ABC")
        assert result is None

    def test_generate_random_cnpj(self):
        cnpj = NewAlphanumericCNPJValidator.generate_valid_cnpj()
        result = NewAlphanumericCNPJValidator.validate(cnpj)
        assert result['valid'] is True

    def test_generate_cnpj_with_custom_root(self):
        cnpj = NewAlphanumericCNPJValidator.generate_valid_cnpj("TESTECNP")
        result = NewAlphanumericCNPJValidator.validate(cnpj)
        assert result['valid'] is True
        assert result['parts']['raiz'] == "TESTECNP"

    def test_generate_cnpj_with_short_root(self):
        cnpj = NewAlphanumericCNPJValidator.generate_valid_cnpj("ABC")
        result = NewAlphanumericCNPJValidator.validate(cnpj)
        assert result['valid'] is True
        assert result['parts']['raiz'].startswith("ABC")

    def test_generate_multiple_unique_cnpjs(self):
        cnpjs = set()
        for _ in range(10):
            cnpj = NewAlphanumericCNPJValidator.generate_valid_cnpj()
            cnpjs.add(cnpj)
        assert len(cnpjs) >= 5

    def test_validate_format_correct(self):
        result = NewAlphanumericCNPJValidator.validate_format("AB.CDE.123/0001-45")
        assert result['valid'] is True

    def test_validate_format_without_separators(self):
        result = NewAlphanumericCNPJValidator.validate_format("ABCDE123000145")
        assert result['valid'] is False

    def test_validate_format_wrong_separators(self):
        result = NewAlphanumericCNPJValidator.validate_format("AB-CDE-123.0001/45")
        assert result['valid'] is False

    def test_validate_with_lowercase_letters(self):
        cnpj_upper = NewAlphanumericCNPJValidator.generate_valid_cnpj("ABCD1234")
        cnpj_lower = cnpj_upper.lower()
        result = NewAlphanumericCNPJValidator.validate(cnpj_lower)
        assert result['valid'] is True

    def test_cnpj_numeric_compatibilidade(self):
        result = NewAlphanumericCNPJValidator.validate("34.028.316/0001-03")
        assert result['valid'] is True
        assert result['is_alphanumeric'] is False


class TestNewAlphanumericCNPJValidatorIntegration:
    def test_full_workflow_generate_and_validate(self):
        cnpj = NewAlphanumericCNPJValidator.generate_valid_cnpj("RAFAE123")
        validation = NewAlphanumericCNPJValidator.validate(cnpj)
        assert validation['valid'] is True
        cnpj_clean = NewAlphanumericCNPJValidator.remove_formatting(cnpj)
        assert len(cnpj_clean) == 14
        cnpj_formatted = NewAlphanumericCNPJValidator.format_cnpj(cnpj_clean)
        assert cnpj_formatted == cnpj
        parts = NewAlphanumericCNPJValidator.extract_parts(cnpj)
        assert parts['raiz'] == "RAFAE123"
        assert parts['ordem'] == "0001"

    def test_dv_calculation_consistency(self):
        base = "ABCD1234" + "0001"
        dv1 = NewAlphanumericCNPJValidator.calculate_first_digit(base)
        dv2 = NewAlphanumericCNPJValidator.calculate_second_digit(base + str(dv1))
        cnpj = base + str(dv1) + str(dv2)
        result = NewAlphanumericCNPJValidator.validate(cnpj)
        assert result['valid'] is True
        assert result['parts']['dv'] == f"{dv1}{dv2}"
