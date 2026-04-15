import re
from dataclasses import dataclass
from datetime import date
from decimal import Decimal, InvalidOperation
from typing import Any


DATE_PATTERN = r"\d{2}[./]\d{2}[./]\d{4}"
AMOUNT_PATTERN = r"-?\d[\d.]*,\d+"


@dataclass
class ParsedDocument:
    business: dict[str, Any]
    fee_items: list[dict[str, Any]]


def normalize_text(raw_text: str) -> str:
    """Normalize common OCR artifacts before applying field rules."""
    if not raw_text:
        return ""

    replacements = {
        "\u00a0": " ",
        "\u0430": " ",
        "\ufeff": "",
        "№": "No.",
        "Noa": "No",
        "EndereE": "Endereco",
        "MunicM": "Municipio",
        "InscriEc tadual": "Inscricao Estadual",
        "DescriEc": "Descricao",
        "LAIOUNaS": "LAIOUN'S",
    }

    text = raw_text
    for source, target in replacements.items():
        text = text.replace(source, target)

    text = re.sub(r"[ \t\r\n]+", " ", text)
    text = re.sub(r"\s+([:./])", r"\1", text)
    text = re.sub(r"([:/])\s+", r"\1", text)
    return text.strip()


def parse_brazilian_decimal(value: str | None) -> Decimal | None:
    if not value:
        return None

    cleaned = value.strip()
    cleaned = cleaned.replace("R$", "").replace("Ra", "").replace("R ", "")
    cleaned = re.sub(r"[^\d,.-]", "", cleaned)
    if not cleaned:
        return None

    if "," in cleaned:
        cleaned = cleaned.replace(".", "").replace(",", ".")

    try:
        return Decimal(cleaned)
    except InvalidOperation:
        return None


def parse_brazilian_date(value: str | None) -> date | None:
    if not value:
        return None

    normalized = value.strip().replace(".", "/")
    match = re.search(DATE_PATTERN, normalized)
    if not match:
        return None

    day, month, year = match.group(0).replace(".", "/").split("/")
    try:
        return date(int(year), int(month), int(day))
    except ValueError:
        return None


def first_match(text: str, pattern: str, group: int | str = 1) -> Any:
    match = re.search(pattern, text, flags=re.IGNORECASE)
    if not match:
        return None
    return clean_value(match.group(group))


def clean_value(value: Any) -> Any:
    if value is None:
        return None
    if not isinstance(value, str):
        return value
    value = re.sub(r"\s+", " ", value).strip(" .:-")
    return value or None


def extract_between(text: str, start: str, end: str) -> str | None:
    match = re.search(start + r"\s*(.*?)\s*(?=" + end + r")", text, flags=re.IGNORECASE)
    if not match:
        return None
    return clean_value(match.group(1))


def parse_money_pair(text: str, label: str, occurrence: int = 0) -> tuple[str | None, Decimal | None]:
    pattern = label + r"\s*:?\s*([A-Z$]{1,4})?\s*(" + AMOUNT_PATTERN + r")"
    matches = list(re.finditer(pattern, text, flags=re.IGNORECASE))
    if not matches:
        return None, None
    match = matches[occurrence]
    return clean_value(match.group(1)), parse_brazilian_decimal(match.group(2))


def infer_issuer_name(text: str) -> str | None:
    match = re.search(r"^(.*?)(?=\s+(?:AV\.|RUA|ALAMEDA|ROD\.|CEP:|CNPJ/CPF:))", text, flags=re.IGNORECASE)
    return clean_value(match.group(1)) if match else None


