# Reporte: kilometros por dolar en vehiculos electricos

Generado por `scripts/analyzers/generate_report.py`.

## Conclusion

**No se publica esta cifra.** Los datos no alcanzan el 10% minimo que
se fijó para no dar por valido un calculo construido sobre una muestra
minima.

| Dato disponible | Anuncios | % de los eléctricos |
| --- | ---: | ---: |
| Potencia en vatios | 191 | 6.4% |
| Autonomia en km | 145 | 4.8% |
| Precio | 2892 | 96.2% |
| **Los tres a la vez** | **51** | **1.7%** |

Solo 51 de 3006 anuncios eléctricos
declaran a la vez potencia, autonomia y precio, que es el minimo para
poder dividir distancia entre precio. Con esa proporcion, cualquier
mediana de kilometros por dolar seria ruido: un unico anuncio caro o mal
escrito cambiaria el resultado.

Ademas, la autonomia solo aparece cuando el vendedor la escribe en el
titulo, y no como campo estructurado. Los que no la ponen no son
vehiculos sin autonomia, sino anuncios que no la declaran, asi que
cualquier promedio calculable estaria sesgado hacia los vendedores que
mejor describen su producto.

Que hace falta para que este reporte sea posible: que las plataformas
expongan autonomia y potencia como campos, o ampliar el scraping a las
fichas completas de producto en lugar de solo al titulo.
