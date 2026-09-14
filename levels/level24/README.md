# Natas Level24

## Descripción
> **Level Goal (natas24.natas.labs.overthewire.org):** Muy parecido al nivel 23: un formulario de "contraseña" que revela las credenciales si `!strcmp($_REQUEST["passwd"], "<contraseña censurada>")` es verdadero — es decir, si `strcmp()` devuelve un valor "falsy" (típicamente 0, que significa "son iguales").

## Solución
`strcmp()` espera dos *strings*. Si en vez de una cadena se le pasa un **array** como argumento, PHP no puede compararlo como texto: en versiones antiguas de PHP, `strcmp()` devuelve `NULL` con un warning en vez de lanzar un error fatal, y `!NULL` se evalúa como `true` — exactamente la condición que abre el acceso, sin necesidad de conocer ni acertar la contraseña real.

Basta con enviar el parámetro `passwd` como array, usando la sintaxis de PHP para parámetros de formulario (`passwd[]=algo`), en vez de como cadena.

```bash
curl -s -u natas24:shlL4BvOtawNCd81dwdKRHFzmTEjYYQX -G \
  --data-urlencode "passwd[]=x" \
  http://natas24.natas.labs.overthewire.org/index.php
# The credentials for the next level are:
# Username: natas25 Password: UJEF5OAHF1eW3lqkpdCDM7ow4syzh4oo
```

## Notas adicionales
- Este patrón se repite en muchos CTFs de PHP: cualquier función que espere un tipo específico (`string`, `int`) pero reciba datos de `$_GET`/`$_POST`/`$_REQUEST` sin *type hinting* ni validación explícita puede recibir un array (`param[]=valor` en la query string) y comportarse de forma inesperada — a menudo devolviendo `null`, `false` o `0` en vez de fallar, lo cual puede burlar comparaciones flojas (`==`, `!=`, o negaciones como `!strcmp(...)`).
- La solución robusta del lado del desarrollador sería validar `is_string($_REQUEST["passwd"])` antes de usarlo, o comparar con `===` en vez de depender del valor de retorno de `strcmp()`.

## Referencias
- Reto original: http://natas24.natas.labs.overthewire.org/
- Apoyo: https://www.php.net/manual/en/function.strcmp.php (manual de PHP, comportamiento de `strcmp()` con tipos inesperados)
