from __future__ import annotations

from agente_imoveis.connectors.definitions import filter_sources_by_names, load_implementation_plan
from agente_imoveis.connectors.mvp_connectors import build_connector


def build_mvp_connectors():
    plan = load_implementation_plan()
    sources = filter_sources_by_names(plan["mvp_imediato"])
    return [build_connector(source) for source in sources]
