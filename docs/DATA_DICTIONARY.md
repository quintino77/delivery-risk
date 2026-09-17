# Dicionário de atributos

| Coluna | Significado | Unidade |
|---|---|---|
| price | Soma dos preços dos itens, sem frete | R$ históricos |
| freight_value | Soma do frete dos itens | R$ históricos |
| item_count | Número de linhas de item | inteiro >= 1 |
| seller_count | Vendedores distintos no pedido | inteiro >= 1 |
| weight_g | Soma dos pesos cadastrados dos itens | gramas |
| volume_cm3 | Soma de comprimento × altura × largura por item | cm³ |
| promised_days | Data prometida menos data da compra | dias corridos |
| purchase_weekday | Dia da semana da compra | segunda=0, domingo=6 |
| purchase_hour | Hora da compra | 0–23 |
| interstate | Pelo menos um vendedor fora do estado do cliente | 0/1 |
| customer_state | UF do cliente | texto |
| seller_state | UF do vendedor do item mais caro | texto |
| category | Categoria do item mais caro | texto original em português |

Apenas essas 13 colunas entram no modelo. Mediana do treino preenche valores
numéricos ausentes na base histórica; a interface exige entradas completas.
Categorias ausentes tornam-se `desconhecida`.

Colunas extras do dashboard: `order_purchase_timestamp` (data da compra), `late`
(alvo 0/1), `delay_days` (dias em relação à promessa, negativo quando antecipado),
`delivery_days` (duração efetiva em dias fracionários). Não enviar essas colunas
como preditores. Em arquivos de lote, colunas extras são ignoradas.
