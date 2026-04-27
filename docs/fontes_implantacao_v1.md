# Fontes de Implantacao v1

## Leitura do cenario

O agente ja tem um catalogo amplo de fontes. O erro agora seria tentar automatizar tudo ao mesmo tempo.

Isso aumentaria:

- retrabalho tecnico
- manutencao
- fragilidade
- ruido operacional

O melhor caminho e entrar em operacao por ondas.

## Diagnostico estrategico

Nem toda fonte tem o mesmo valor.

As fontes mais fortes para o inicio sao as que combinam:

- volume de oportunidade
- boa chance de desconto
- capacidade de gerar comparativo de mercado
- baixo ou medio esforco tecnico
- relevancia geografica para o radar inicial

## MVP imediato

Essas fontes entram primeiro porque entregam o maior retorno por unidade de esforco.

### Bancos e retomados

- Caixa - Lista Completa por Estado
- Imoveis Caixa
- Seu Imovel BB
- Banrisul - Bens a Venda

### Agregadores e leilao com alto volume

- Leilao Imovel
- Mega Leiloes
- Moraes Leiloes
- Zago Leiloes

### Mercado e preco

- OLX Imoveis
- ZAP Imoveis
- Facebook Marketplace

### Imobiliarias locais mais importantes

- Imobiliaria Guaiba
- Imobsul Imobiliaria
- Almeida e Koch
- Zicuri Imoveis

### Logica do MVP

Com esse bloco, o agente ja consegue:

- captar assimetria forte em bancos e leiloes
- construir referencia de mercado
- captar urgencia e dono direto
- trazer leitura regional real

## Segunda onda

Entram depois do MVP estabilizado.

### Expansao de mercado e benchmark

- Viva Real
- Imovelweb
- Chaves na Mao

### Expansao bancaria

- Itau Imoveis
- Bradesco Leiloes
- Santander Imoveis

### Expansao de leiloeiros e agregadores

- Peterlongo Leiloes
- Joyce Ribeiro Leiloes
- Leiloeiro Bonatto
- Superbid Exchange
- Sold Superbid
- Portal Zuk
- Pro Leilao
- Nucleo Leiloes

### Expansao de imobiliarias locais

- Andre Dorneles Imoveis
- Pestana Imoveis
- Caroline Imoveis
- Gonsioroski Imoveis

## Fontes especiais e mais dificeis

Essas fontes sao importantes, mas nao devem travar o inicio porque costumam exigir mais tratamento, interpretar edital ou gerar mais ruido.

- TJRS - Leiloes
- TRT4 - Leiloeiros Credenciados
- SINDILEI-RS
- Leiloes Judiciais
- Hasta Publica
- Leilao Ninja
- Grupo Lance
- Spy Leiloes
- Receita Federal - SLE
- SPU - Imoveis da Uniao
- SPU - Plataforma de Leilao
- INSS - Leiloes
- SEFAZ-RS - Divida Ativa
- Sicoob Imoveis
- Sicredi Classificados
- Mercado Livre Imoveis
- QuintoAndar
- Fernanda Leiloes
- Muller Leiloes
- Jorge Brasil Leiloes
- Frazao Leiloes
- Turani Leiloes
- Nogari Leiloes
- A Ideal Imoveis
- D'Casa Imoveis Butia

## Recomendacao executiva

O melhor caminho agora e desenvolver o agente em 3 ondas:

1. `MVP imediato`
2. `segunda onda`
3. `fontes especiais`

Isso reduz risco, acelera validacao e aumenta a chance de chegar rapido em relatorios bons de verdade.

## Prioridade real

Se eu fosse dono do projeto, faria primeiro nesta ordem:

1. Caixa - Lista Completa por Estado
2. Imoveis Caixa
3. Seu Imovel BB
4. Banrisul - Bens a Venda
5. Leilao Imovel
6. Mega Leiloes
7. OLX Imoveis
8. ZAP Imoveis
9. Facebook Marketplace
10. Imobiliaria Guaiba

## Regra de implantacao

Uma fonte nova so entra quando:

- a anterior estiver estavel
- o parser estiver limpo
- a deduplicacao estiver funcionando
- o relatorio estiver absorvendo bem a nova carga
