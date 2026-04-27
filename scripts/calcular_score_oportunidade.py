from __future__ import annotations

import json
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]
CONFIG_PATH = BASE_DIR / "config" / "regua_score_v1.json"


def load_rules() -> dict:
    return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))


def clamp(value: float, min_value: float = 0.0, max_value: float = 10.0) -> float:
    return max(min_value, min(max_value, value))


def calcular_score(
    desconto: float,
    liquidez: float,
    risco: float,
    potencial_estrategico: float,
    facilidade_execucao: float,
) -> float:
    rules = load_rules()
    pesos = rules["pesos"]

    score = (
        clamp(desconto) * pesos["desconto"]
        + clamp(liquidez) * pesos["liquidez"]
        + clamp(risco) * pesos["risco"]
        + clamp(potencial_estrategico) * pesos["potencial_estrategico"]
        + clamp(facilidade_execucao) * pesos["facilidade_execucao"]
    )
    return round(score, 2)


def classificar_decisao(score: float) -> str:
    faixas = load_rules()["faixas_decisao"]

    if score >= faixas["atacar_agora"]["score_minimo"]:
        return "Atacar Agora"
    if score >= faixas["aprofundar_analise"]["score_minimo"]:
        return "Aprofundar Analise"
    if score >= faixas["monitorar"]["score_minimo"]:
        return "Monitorar"
    return "Descartar"


def main() -> None:
    exemplo = {
        "desconto": 8.5,
        "liquidez": 7.5,
        "risco": 6.5,
        "potencial_estrategico": 8.0,
        "facilidade_execucao": 7.0,
    }

    score = calcular_score(**exemplo)
    decisao = classificar_decisao(score)

    print("Regua v1 carregada com sucesso.")
    print(f"Score exemplo: {score}")
    print(f"Decisao exemplo: {decisao}")


if __name__ == "__main__":
    main()
