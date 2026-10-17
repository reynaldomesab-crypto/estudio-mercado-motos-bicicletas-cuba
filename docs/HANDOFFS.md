# Handoffs del proyecto

Registro de los **handoffs** usados para mantener el trabajo entre sesiones, y del
procedimiento para crear nuevos.

---

## Qué es un handoff aquí

Un handoff es el resumen del estado del trabajo que permite retomar una tarea sin
releer la conversación entera. En este proyecto solo consta **uno**, que llegó al
comienzo de la sesión de análisis. Los apartados siguientes describen ese handoff
real y, después, el procedimiento para registrar los futuros.

Si en una sesión posterior aparecen más apartados, deben recogerse desde el
resumen que se recibe, no reconstruirse de memoria.

---

## Handoff registrado

### Apertura del proyecto (único handoff documentado)

**Origen:** el resumen de contexto entregado por el sistema al agotarse el
contexto de la sesión anterior a esta.
**Recibido:** al comienzo del trabajo de análisis, antes de generar la primera
figura.

**Qué traía:**

- La estructura del repositorio y la función de cada carpeta.
- Los datasets disponibles y sus campos.
- El problema recurrente de los análisis sueltos: funciones duplicadas,
  literales `EOF` pegados al final de los archivos y errores de ámbito al pasar
  heredocs a `bash`.
- Los gráficos que ya se habían hecho y cuáles quedaban por revisar.
- Qué preguntas del usuario seguían sin responder y por qué.

**Qué se hizo con él:**

Se decidió no seguir con scripts temporales y crear en su lugar un único
generador, `scripts/analyzers/generate_report.py`, que hoy produce todas las
figuras y reportes. Además se accompagnés la advertencia sobre no aceptar
cifras de conteo sin verificarlas contra el dataset, que fue la decisión que
desbloqueó el hallazgo de los duplicados.

**Vigencia:** parcial. La parte estructural sigue siendo válida; la de "datos
pendientes" quedó superada.

---

## Lo que este documento todavía no cubre

- Los cortes entre revisiones de gráficos de esta misma sesión **no** son
  handoffs: fue trabajo continuo dentro de una sola sesión, sin corte de
  contexto.
- Si en el futuro una sesión empieza con un resumen de este tipo, debe añadirse
aquí como apartado nuevo.

---

## Procedimiento para crear un handoff

Se documenta para que el procedimiento no viva solo en la conversación.

### Cuándo

- La sesión está por agotar su contexto.
- El trabajo queda a medias en un punto que no conviene abandonar sin resumen.
- Otra persona o agente necesita retomar.

### Qué debe contener

1. **Estado**: qué está hecho y verificado, con cifras exactas.
2. **Decisiones pendientes**: qué se debatió y por qué no se decidió.
3. **Trampas conocidas**: lo que salió mal y costó tiempo, para no repetirlo.
4. **Rutas exactas**: rutas absolutas, incluido el intérprete correcto.
5. **Cómo verificar**: los comandos que regeneran y auditan el trabajo.

### Cómo registrarlo

Añadir un apartado con el mismo formato del existente: origen, qué traía, qué se
hizo con él y vigencia. Si el handoff no se recibió realmente, no se documenta:
es preferible un apartado vacío a uno inventado.

### Cómo verificar el trabajo tras un handoff

```bash
# Regenera figuras, reportes y la clasificacion registro a registro
<intérprete del venv> \
    scripts/analyzers/generate_report.py

# Audita la clasificacion de vehiculos
<intérprete del venv> \
    scripts/analyzers/auditar_clasificaciones.py --json
```

---

## Nota sobre el intérprete

`/usr/bin/python3` **no tiene matplotlib** en esta máquina. Todo el análisis se
ejecuta con:

```
<intérprete del venv>
```

Si al reproducir un análisis falla con `ModuleNotFoundError: matplotlib`, el
problema es el intérprete y no el código.

---

## Documentos relacionados

| Documento | Contenido |
| --- | --- |
| `JOURNEY.md` | Bitácora del proyecto por fechas: hallazgos y decisiones |
| `README.md` | Descripción, instalación y uso |
| `analysis/auditoria_clasificaciones.json` | Salida de la auditoría, generada |
| `analysis/resultados.json` | Todas las cifras del análisis |
| `docs/PROMPTS_DEL_USUARIO.md` | Registro de prompts del usuario |