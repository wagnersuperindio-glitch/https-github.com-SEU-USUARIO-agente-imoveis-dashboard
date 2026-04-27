from __future__ import annotations

from html import unescape
import re
from urllib.parse import quote

from agente_imoveis.connectors.anti_bot import BrowserBackedConnector
from agente_imoveis.connectors.base import BaseConnector
from agente_imoveis.models import SourceDefinition, SourceRecord
from agente_imoveis.processing.geography import load_radar_cities
from agente_imoveis.utils.normalization import detect_city_state, normalize_text, parse_brl_number, slugify


def extract_links(html: str) -> list[tuple[str, str]]:
    pattern = re.compile(r"<a[^>]+href=[\"']([^\"']+)[\"'][^>]*>(.*?)</a>", re.IGNORECASE | re.DOTALL)
    clean_tags = re.compile(r"<[^>]+>")
    links: list[tuple[str, str]] = []
    for href, raw_text in pattern.findall(html):
        text = normalize_text(clean_tags.sub(" ", raw_text))
        if text:
            links.append((href, text))
    return links


def absolute_url(base_url: str, href: str) -> str:
    if href.startswith("http"):
        return href
    return f"{base_url.rstrip('/')}/{href.lstrip('/')}"


def extract_area_m2(text: str) -> float | None:
    match = re.search(r"(\d[\d\.,]*)\s*m(?:²|2)", text, re.IGNORECASE)
    if not match:
        return None
    return parse_brl_number(match.group(1))


def extract_city_state_from_title(text: str) -> tuple[str, str]:
    match = re.search(r"-\s*([A-Za-zÀ-ÿ' ]+)\s*-\s*([A-Z]{2})$", text)
    if match:
        return normalize_text(match.group(1)), normalize_text(match.group(2))
    return "", ""


def extract_facebook_marketplace_records(html: str, source: SourceDefinition) -> list[SourceRecord]:
    pattern = re.compile(
        r'"MarketplaceFeedGeneralListingObject".*?'
        r'"product_item_id":"(?P<item_id>[^"]+)".*?'
        r'"title":"(?P<title>.*?)","price":\{"currency":"(?P<currency>[^"]+)","amount_with_offset":"(?P<price>\d+)"\}.*?'
        r'"reverse_geocode":\{"city":"(?P<city>[^"]+)","state":"(?P<state>[^"]+)"',
        re.IGNORECASE | re.DOTALL,
    )
    records: list[SourceRecord] = []
    seen_item_ids: set[str] = set()
    for match in pattern.finditer(html):
        item_id = match.group("item_id")
        if item_id in seen_item_ids:
            continue
        seen_item_ids.add(item_id)
        records.append(
            SourceRecord(
                source_name=source.nome,
                category=source.categoria,
                city=normalize_text(unescape(match.group("city"))),
                state=normalize_text(unescape(match.group("state"))),
                asset_type="marketplace",
                title=normalize_text(unescape(match.group("title")))[:180],
                price=parse_brl_number(match.group("price")),
                link=f"https://www.facebook.com/marketplace/item/{item_id}",
                raw_payload={
                    "currency": normalize_text(match.group("currency")),
                    "listing_id": item_id,
                    "capture_mode": "browser_marketplace_feed",
                },
            )
        )
        if len(records) >= 30:
            break
    return records


def load_radar_city_names() -> list[str]:
    return [item["cidade"] for item in load_radar_cities().values()]


def olx_search_url_for_city(city: str) -> str:
    normalized_city = normalize_text(city)
    return f"https://www.olx.com.br/imoveis/venda/estado-rs?q={quote(normalized_city)}"


def zap_search_url_for_city(city: str) -> str:
    city_slug = slugify(city)
    if city_slug == "xangrila":
        city_slug = "xangri-la"
    encoded = quote(f"rs+{city_slug}", safe="")
    return f"https://www.zapimoveis.com.br/venda/imoveis/{encoded}/"


