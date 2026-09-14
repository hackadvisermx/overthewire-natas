# Características del host Natas (para réplica en contenedor)

Notas técnicas sobre la infraestructura del wargame Natas de OverTheWire, recopiladas mientras se resolvían los niveles. Natas es un wargame **web**, a diferencia de Bandit (SSH): cada nivel es una aplicación PHP distinta servida por HTTP, y el "login" al siguiente nivel es HTTP Basic Auth, no una shell.

## Acceso
- Cada nivel `N` vive en su propio (sub)dominio: `natasN.natas.labs.overthewire.org`, puerto 80 (HTTP plano, sin TLS).
- Autenticación HTTP Basic: usuario `natasN`, contraseña obtenida resolviendo el nivel `N-1` (excepto `natas0`, cuya contraseña, `natas0`, es pública).
- Backend: Apache/2.4.66 (Ubuntu) + PHP, con MySQL/MariaDB para los niveles de inyección SQL.
- No hace falta navegador: `curl -u natasN:pass http://natasN.natas.labs.overthewire.org/...` cubre prácticamente todo el flujo (incluyendo `-b`/`-c` para cookies, `-F` para subir archivos, `-H` para forjar headers, `-d`/`--data-urlencode` para POST).

## Mecanismos de "juego" observados
- **Comentarios HTML con la contraseña** en el código fuente, a veces con protecciones puramente client-side (bloqueo de clic derecho) que no afectan a `curl` — niveles 0-1.
- **Listados de directorio (Apache `Indexes`) y `robots.txt`** exponiendo archivos no enlazados (`users.txt`) — niveles 2-3.
- **Controles de acceso basados en headers/cookies no verificados** (`Referer`, cookie `loggedin`) — niveles 4-5.
- **Archivos "incluidos" servidos directamente como estáticos** (`includes/secret.inc`) pese a que la vista de código fuente los censura — nivel 6.
- **Local File Inclusion (LFI)** vía parámetro `page` pasado sin validar a `include()` — nivel 7.
- **"Seguridad por ofuscación" reversible** (`bin2hex(strrev(base64_encode(...)))`) — nivel 8.
- **Inyección de comandos** vía `passthru("grep ... $key ...")`, primero sin filtro, luego con blacklist de `;|&` evadible con salto de línea — niveles 9-10.
- **XOR con clave corta repetida** en cookies, roto con ataque de texto plano conocido — nivel 11.
- **Subida de archivos sin restricción de tipo real**, evadiendo primero ninguna validación y luego `getimagesize()` con un polyglot GIF+PHP — niveles 12-13.
- **Inyección SQL clásica** en login (con matiz de precedencia `AND`/`OR`) y **blind SQL injection booleana** carácter a carácter contra una tabla `users`, con la sorpresa de que la comparación en SQL es *case-insensitive* por la collation por defecto (`utf8_general_ci` o similar) mientras que el HTTP Basic Auth real sí distingue mayúsculas/minúsculas — hace falta forzar `BINARY` en la comparación SQL para extraer el valor exacto — niveles 14-16.
- Estructura general: cada nivel tiene un botón "View sourcecode" (`index-source.html`) que muestra el PHP con `highlight_string()`/similar, pero censurando variables sensibles (`<censored>`) — el propio código fuente es la pista principal de cada reto.
- **Inyección SQL basada en tiempo (`UNION SELECT SLEEP(...)`)** cuando la tabla no tiene filas que combinen con el predicado y un `AND`/`OR` normal nunca llega a evaluar `SLEEP()` — nivel 17.
- **Espacio de IDs de sesión demasiado pequeño** (`rand(1, 640)`, con o sin codificación hexadecimal reversible del propio nombre de usuario dentro del ID) — fuerza bruta de 640 valores para secuestrar una sesión con `admin=1` ya existente en el servidor compartido — niveles 18-19.
- **Manejadores de sesión PHP "caseros"** (`session_set_save_handler`) que serializan `$_SESSION` como líneas de texto sin escapar delimitadores, permitiendo inyectar variables de sesión arbitrarias insertando un salto de línea en un valor controlado — nivel 20.
- **Dos aplicaciones "colocadas" compartiendo el mismo almacén de sesiones PHP**, donde una validación de "solo estas claves" se aplica en la vista pero no en el guardado — nivel 21.
- **`header("Location: ...")` sin `exit` posterior**, dejando que el resto del script (incluido contenido "protegido") se siga ejecutando y enviando en el cuerpo de la respuesta — nivel 22.
- ***Type juggling* de PHP** en comparaciones débiles (`==`) entre cadenas y números, y en funciones como `strcmp()` cuando reciben un array en vez de una cadena (devuelven `NULL`/`false` en vez de fallar) — niveles 23-24.
- **LFI con filtro de *directory traversal* no recursivo** (`str_replace("../", "", ...)` aplicado una sola vez, evadible con `....//`) combinado con **envenenamiento de logs** (escritura sin escapar de la cabecera `User-Agent` en un archivo que después puede incluirse como código) — nivel 25.
- **Inyección de objetos PHP (`unserialize()` sobre datos de cliente)**, con una clase cuyo `__destruct()` escribe en un archivo cuyo nombre y contenido son completamente controlados por el atacante (webshell en el propio directorio público) — nivel 26.
- **Inconsistencias de tratamiento del mismo dato en funciones distintas** de una misma app (una trunca a N bytes, otra recorta espacios, otra no hace ninguna de las dos) combinadas con **ausencia de restricción `UNIQUE`** en una tabla, permitiendo filas "colisionables" — nivel 27.
- **Cifrado de bloque en modo ECB** (sin encadenar bloques) para "proteger" un parámetro antes de usarlo en una consulta SQL con comillas escapadas — permite manipular/recombinar bloques cifrados de peticiones distintas ("ECB block splicing") para desalinear el escapado y lograr inyección SQL sin conocer la clave — nivel 28.
- **`open()` de Perl con dos argumentos** interpretando un valor que empieza por `|` como tubería de shell en vez de nombre de archivo, con bypass de filtro de palabra partiéndola con comillas — nivel 29.
- **`DBI->quote($value, $type)` de Perl** con un segundo argumento (tipo SQL) controlable indirectamente a través de un parámetro CGI duplicado — si el tipo indica "numérico", el valor se inserta sin escapar ni entrecomillar — nivel 30.
- **`CGI.pm` de Perl en modo "keywords"** (query string sin `=`) volcando la lista de palabras en `@ARGV`, que `<ARGV>` recorre abriendo cada una como archivo — un vector de **LFI** que se puede transformar en **RCE real** si se logra que una única palabra clave conserve espacios internos (usando `%20` en vez de `+`, para evitar el troceo por espacios que hace `CGI.pm` antes de decodificar `%XX`) y termine en `|` — niveles 31-32.
- **Deserialización de metadatos de archivos Phar** (`phar://...` pasado a cualquier función de sistema de archivos, no solo a `unserialize()`) como vector de inyección de objetos PHP — nivel 33 (nivel final).

