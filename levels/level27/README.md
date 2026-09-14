# Natas Level27

## Descripción
> **Level Goal (natas27.natas.labs.overthewire.org):** Un sistema de registro/login contra una tabla `users(username, password)` (VARCHAR(64) cada campo). `validUser()` comprueba si el usuario existe, `checkCredentials()` verifica usuario+contraseña, `createUser()` registra uno nuevo (rechazando cualquier username con espacios al principio o al final: `if($usr != trim($usr)) { echo "Go away hacker"; ... }`), y `dumpData()` — tras un login exitoso — vuelve a consultar por usuario, pero usando `trim($usr)` en vez del valor tal cual, y **solo devuelve la primera fila** que encuentre (`return print_r($row,true)` dentro del `while`).

## Solución
El fallo es una inconsistencia entre tres piezas de código que deberían tratar el nombre de usuario de la misma forma y no lo hacen:

1. **`createUser` trunca a 64 caracteres antes de insertar** (`substr($usr, 0, 64)`), pero solo rechaza espacios sobrantes mirando el string **original, sin truncar**.
2. **`dumpData` recorta (`trim`) el nombre antes de buscar**, mientras que `checkCredentials`/`validUser` **no** lo hacen.
3. La tabla **no tiene ninguna restricción de unicidad** sobre `username`: nada impide que dos filas compartan el mismo valor.

Combinando los tres puntos: si registramos el usuario `"natas28" + 57 espacios + "x"` (65 caracteres en total), `createUser` lo acepta porque el string, tal cual, no empieza ni termina en espacio (termina en `"x"`) — pasa su propio filtro. Pero al insertarlo, lo trunca a los primeros 64 caracteres, así que lo que realmente queda guardado en la base de datos es `"natas28"` seguido de exactamente 57 espacios (la `"x"` se pierde). Como ese valor de 64 caracteres es distinto (para una comparación exacta de cadenas) del `"natas28"` real ya existente, `validUser` no lo considera un duplicado y deja crear la fila con la contraseña que nosotros elijamos.

A continuación, iniciamos sesión usando exactamente ese mismo valor de 64 caracteres (`"natas28"` + 57 espacios, sin la `"x"` esta vez, para que coincida byte a byte con lo guardado). `checkCredentials` valida perfectamente contra **nuestra** fila. Pero al llamar a `dumpData()` con ese mismo nombre, la función le aplica `trim()` internamente, convirtiéndolo en `"natas28"` **sin espacios** — que ahora coincide tanto con nuestra fila (por casualidad de longitud) como, sobre todo, con la fila real y preexistente del usuario `natas28`. Como la consulta no tiene `ORDER BY` y el bucle de `dumpData` se detiene en la **primera** fila encontrada, y la fila real de `natas28` fue insertada mucho antes que la nuestra (aparece primero en el orden de inserción), el resultado que se imprime es el de la cuenta real — filtrando su contraseña.

```python
import requests

auth = ("natas27", "mj2mBEPWycXTTg5BXYT7UPXgXHx5hjvV")
url = "http://natas27.natas.labs.overthewire.org/index.php"

# 1) Registrar un usuario "natas28" + 57 espacios + "x" (65 caracteres):
#    pasa el filtro anti-espacios de createUser (termina en "x", no en espacio),
#    pero al truncarse a 64 caracteres para el INSERT, la "x" se pierde.
reg_user = "natas28" + " " * 57 + "x"
requests.post(url, auth=auth, data={"username": reg_user, "password": ""})

# 2) Iniciar sesión con el mismo valor pero SIN la "x" (64 caracteres exactos,
#    coincide byte a byte con lo que quedó guardado en la base de datos)
login_user = "natas28" + " " * 57
r = requests.post(url, auth=auth, data={"username": login_user, "password": ""})
print(r.text)
# [username] => natas28
# [password] => Hy5wZLfVml7jnGmuvfbilRTUUkk29Dv3
```

## Notas adicionales
- El primer intento (equivocado) fue asumir que MySQL ignoraría los espacios finales por sí solo en la comparación `username='natas28'` (comportamiento típico de "PAD SPACE" en columnas `CHAR`/`VARCHAR`) e iniciar sesión con el nombre **sin** espacios tras el registro — eso no funcionó en esta instancia concreta del servidor (se comprobó empíricamente creando cuentas de prueba con sufijos aleatorios: el registro con espacios finales y el login con el nombre "limpio" **no** coincidían como la misma fila). El paso que realmente faltaba era iniciar sesión con el nombre **con los 64 caracteres exactos** (incluidos los espacios) para que `checkCredentials` encontrara nuestra propia fila, dejando que fuera **`dumpData`**, y solo `dumpData`, quien aplicara el `trim()` que produce la colisión con la fila real de `natas28`.
- La contraseña usada en el registro y el login es irrelevante para el resultado final — de hecho puede dejarse vacía — porque lo único que importa es que `checkCredentials` encuentre *alguna* fila que combine ese nombre de usuario exacto con esa contraseña exacta (la nuestra), no que se autentique como el `natas28` real.
- Lección general: cuando varias funciones de una misma aplicación manipulan el mismo dato de entrada de formas sutilmente distintas (una trunca, otra recorta espacios, otra no hace ninguna de las dos), cualquier suposición de que "todas lo tratan igual" puede ser una vulnerabilidad. Aquí, además, la ausencia de una restricción `UNIQUE` sobre `username` es lo que permite que existan filas "colisionables" en primer lugar.

## Referencias
- Reto original: http://natas27.natas.labs.overthewire.org/
- Apoyo (walkthrough con el mismo enfoque, confirmado funcional): https://gist.github.com/austinylin/18ce7f5cd730fda6631850d4d51cc098
- Apoyo: https://dev.mysql.com/doc/refman/8.0/en/char.html (manual de MySQL sobre semántica de `VARCHAR` y comparación de cadenas)
