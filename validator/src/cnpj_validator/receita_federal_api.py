"""
Cliente da API da Receita Federal (simplificado)
"""

from dataclasses import dataclass, field
from typing import Optional
import time
import logging
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError
import json
import ssl

logger = logging.getLogger(__name__)


@dataclass
class CNPJData:
    cnpj: str = ""
    razao_social: str = ""
    nome_fantasia: str = ""
    situacao_cadastral: str = ""
    data_situacao_cadastral: str = ""
    motivo_situacao_cadastral: str = ""
    data_abertura: str = ""
    porte: str = ""
    natureza_juridica: str = ""
    cnae_principal: dict = field(default_factory=dict)
    cnaes_secundarios: list = field(default_factory=list)
    endereco: dict = field(default_factory=dict)
    telefone: str = ""
    email: str = ""
    capital_social: float = 0.0
    quadro_societario: list = field(default_factory=list)
    simples_nacional: dict = field(default_factory=dict)
    mei: bool = False
    raw_data: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "cnpj": self.cnpj,
            "razao_social": self.razao_social,
        }


class ReceitaFederalAPIError(Exception):
    def __init__(self, message: str, status_code: Optional[int] = None, response: Optional[str] = None):
        super().__init__(message)
        self.status_code = status_code
        self.response = response


class ReceitaFederalAPI:
    APIS = {
        "brasilapi": "https://brasilapi.com.br/api/cnpj/v1/{cnpj}",
        "receitaws": "https://www.receitaws.com.br/v1/cnpj/{cnpj}",
    }

    def __init__(self, api_preferida: str = "brasilapi", timeout: int = 30, max_retries: int = 3, retry_delay: float = 1.0):
        self.api_preferida = api_preferida
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self._last_request_time: float = 0.0
        self._min_interval: float = 20.0

    def _limpar_cnpj(self, cnpj: str) -> str:
        return "".join(c for c in cnpj if c.isalnum()).upper()

    def _limpar_cnpj_numerico(self, cnpj: str) -> str:
        return "".join(c for c in cnpj if c.isdigit())

    def _is_alphanumeric_cnpj(self, cnpj: str) -> bool:
        cnpj_limpo = self._limpar_cnpj(cnpj)
        return any(c.isalpha() for c in cnpj_limpo[:8])

    def _validar_cnpj_basico(self, cnpj: str) -> bool:
        cnpj_limpo = self._limpar_cnpj(cnpj)
        if len(cnpj_limpo) != 14:
            return False
        if len(set(cnpj_limpo)) == 1:
            return False
        raiz = cnpj_limpo[:8]
        ordem = cnpj_limpo[8:12]
        dv = cnpj_limpo[12:14]
        if not all(c.isalnum() for c in raiz):
            return False
        if not ordem.isdigit() or not dv.isdigit():
            return False
        return True

    def _respeitar_rate_limit(self):
        elapsed = time.time() - self._last_request_time
        if elapsed < self._min_interval:
            wait_time = self._min_interval - elapsed
            logger.debug(f"Rate limit: aguardando {wait_time:.1f}s")
            time.sleep(wait_time)
        self._last_request_time = time.time()

    def consultar(self, cnpj: str, usar_fallback: bool = True) -> CNPJData:
        cnpj_limpo = self._limpar_cnpj(cnpj)
        if not self._validar_cnpj_basico(cnpj_limpo):
            raise ValueError(f"CNPJ inválido: {cnpj}")

        is_alphanumeric = self._is_alphanumeric_cnpj(cnpj_limpo)
        if is_alphanumeric:
            raise ReceitaFederalAPIError("CNPJs alfanuméricos ainda não são suportados pelas APIs externas.", status_code=501)

        cnpj_numerico = self._limpar_cnpj_numerico(cnpj)
        apis_para_tentar = [self.api_preferida]
        if usar_fallback:
            apis_para_tentar.extend(api for api in self.APIS.keys() if api != self.api_preferida)

        last_error = None
        for api_name in apis_para_tentar:
            if api_name not in self.APIS:
                continue
            url = self.APIS[api_name].format(cnpj=cnpj_numerico)
            for attempt in range(self.max_retries):
                try:
                    self._respeitar_rate_limit()
                    data = self._fazer_requisicao(url)
                    if api_name == 'brasilapi':
                        return self._parse_brasilapi(data)
                    else:
                        return self._parse_brasilapi(data)
                except Exception as e:
                    last_error = e
        if last_error:
            raise last_error
        raise ReceitaFederalAPIError("Não foi possível consultar o CNPJ em nenhuma API")

    def _fazer_requisicao(self, url: str) -> dict:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        headers = {"User-Agent": "CNPJ-Validator/1.0 (Python)", "Accept": "application/json"}
        request = Request(url, headers=headers)
        try:
            with urlopen(request, timeout=self.timeout, context=ctx) as response:
                data = response.read().decode("utf-8")
                return json.loads(data)
        except HTTPError as e:
            error_body = ""
            try:
                error_body = e.read().decode("utf-8")
            except Exception:
                pass
            if e.code == 404:
                raise ReceitaFederalAPIError("CNPJ não encontrado na base da Receita Federal", status_code=404, response=error_body)
            raise ReceitaFederalAPIError(f"Erro HTTP {e.code}: {e.reason}", status_code=e.code, response=error_body)
        except URLError as e:
            raise ReceitaFederalAPIError(f"Erro de conexão: {e.reason}")
        except json.JSONDecodeError as e:
            raise ReceitaFederalAPIError(f"Erro ao decodificar resposta JSON: {e}")

    def _parse_brasilapi(self, data: dict) -> CNPJData:
        socios = []
        for socio in data.get('qsa', []) or []:
            if isinstance(socio, dict):
                socios.append({'nome': socio.get('nome_socio', ''), 'qualificacao': socio.get('qualificacao_socio', ''), 'data_entrada': socio.get('data_entrada_sociedade', '')})
        return CNPJData(cnpj=data.get('cnpj', ''), razao_social=data.get('razao_social', ''), nome_fantasia=data.get('nome_fantasia', '') or '', situacao_cadastral=data.get('descricao_situacao_cadastral', ''), data_situacao_cadastral=data.get('data_situacao_cadastral', ''), motivo_situacao_cadastral=str(data.get('motivo_situacao_cadastral', '')), data_abertura=data.get('data_inicio_atividade', ''), porte=data.get('porte', ''), natureza_juridica=data.get('natureza_juridica', ''), cnae_principal={'codigo': data.get('cnae_fiscal', ''), 'descricao': data.get('cnae_fiscal_descricao', '')}, cnaes_secundarios=[], endereco={'logradouro': data.get('logradouro', ''), 'numero': data.get('numero', ''), 'complemento': data.get('complemento', ''), 'bairro': data.get('bairro', ''), 'municipio': data.get('municipio', ''), 'uf': data.get('uf', ''), 'cep': data.get('cep', '')}, telefone=data.get('ddd_telefone_1', ''), email=data.get('email', '') or '', capital_social=float(data.get('capital_social', 0) or 0), quadro_societario=socios, simples_nacional={'optante': data.get('opcao_pelo_simples', False)}, mei=data.get('opcao_pelo_mei', False) if data.get('opcao_pelo_mei') else False, raw_data=data)
