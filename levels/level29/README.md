# Natas Level29

## Descripción
> **Level Goal (natas29.natas.labs.overthewire.org):** Un selector desplegable ("perl underground 1-5") carga distintos textos vía `index.pl?file=<nombre>`. No hay enlace de "ver código fuente".

## Solución
El script Perl detrás de `index.pl` casi con toda seguridad abre el archivo con la forma de dos argumentos de `open()`: `open(FILE, "texts/" . $file . ".txt")`. En Perl, si la cadena que se le pasa a esta forma de `open()` **empieza por `|`**, Perl no la trata como un nombre de archivo: la interpreta como una **tubería de shell** y ejecuta lo que sigue como un comando, devolviendo su salida. Es el clásico fallo de "Perl open() de dos argumentos", muy anterior y hoy generalmente evitado usando la forma segura de tres argumentos.

Dos detalles adicionales hay que resolver:
- El código añade `.txt` al final de nuestro valor antes de abrir. Para que nuestro comando no termine con `.txt` pegado (lo que rompería su sintaxis), se usa un **byte nulo** (`%00`) al final: en el Perl usado aquí, el nombre de archivo (o, en este caso, el comando) que llega a `open()` se corta en el primer byte nulo, ignorando todo lo que el propio código añada después.
- El código filtra la palabra `"natas"` en el valor recibido (para impedir leer directamente `/etc/natas_webpass/natasXX`). Basta con partir la palabra con comillas dobles en medio (`na"tas_webpass/nat"as30`): para el shell, las comillas simplemente concatenan fragmentos de la misma palabra sin dejar rastro de "natas" como subcadena contigua, así que el filtro de texto no lo detecta, pero el comando final ejecutado es idéntico.

```python
import requests

auth = ("natas29", "hwgoYUiGWoSZAqphtCAZf7u1jS16KEah")
url = "http://natas29.natas.labs.overthewire.org/index.pl"

payload = '|cat /etc/na"tas_webpass/nat"as30\x00'
r = requests.get(url, auth=auth, params={"file": payload})
print(r.text[-200:])
# frO4U4zCfVJXq2zG5HSVNjA46nQGzoqF
```

## Notas adicionales
- La salida del comando aparece al **final** de la respuesta HTML, fuera de las etiquetas `<pre>` habituales — el script simplemente vuelca lo leído de la tubería sin integrarlo en la plantilla de la página, así que conviene mirar el cuerpo completo de la respuesta, no solo la sección esperada.
- Con `|id\x00` como prueba de concepto se confirma la ejecución de comandos antes de intentar leer el archivo de contraseñas — un paso útil para separar "¿tengo RCE?" de "¿logro evadir el filtro de palabra?".
- Este fallo es distinto (y más grave) que un simple *Local File Inclusion*: no se trata de leer archivos arbitrarios, sino de **ejecutar cualquier comando del sistema** como el usuario que corre el proceso web, simplemente por la forma insegura en que Perl decide si un argumento a `open()` es una ruta de archivo o una orden de shell.

## Referencias
- Reto original: http://natas29.natas.labs.overthewire.org/
- Apoyo: https://perldoc.perl.org/functions/open (manual de Perl — advertencia explícita sobre `open()` de 2 argumentos y tuberías)
- Apoyo: https://anyafachri.medium.com/command-injection-via-file-inclusion-vulnerability-natas29-overthewire-write-up-16c801259edf (walkthrough con el mismo enfoque de bypass del filtro de "natas")