## Herramientas usadas para automatizar
- `curl` cubre casi todo (auth básica, cookies, POST, multipart, headers custom).
- Python (`requests`) para los ataques que requieren muchas peticiones automatizadas (fuerza bruta de blind SQLi carácter a carácter, fuerza bruta de session IDs, generación de payloads).
- `python3 -c`/scripts inline para operaciones de codificación/decodificación (base64, hex, XOR) sin depender de herramientas externas.
- **PHP CLI** (instalado vía Homebrew específicamente para el nivel 33) para generar localmente un archivo `.phar` con metadatos serializados forjados — necesario porque construir a mano el formato binario de Phar sería mucho más laborioso que usar la propia clase `Phar` de PHP.

## Ideas para la réplica en contenedor (fase futura, si se decide)
- Imagen con Apache + PHP + Perl (CGI) + MySQL, un vhost por nivel (o un único vhost parametrizado por subdominio/puerto) sirviendo el código correspondiente a cada reto.
- Guardar el mapa nivel→contraseña fuera del Dockerfile (variable de entorno o fichero de secretos), igual que en el proyecto Bandit.
- Replicar cuidadosamente los detalles de collation de MySQL en los niveles de SQLi para reproducir el matiz de mayúsculas/minúsculas de los niveles 15-17.
- Para los niveles 29-32 (Perl/CGI.pm), fijar una versión concreta de `CGI.pm` — el comportamiento exacto de "keywords"/`@ARGV` y el orden de decodificación de `%XX` frente al troceo por espacios depende de la versión del módulo.
- Para el nivel 27, tener en cuenta que el comportamiento de padding de espacios en comparaciones `VARCHAR` puede variar entre versiones/collations de MySQL — en el servidor probado durante esta sesión, la técnica que finalmente funcionó no dependía de ese padding (ver el writeup del nivel 27 para el detalle exacto que sí funcionó).
