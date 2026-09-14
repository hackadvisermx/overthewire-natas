# Natas Level08

## Descripción
> **Level Goal (natas8.natas.labs.overthewire.org):** Un formulario de "secreto" compara lo enviado contra `$encodedSecret`, un valor fijo, pasándolo antes por una función `encodeSecret()`.

## Solución
El código fuente (visible vía `index-source.html`) muestra la función de codificación y el valor codificado en hexadecimal:

```php
$encodedSecret = "3d3d516343746d4d6d6c315669563362";
function encodeSecret($secret) {
    return bin2hex(strrev(base64_encode($secret)));
}
```

Para obtener el secreto original hay que invertir el proceso en orden inverso: de hex a bytes, invertir la cadena, y decodificar base64.

```bash
python3 -c '
h = "3d3d516343746d4d6d6c315669563362"
s = bytes.fromhex(h).decode()[::-1]
import base64
print(base64.b64decode(s).decode())
'
# oubWYf2kBq

curl -s -u natas8:ugXL95KQmUAJJj6bMezOlBNDyI9Imwkc \
  -d "submit=1&secret=oubWYf2kBq" \
  http://natas8.natas.labs.overthewire.org/index.php
# Access granted. The password for natas9 is UdxmI27dTaXmnd1rxKQTfws6jihTdcQ9
```

## Notas adicionales
- "Seguridad por ofuscación": el algoritmo de codificación es simétrico y reversible sin ninguna clave secreta, solo composición de funciones conocidas (`base64`, `strrev`, `bin2hex`). Al conocerse el código fuente, invertirlo es trivial.

## Referencias
- Reto original: http://natas8.natas.labs.overthewire.org/
- Apoyo: https://www.php.net/manual/en/function.base64-encode.php (funciones PHP usadas: base64, strrev, bin2hex)
