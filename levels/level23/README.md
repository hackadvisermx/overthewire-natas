# Natas Level23

## Descripción
> **Level Goal (natas23.natas.labs.overthewire.org):** Un formulario de "contraseña" que solo revela las credenciales del siguiente nivel si el valor enviado **contiene** la subcadena `"iloveyou"` **y**, comparado como número, es **mayor que 10**: `strstr($_REQUEST["passwd"],"iloveyou") && ($_REQUEST["passwd"] > 10)`.

## Solución
A primera vista parecen dos condiciones contradictorias: una cadena de texto normal como `"iloveyou"` vale `0` al convertirla a número, así que `"iloveyou" > 10` es falso. Pero si la cadena **empieza** con dígitos, PHP la trata como numérica para efectos de comparación con un entero, tomando el prefijo numérico inicial. Basta con anteponer un número mayor que 10 a la subcadena requerida:

```bash
curl -s -u natas23:CH1OBxJy8uAxMM15Nx6VXSMwcJbBbnS5 -G \
  --data-urlencode "passwd=11iloveyou" \
  http://natas23.natas.labs.overthewire.org/index.php
# The credentials for the next level are:
# Username: natas24 Password: shlL4BvOtawNCd81dwdKRHFzmTEjYYQX
```

`"11iloveyou"` cumple ambas condiciones a la vez: `strstr()` encuentra `"iloveyou"` en cualquier parte de la cadena (no exige que sea toda la cadena), y al compararla con `10` PHP la interpreta por su prefijo numérico (`11`), que sí es mayor que `10`.

## Notas adicionales
- Esto es un caso de "type juggling" (conversión implícita de tipos) de PHP: comparar una cadena con un número fuerza una conversión de tipos que puede no coincidir con la intuición de "si no es un número, debería ser 0 o false". El comportamiento exacto (y si se emite un warning) varía entre versiones de PHP, pero el principio general — nunca comparar directamente un string controlado por el usuario contra un número sin normalizar/validar antes — se mantiene.
- La solución correcta para el desarrollador sería usar comparaciones estrictas (`===`) o validar explícitamente el formato esperado del valor antes de cualquier comparación numérica.

## Referencias
- Reto original: http://natas23.natas.labs.overthewire.org/
- Apoyo: https://www.php.net/manual/en/language.types.comparisons.php (manual de PHP, tabla de comparaciones y conversión de tipos)
