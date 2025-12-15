# CNPJ-Project

> Validação e utilitários para CNPJ (Projeto de exemplo).

## Visão geral

Este projeto fornece validadores e utilitários relacionados a CNPJ (Cadastro Nacional da Pessoa Jurídica). Contém código fonte em `validator/src/cnpj_validator` e testes em `tests/`.

## Pré-requisitos

- Python 3.8+
- `pip` ou ambiente que suporte instalar o projeto em modo editable

## Instalação (modo dev)

Abra um terminal na raiz do repositório `CNPJ-Project` e execute:

```bash
python -m pip install -e .
pip install -r requirements.txt  # se existir
```

Ou usando `poetry` (se aplicável):

```bash
poetry install
```

## Executar testes

Execute os testes com `pytest`:

```bash
pytest -q
```

## Estrutura do projeto

- `validator/src/cnpj_validator/` — pacote principal com validadores.
- `tests/` — suítes de testes unitários e de integração.
- `pyproject.toml`, `setup.cfg` — metadados do projeto e configuração de build/test.

## Exemplo de uso

Após instalar o pacote (veja seção Instalação), importe o validador no seu código Python:

```python
from cnpj_validator import some_validator_function

resultado = some_validator_function("12.345.678/0001-95")
print(resultado)
```

Substitua `some_validator_function` pela função exposta pelo pacote (ver `validator/src/cnpj_validator`).

## Contribuindo

1. Fork do repositório
2. Crie uma branch com sua feature/bugfix
3. Abra um Pull Request descrevendo as mudanças e testes

## Licença

Consulte o arquivo `LICENSE` na raiz do workspace para detalhes sobre a licença.

## Testar CNPJs Alfanuméricos (2026)

Incluí um script simples para validar ou gerar CNPJs alfanuméricos no diretório `scripts`.

- Validar um CNPJ:

```bash
python scripts/test_cnpj_alphanumeric.py "AB.CDE.123/0001-45"
```

- Gerar um CNPJ válido (raiz aleatória):

```bash
python scripts/test_cnpj_alphanumeric.py --generate
```

- Gerar um CNPJ válido com raiz fornecida (8 caracteres):

```bash
python scripts/test_cnpj_alphanumeric.py --generate TESTECNP
```

O script usa `NewAlphanumericCNPJValidator` localizado em `validator/src/cnpj_validator/validators`.