def extract_olx_records(html: str, source: SourceDefinition, requested_city: str) -> list[SourceRecord]:
    section_pattern = re.compile(r'<section class="olx-adcard.*?</section>', re.IGNORECASE | re.DOTALL)
    link_pattern = re.compile(
        r'data-testid="adcard-link"[^>]*title="(?P<title>[^"]+)" href="(?P<href>[^"]+)"',
        re.IGNORECASE | re.DOTALL,
    )
    price_pattern = re.compile(r'olx-adcard__price[^>]*>(?P<price>.*?)</h3>', re.IGNORECASE | re.DOTALL)
    location_pattern = re.compile(r'olx-adcard__location[^>]*>.*?</svg>\s*(?P<location>.*?)</p>', re.IGNORECASE | re.DOTALL)
    detail_pattern = re.compile(r'olx-adcard__detail"[^>]*aria-label="(?P<detail>[^"]+)"', re.IGNORECASE)
    clean_tags = re.compile(r"<[^>]+>")
    records: list[SourceRecord] = []
    normalized_target = normalize_text(requested_city).lower()
    for block in section_pattern.findall(html):
        link_match = link_pattern.search(block)
        price_match = price_pattern.search(block)
        if not link_match or not price_match:
            continue
        href = absolute_url(source.url, unescape(link_match.group("href")))
        title = normalize_text(unescape(link_match.group("title")))
        location_match = location_pattern.search(block)
        location = normalize_text(unescape(clean_tags.sub(" ", location_match.group("location")))) if location_match else ""
        city = normalize_text(location.split(",", 1)[0]) if location else requested_city
        if city and normalize_text(city).lower() != normalized_target:
            continue
        raw_price = clean_tags.sub(" ", price_match.group("price"))
        details = [normalize_text(detail) for detail in detail_pattern.findall(block)]
        area_m2 = None
        for detail in details:
            area_match = re.search(r"(\d[\d\.,]*)\s+metros?\s+quadrados", detail, re.IGNORECASE)
            if area_match:
                area_m2 = parse_brl_number(area_match.group(1))
                break
        records.append(
            SourceRecord(
                source_name=source.nome,
                category=source.categoria,
                city=city,
                state="RS",
                asset_type="portal_mercado",
                title=title[:180],
                address=location[:180],
                price=parse_brl_number(raw_price),
                area_m2=area_m2,
                link=href,
                raw_payload={
                    "requested_city": requested_city,
                    "details": details,
                    "capture_mode": "browser_stealth_property",
                },
            )
        )
        if len(records) >= 12:
            break
    return records


def extract_zap_records(html: str, source: SourceDefinition, requested_city: str) -> list[SourceRecord]:
    link_pattern = re.compile(
        r'<a[^>]+href="(?P<href>https://www\.zapimoveis\.com\.br/imovel/[^"]+)"[^>]*>(?P<text>.*?)</a>',
        re.IGNORECASE | re.DOTALL,
    )
    clean_tags = re.compile(r"<[^>]+>")
    records: list[SourceRecord] = []
    normalized_target = normalize_text(requested_city).lower()
    seen_links: set[str] = set()
    for match in link_pattern.finditer(html):
        href = unescape(match.group("href"))
        if href in seen_links:
            continue
        text = normalize_text(unescape(clean_tags.sub(" ", match.group("text"))))
        if "para comprar com" not in text.lower():
            continue
        city_match = re.search(r"([A-Za-zÀ-ÿ' -]+),\s*([A-Za-zÀ-ÿ' -]+)\s+Rua", text)
        city = normalize_text(city_match.group(2)) if city_match else requested_city
        address = normalize_text(city_match.group(0).rsplit("Rua", 1)[0].strip()) if city_match else ""
        if city and normalize_text(city).lower() != normalized_target:
            continue
        seen_links.add(href)
        price_match = re.search(r"R\$\s*([\d\.\,]+)", text)
        slug = href.split("/imovel/", 1)[-1].split("/?", 1)[0]
        slug = re.sub(r"-id-\d+$", "", slug)
        title = normalize_text(slug.replace("-", " "))
        records.append(
            SourceRecord(
                source_name=source.nome,
                category=source.categoria,
                city=city,
                state="RS",
                asset_type="portal_mercado",
                title=title[:180],
                address=address[:180],
                price=parse_brl_number(price_match.group(1)) if price_match else None,
                area_m2=extract_area_m2(text),
                link=href,
                raw_payload={
                    "requested_city": requested_city,
                    "capture_mode": "browser_stealth_property",
                    "text_excerpt": text[:500],
                },
            )
        )
        if len(records) >= 12:
            break
    return records


class CaixaListaConnector(BaseConnector):
    connector_name = "caixa_lista_estado"

    def collect(self):
        html = self.fetch_page()
        return [
            SourceRecord(
                source_name=self.source.nome,
                category=self.source.categoria,
                city="",
                state="RS",
                asset_type="lista_estado",
                title="Lista completa Caixa por estado",
                link=self.source.url,
                raw_payload={"html_excerpt": html[:2000]},
            )
        ]


