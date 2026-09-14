# OverTheWire: Natas

Writeups y automatización de los 35 niveles (00-34) del wargame web [Natas](https://overthewire.org/wargames/natas/) de OverTheWire. A diferencia de Bandit (SSH), cada nivel de Natas es una aplicación web distinta servida por HTTP, y la contraseña de cada nivel se obtiene explotando una vulnerabilidad concreta de esa aplicación (autenticación básica HTTP: usuario `natasN`, contraseña obtenida al resolver el nivel `N-1`).

## Contenido

- **[`PROGRESS.md`](PROGRESS.md)** — estado de avance por nivel, fases del proyecto y notas relevantes descubiertas durante la resolución (matices de collation en MySQL, inconsistencias explotables entre funciones, bugs encontrados al automatizar, etc.).
- **`levels/levelNN/README.md`** — un writeup por nivel (00 a 34), cada uno con: el objetivo oficial del reto, la explicación de la vulnerabilidad y la solución paso a paso con los comandos usados, notas adicionales, y referencias de apoyo. `levels/_template/` contiene la plantilla usada para escribir cada writeup.
- **[`notes/host-characteristics.md`](notes/host-characteristics.md)** — notas técnicas sobre la infraestructura del wargame (acceso, patrones de vulnerabilidad recurrentes, ideas para replicar un entorno similar en contenedor).
- **`scripts/`**:
  - **[`solve_level.py`](scripts/solve_level.py)** — script en Python puro (solo depende de `requests`) que automatiza la explotación de los 34 niveles resolubles (0→33), reproduciendo la técnica documentada en cada writeup. Guarda cada contraseña obtenida en `scripts/passwords.json` (no versionado) para poder encadenar niveles sin volver a pasar `--password`.
    ```bash
    python3 scripts/solve_level.py --level N [--password XXX] [--all]
    ```
  - **[`natas_get.sh`](scripts/natas_get.sh)** — helper en bash para hacer peticiones GET autenticadas rápidas desde la terminal (`curl` con HTTP Basic Auth).

Las contraseñas reales (`scripts/passwords.json`, `scripts/creds.txt`) no se versionan — ver [`.gitignore`](.gitignore).

## Técnicas cubiertas

Un recorrido representativo de vulnerabilidades web clásicas, cada una aislada en su propio nivel: fugas de información (comentarios HTML, `robots.txt`, listados de directorio), controles de acceso basados en headers/cookies sin verificar, LFI, inyección de comandos, XOR con clave repetida, bypass de subida de archivos, inyección SQL (clásica, ciega booleana, ciega basada en tiempo, con matices de *collation*), sesiones PHP predecibles o con manejadores caseros vulnerables, *type juggling*, inyección de objetos PHP (`unserialize()` y deserialización de metadatos de Phar vía `phar://`), cifrado en modo ECB manipulable por bloques, y varios fallos específicos de Perl/CGI.pm (`open()` con tuberías, `DBI->quote()`, `@ARGV`).

## Uso

Cada writeup incluye los comandos exactos (`curl`, Python) para reproducir la explotación manualmente. Para resolver todo automáticamente:

```bash
python3 scripts/solve_level.py --level 0 --password natas0 --all
```

El nivel 33 requiere además un binario `php` local (p. ej. `brew install php`) para generar un `.phar` malicioso.