def parse_header_fields(text: str) -> dict[str, Any]:
    tax_numbers = re.findall(r"CNPJ/CPF:\s*([\d./-]+)", text, flags=re.IGNORECASE)
    zip_codes = re.findall(r"\bCEP:\s*([\d-]{8,10})", text, flags=re.IGNORECASE)
    freight_currency, freight_amount = parse_money_pair(text, r"FRETE")
    fob_currency, fob_amount = parse_money_pair(text, r"FOB", occurrence=-1)
    cif_currency, cif_amount = parse_money_pair(text, r"CIF", occurrence=-1)

    total_match = re.search(
        r"TOTAL\s*=>\s*(" + AMOUNT_PATTERN + r")\s+(" + AMOUNT_PATTERN + r")",
        text,
        flags=re.IGNORECASE,
    )
    balance_match = re.search(
        r"SALDO\s+(A\s+FAVOR|A\s+PAGAR).*?=>\s*(" + AMOUNT_PATTERN + r")",
        text,
        flags=re.IGNORECASE,
    )

    di_value = extract_between(text, r"DI/DUIMP/DUE:", r"(?:-\s*)?Reg:|Destino:")
    business_type = "IMPORT" if di_value or re.search(r"\bIMPORTACAO\b|\bIMPORT\b", text, flags=re.IGNORECASE) else None

    fields = {
        "issuer_name": infer_issuer_name(text),
        "issuer_tax_no": tax_numbers[0] if len(tax_numbers) >= 1 else None,
        "customer_tax_no": tax_numbers[1] if len(tax_numbers) >= 2 else None,
        "document_no": first_match(text, r"Demonstrativo\s+de\s+Despesas\s+No\.?\s*(\d+)"),
        "customer_name": extract_between(text, r"Cliente:", r"Endereco|Endere\w*|RUA\s+|No\.\s*Processo:"),
        "customer_address": extract_between(text, r"(?:Endereco|Endere\w*)", r"Complem\.?:|Municipio|Munic\w*|Bairro:|UF:|CEP:|CNPJ/CPF:"),
        "customer_city": extract_between(text, r"(?:Municipio|Munic\w*)", r"Bairro:|UF:|CEP:|CNPJ/CPF:"),
        "customer_state": first_match(text, r"\bUF:\s*([A-Z]{2})\b"),
        "customer_zip_code": zip_codes[1] if len(zip_codes) >= 2 else (zip_codes[0] if zip_codes else None),
        "n_ref": first_match(text, r"No\.?\s*Processo:\s*([^\s]+)"),
        "process_no": first_match(text, r"No\.?\s*Processo:\s*([^\s]+)"),
        "business_type": business_type,
        "trade_company": extract_between(text, r"Export/Import:", r"S/Ref\.?:"),
        "s_ref": first_match(text, r"S/Ref\.?:\s*([A-Z0-9./-]+)"),
        "mawb_mbl": extract_between(text, r"MAWB\s*/\s*MBL:", r"Peso\s+Bruto:|DI/DUIMP/DUE:"),
        "di_duimp_due": di_value,
        "registration_date": parse_brazilian_date(first_match(text, r"\bReg:\s*(" + DATE_PATTERN + r")")),
        "arrival_date": parse_brazilian_date(first_match(text, r"Chegada:\s*(" + DATE_PATTERN + r")")),
        "customs_clearance_date": parse_brazilian_date(first_match(text, r"Desembara[cç]o:\s*(" + DATE_PATTERN + r")")),
        "loading_date": parse_brazilian_date(first_match(text, r"Carregamento:\s*(" + DATE_PATTERN + r")")),
        "destination": extract_between(text, r"Destino:", r"No\.?\s*Protocolo:|Avi[aã]o\s*/\s*Navio:|Desembara[cç]o:"),
        "vessel_flight_name": extract_between(text, r"Avi[aã]o\s*/\s*Navio:", r"Desembara[cç]o:|Chegada:"),
        "gross_weight": parse_brazilian_decimal(first_match(text, r"Peso\s+Bruto:\s*(" + AMOUNT_PATTERN + r")")),
        "volume_count": int(first_match(text, r"Volumes:\s*(\d+)") or 0) or None,
        "cargo_desc": extract_between(text, r"Mercadoria:", r"No\.?\s*NFS-e:|FRETE:|FOB:"),
        "nf_no": first_match(text, r"No\.?\s*NFS-e:\s*([A-Z0-9./-]+)"),
        "freight_currency": freight_currency,
        "freight_amount": freight_amount,
        "fob_currency": fob_currency,
        "fob_amount": fob_amount,
        "cif_currency": cif_currency,
        "cif_amount": cif_amount,
        "invoice_no": first_match(text, r"No\.?\s*Invoice:\s*([A-Z0-9./-]+)"),
        "hawb_hbl": extract_between(text, r"HAWB/HBL:", r"Taxa\s+Dolar:|Taxa\s+Euro:|Data\s+CC"),
        "dollar_rate": parse_brazilian_decimal(first_match(text, r"Taxa\s+Dolar:\s*(" + AMOUNT_PATTERN + r")")),
        "euro_rate": parse_brazilian_decimal(first_match(text, r"Taxa\s+Euro:\s*(" + AMOUNT_PATTERN + r")")),
        "cif_brl_amount": parse_brazilian_decimal(first_match(text, r"CIF\s*/\s*FOB:\s*(?:R\$?|BRL)?\s*(" + AMOUNT_PATTERN + r")")),
        "total_credit": parse_brazilian_decimal(total_match.group(1)) if total_match else None,
        "total_debit": parse_brazilian_decimal(total_match.group(2)) if total_match else None,
        "balance_direction": "FAVOR" if balance_match and "FAVOR" in balance_match.group(1).upper() else ("PAYABLE" if balance_match else None),
        "balance_amount": parse_brazilian_decimal(balance_match.group(2)) if balance_match else None,
    }

    if not fields["s_ref"]:
        fields["s_ref"] = fields["invoice_no"] or fields["document_no"]

    return {key: value for key, value in fields.items() if value is not None}


def parse_fee_items(text: str) -> list[dict[str, Any]]:
    total_index = re.search(r"\bTOTAL\s*=>", text, flags=re.IGNORECASE)
    fee_text = (text[: total_index.start()] if total_index else text).strip()

    pattern = re.compile(
        r"(?P<fee_date>\d{2}\.\d{2}\.\d{4})\s+"
        r"(?P<fee_code>\d{3})\s+"
        r"(?P<fee_name>.+?)\s+"
        r"(?P<amount>-?\d[\d.]*,\d{2})"
        r"(?=\s+\d{2}\.\d{2}\.\d{4}\s+\d{3}|\s+\bTOTAL\b|\s*$)",
        flags=re.IGNORECASE,
    )

    items = []
    for line_no, match in enumerate(pattern.finditer(fee_text), start=1):
        fee_name = clean_value(match.group("fee_name"))
        amount = parse_brazilian_decimal(match.group("amount"))
        if not fee_name or amount is None:
            continue

        is_credit = match.group("fee_code") == "200" or "ADIANTAMENTO" in fee_name.upper()
        items.append(
            {
                "fee_date": parse_brazilian_date(match.group("fee_date")),
                "fee_code": match.group("fee_code"),
                "fee_name": fee_name,
                "credit_amount": amount if is_credit else None,
                "debit_amount": None if is_credit else amount,
                "line_no": line_no,
                "raw_text": clean_value(match.group(0)),
            }
        )

    return items


def parse_demonstrativo_text(raw_text: str) -> ParsedDocument:
    text = normalize_text(raw_text)
    business = parse_header_fields(text)
    fee_items = parse_fee_items(text)

    if not business.get("s_ref"):
        raise ValueError("无法从文本中识别 S/Ref、Invoice 或单据号，不能写入 customs_business")

    return ParsedDocument(business=business, fee_items=fee_items)
