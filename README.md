# OverTheWire: Natas

> Este repositorio es parte de **[sec-proy](https://github.com/hackadvisermx/sec-proy)**, un proyecto más amplio de soluciones a retos de ciberseguridad (CTFs, wargames y máquinas de hacking).

Writeups y automatización de los 35 niveles (00-34) del wargame web [Natas](https://overthewire.org/wargames/natas/) de OverTheWire. A diferencia de Bandit (SSH), cada nivel de Natas es una aplicación web distinta servida por HTTP, y la contraseña de cada nivel se obtiene explotando una vulnerabilidad concreta de esa aplicación (autenticación básica HTTP: usuario `natasN`, contraseña obtenida al resolver el nivel `N-1`).

## Contenido

- **[`PROGRESS.md`](PROGRESS.md)** — estado de avance por nivel, fases del proyecto y notas relevantes descubiertas durante la resolución (matices de collation en MySQL, inconsistencias explotables entre funciones, bugs encontrados al automatizar, etc.).
- **`levels/levelNN/README.md`** — un writeup por nivel (00 a 34), cada uno con: el objetivo oficial del reto, la explicación de la vulnerabilidad y la solución paso a paso con los comandos usados, notas adicionales, y referencias de apoyo. `levels/_template/` contiene la plantilla usada para escribir cada writeup.
- **`scripts/`**:
  - **[`natas_get.sh`](scripts/natas_get.sh)** — helper en bash para hacer peticiones GET autenticadas rápidas desde la terminal (`curl` con HTTP Basic Auth).

Las contraseñas reales y la automatización local de niveles no se versionan — ver [`.gitignore`](.gitignore).

## Técnicas cubiertas

Un recorrido representativo de vulnerabilidades web clásicas, cada una aislada en su propio nivel: fugas de información (comentarios HTML, `robots.txt`, listados de directorio), controles de acceso basados en headers/cookies sin verificar, LFI, inyección de comandos, XOR con clave repetida, bypass de subida de archivos, inyección SQL (clásica, ciega booleana, ciega basada en tiempo, con matices de *collation*), sesiones PHP predecibles o con manejadores caseros vulnerables, *type juggling*, inyección de objetos PHP (`unserialize()` y deserialización de metadatos de Phar vía `phar://`), cifrado en modo ECB manipulable por bloques, y varios fallos específicos de Perl/CGI.pm (`open()` con tuberías, `DBI->quote()`, `@ARGV`).

## Uso

Cada writeup incluye los comandos exactos (`curl`, Python) para reproducir la explotación manualmente. El nivel 33 requiere además un binario `php` local (p. ej. `brew install php`) para generar un `.phar` malicioso.

## Aviso

Este material es para uso educativo propio sobre un wargame público que autoriza explícitamente su resolución. Evita publicar las contraseñas o soluciones textuales fuera de un contexto de práctica personal como este.