class CaixaImoveisConnector(BaseConnector):
    connector_name = "caixa_imoveis"

    def collect(self):
        html = self.fetch_page()
        modalidades = []
        for _, text in extract_links(html):
            if "Venda" in text or "Leilao" in normalize_text(text):
                modalidades.append(text)
        return [
            SourceRecord(
                source_name=self.source.nome,
                category=self.source.categoria,
                city="",
                state="RS",
                asset_type="busca_caixa",
                title="Portal de busca Caixa",
                link=self.source.url,
                raw_payload={
                    "modalidades_detectadas": modalidades[:20],
                    "html_excerpt": html[:2000],
                },
            )
        ]


class BancoBrasilConnector(BaseConnector):
    connector_name = "seu_imovel_bb"

    def collect(self):
        html = self.fetch_page()
        records: list[SourceRecord] = []
        card_pattern = re.compile(
            r'<div class="card carta">.*?'
            r'<a href="(?P<href>/imovel/id/\d+)">.*?'
            r'<div class="tipo">.*?</i>\s*(?P<asset_type>[^<]+)</div>.*?'
            r'<div class="valor">R\$\s*(?P<price>[\d\.,]+)</div>.*?'
            r"onClick=\"_compartilhar\('(?P<share>.*?)',\s*'(?P<share_link>http[^']+)'\);\".*?"
            r'<div class="localidade">.*?</i>\s*(?P<location>[^<]+)</div>.*?'
            r'<div class="leilao pt-2 "><i.*?</i>\s*(?P<event_stage>[^<]+)</div>.*?'
            r'<div class="leilao pt-3 "><i.*?</i>\s*(?P<event_date>[^<]+)</div>',
            re.IGNORECASE | re.DOTALL,
        )

        for match in card_pattern.finditer(html):
            location = normalize_text(unescape(match.group("location")))
            city, state = detect_city_state(location)
            share_text = normalize_text(unescape(match.group("share")))
            title_head = share_text.split("Descricao legal:", 1)[0].strip() or f"{match.group('asset_type')} - {location}"
            records.append(
                SourceRecord(
                    source_name=self.source.nome,
                    category=self.source.categoria,
                    city=city,
                    state=state,
                    asset_type=normalize_text(unescape(match.group("asset_type"))),
                    title=title_head[:180],
                    price=parse_brl_number(match.group("price")),
                    event_date=normalize_text(unescape(match.group("event_date"))),
                    event_stage=normalize_text(unescape(match.group("event_stage"))),
                    link=absolute_url(self.source.url, match.group("href")),
                    raw_payload={
                        "location": location,
                        "share_text": share_text,
                        "share_link": match.group("share_link"),
                    },
                )
            )

        if not records:
            records.append(
                SourceRecord(
                    source_name=self.source.nome,
                    category=self.source.categoria,
                    city="",
                    state="",
                    asset_type="imovel_bb",
                    title="Portal BB acessado sem itens parseados",
                    link=self.source.url,
                    raw_payload={"html_excerpt": html[:2000]},
                )
            )
        return records


class BanrisulConnector(BaseConnector):
    connector_name = "banrisul_bens_venda"

    def collect(self):
        html = self.fetch_page()
        return [
            SourceRecord(
                source_name=self.source.nome,
                category=self.source.categoria,
                city="",
                state="RS",
                asset_type="bens_banrisul",
                title="Banrisul bens a venda",
                link=self.source.url,
                raw_payload={"html_excerpt": html[:2000]},
            )
        ]


class LeilaoImovelConnector(BrowserBackedConnector):
    connector_name = "leilao_imovel"

    def collect(self):
        try:
            html = self.fetch_page_with_browser()
        except Exception:
            html = self.fetch_page()
        records: list[SourceRecord] = []
        for href, text in extract_links(html)[:200]:
            if "imovel" not in href.lower() and "leil" not in href.lower():
                continue
            records.append(
                SourceRecord(
                    source_name=self.source.nome,
                    category=self.source.categoria,
                    city="",
                    state="",
                    asset_type="leilao_imovel",
                    title=text[:180],
                    price=parse_brl_number(text),
                    link=absolute_url(self.source.url, href),
                    raw_payload={"anchor_text": text},
                )
            )
        if not records:
            records.append(
                SourceRecord(
                    source_name=self.source.nome,
                    category=self.source.categoria,
                    city="",
                    state="",
                    asset_type="leilao_imovel",
                    title="Portal Leilao Imovel acessado sem itens parseados",
                    link=self.source.url,
                    raw_payload={"html_excerpt": html[:2000]},
                )
            )
        return records


