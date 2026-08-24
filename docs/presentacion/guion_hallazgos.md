# Los cuatro hallazgos, para contarlos en voz alta

> Generado por `docs/presentacion/generar_ppt.py` junto con la lámina de la
> auditoría: las cifras salen de los mismos artefactos que la presentación,
> no se escriben aquí a mano. La versión canónica de cada hallazgo vive en
> `app/streamlit_app.py` (lista `AUDITORIA`) y en `INFORME_AUDITORIA.md`.

Un párrafo por hallazgo. Cada uno se puede contar en unos treinta segundos
y responde a lo mismo: qué se leía mal, cómo se notó, en qué quedó.

## 1. El código de faltante, leído como un sueldo

*Nació en los datos de origen.* El INEI codifica «no sabe» como el valor
999999. Ese número entraba al modelo como si fuera un ingreso real de
999.999 soles al mes, y arrastraba consigo toda la regresión: con esos casos
dentro, vivir en zona urbana aparecía asociado a **once soles** más de
ingreso, una cifra sin ningún sentido económico. Al tratar el centinela como
dato faltante, el R² pasó de **0,023** a
**0,248** y todos los coeficientes
recuperaron su signo y su magnitud esperables. Es el hallazgo más grave de
los cuatro y el único que no nació en una decisión nuestra: le habría pasado
a cualquiera que use estos microdatos sin leer el diccionario de variables.

## 2. La rejilla de hiperparámetros estaba acotada

*Decisión propia.* Al buscar los hiperparámetros del modelo desplegado, los
tres ganadores quedaron en el borde del rango que se había probado — la
señal clásica de que el óptimo estaba fuera de la rejilla y nunca se llegó a
mirar. Se amplió el rango y se volvió a buscar: el error baja de
**S/ 610,90** a **S/ 607,31**, y los tres
hiperparámetros quedan ya en el interior. La mejora es sistemática: gana en
los cinco pliegues de la validación cruzada. Y aun así **no se promovió**.
El motivo no es que la diferencia sea ruido, porque no lo es: es que
0,59 % de mejora no justifica regenerar el artefacto
desplegado, revalidar el factor de smearing y rehacer todo el precómputo de
la interfaz. Separar «es mejor» de «vale la pena cambiarlo» es parte del
método, y el hallazgo queda documentado en vez de barrido.

## 3. Una cifra del INEI con la etiqueta equivocada

*Decisión propia.* Se publicaba que el gradiente por tamaño de empresa
«replica el patrón oficial del INEI, con 88,6 % de
informalidad en microempresas». La cifra es real y es del INEI, pero
corresponde a su tramo de **1 a 10 trabajadores**, que no es la categoría
«Hasta 20» que usa este proyecto. Al resumir se perdió el tramo, y el lector
terminaba mapeando el 88,6 % a una categoría nuestra cuyo
valor propio es **81,1 %**. No era un dato inventado: era
una comparación mal etiquetada, que es más difícil de detectar precisamente
porque cada mitad, por separado, es correcta. La app ya no la escribe a
mano: la calcula en el precómputo.

## 4. Tres afirmaciones distintas sobre el mismo R²

*Decisión propia y de documentación.* Sobre cuál es el R² esperable en una
ecuación de ingresos circulaban por el proyecto tres versiones a la vez —
«0,4–0,5», «rara vez supera 0,4» y «ningún R² supera 0,5» — repartidas en
cuatro sitios distintos, cada una escrita en un momento diferente y ninguna
consciente de las otras. Al ir a verificarlas apareció el segundo problema:
las dos fuentes que se citaban para sostenerlas, Lemieux (2006) y Heckman,
Lochner y Todd (2006), **no reportan ningún R²**, así que no se las podía
citar para eso. Hoy la afirmación se define **una sola vez**, se apoya en
los cuadros de Mincer y de Card, y dice explícitamente qué parte es lectura
nuestra. La solución de fondo es esa: una cifra, un lugar donde vive.

---

**La línea de método.** Los problemas de origen se corrigen y se documentan;
los propios se corrigen y se aprende de ellos; los de cita se verifican
yendo al texto completo. Ninguno se borra: un hallazgo corregido en silencio
es un hallazgo desperdiciado. Y los dos primeros tenían la misma raíz —
cifras escritas a mano que nadie vuelve a comprobar — así que el arreglo
estructural fue sacarlas del texto y calcularlas en el precómputo.