class MegaLeiloesConnector(BaseConnector):
    connector_name = "mega_leiloes"

    def collect(self):
        html = self.fetch_page()
        records: list[SourceRecord] = []
        title_pattern = re.compile(
            r'<a class="card-title" href="(?P<href>https?://[^"]+)"[^>]*>(?P<title>.*?)</a>',
            re.IGNORECASE | re.DOTALL,
        )
        for match in title_pattern.finditer(html):
            href = unescape(match.group("href"))
            text = normalize_text(unescape(match.group("title")))
            if not text:
                continue
            if "/imoveis/" not in href.lower() and "/ml" not in href.lower():
                continue
            city, state = extract_city_state_from_title(text)
            records.append(
                SourceRecord(
                    source_name=self.source.nome,
                    category=self.source.categoria,
                    city=city,
                    state=state,
                    asset_type="mega_leiloes",
                    title=text[:180],
                    price=parse_brl_number(text) if "R$" in text else None,
                    area_m2=extract_area_m2(text),
                    link=href,
                    raw_payload={"card_title": text},
                )
            )
        if not records:
            records.append(
                SourceRecord(
                    source_name=self.source.nome,
                    category=self.source.categoria,
                    city="",
                    state="",
                    asset_type="mega_leiloes",
                    title="Portal Mega Leiloes acessado sem itens parseados",
                    link=self.source.url,
                    raw_payload={"html_excerpt": html[:2000]},
                )
            )
        return records


class OLXConnector(BrowserBackedConnector):
    connector_name = "olx_imoveis"

    def collect(self):
        records: list[SourceRecord] = []
        for city in load_radar_city_names():
            target_url = olx_search_url_for_city(city)
            try:
                html = self.fetch_page_with_browser(target_url, strategy="stealth_property")
            except Exception:
                continue
            records.extend(extract_olx_records(html, self.source, requested_city=city))
        if records:
            return records
        try:
            html = self.fetch_page_with_browser(strategy="stealth_property")
        except Exception:
            html = self.fetch_page()
        return [
            SourceRecord(
                source_name=self.source.nome,
                category=self.source.categoria,
                city="",
                state="RS",
                asset_type="portal_mercado",
                title="OLX Imoveis - radar de mercado",
                link=self.source.url,
                raw_payload={"html_excerpt": html[:2000]},
            )
        ]


class ZapConnector(BrowserBackedConnector):
    connector_name = "zap_imoveis"

    def collect(self):
        records: list[SourceRecord] = []
        for city in load_radar_city_names():
            target_url = zap_search_url_for_city(city)
            try:
                html = self.fetch_page_with_browser(target_url, strategy="stealth_property")
            except Exception:
                continue
            records.extend(extract_zap_records(html, self.source, requested_city=city))
        if records:
            return records
        try:
            html = self.fetch_page_with_browser(strategy="stealth_property")
        except Exception:
            html = self.fetch_page()
        return [
            SourceRecord(
                source_name=self.source.nome,
                category=self.source.categoria,
                city="",
                state="RS",
                asset_type="portal_mercado",
                title="ZAP Imoveis - benchmark e CMA",
                link=self.source.url,
                raw_payload={"html_excerpt": html[:2000]},
            )
        ]


class FacebookMarketplaceConnector(BrowserBackedConnector):
    connector_name = "facebook_marketplace"

    def collect(self):
        try:
            html = self.fetch_page_with_browser()
        except Exception:
            html = self.fetch_page()
        records = extract_facebook_marketplace_records(html, self.source)
        if records:
            return records
        return [
            SourceRecord(
                source_name=self.source.nome,
                category=self.source.categoria,
                city="",
                state="",
                asset_type="marketplace",
                title="Facebook Marketplace - radar de urgencia",
                link=self.source.url,
                raw_payload={"html_excerpt": html[:2000]},
            )
        ]


class GenericConnector(BaseConnector):
    connector_name = "generic"

    def collect(self):
        html = self.fetch_page()
        return [
            SourceRecord(
                source_name=self.source.nome,
                category=self.source.categoria,
                city="",
                state="",
                asset_type="generic",
                title=f"{self.source.nome} - coleta generica",
                link=self.source.url,
                raw_payload={"html_excerpt": html[:2000]},
            )
        ]


CONNECTOR_REGISTRY: dict[str, type[BaseConnector]] = {
    "Caixa - Lista Completa por Estado": CaixaListaConnector,
    "Imoveis Caixa": CaixaImoveisConnector,
    "Seu Imovel BB": BancoBrasilConnector,
    "Banrisul - Bens a Venda": BanrisulConnector,
    "Leilao Imovel": LeilaoImovelConnector,
    "Mega Leiloes": MegaLeiloesConnector,
    "OLX Imoveis": OLXConnector,
    "ZAP Imoveis": ZapConnector,
    "Facebook Marketplace": FacebookMarketplaceConnector,
}


def build_connector(source: SourceDefinition) -> BaseConnector:
    connector_class = CONNECTOR_REGISTRY.get(source.nome, GenericConnector)
    return connector_class(source)
