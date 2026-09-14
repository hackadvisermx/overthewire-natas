# Progreso Natas (OverTheWire)

Estado de avance por nivel. Contraseñas se guardan solo localmente (no se suben a repos públicos); los writeups documentan técnica, no las claves en sí (salvo capturas de comandos ya ejecutados, siguiendo el mismo criterio del proyecto Bandit).

| Nivel | Estado | Writeup |
|-------|--------|---------|
| 00 | ✅ resuelto | [levels/level00](levels/level00/README.md) |
| 01 | ✅ resuelto | [levels/level01](levels/level01/README.md) |
| 02 | ✅ resuelto | [levels/level02](levels/level02/README.md) |
| 03 | ✅ resuelto | [levels/level03](levels/level03/README.md) |
| 04 | ✅ resuelto | [levels/level04](levels/level04/README.md) |
| 05 | ✅ resuelto | [levels/level05](levels/level05/README.md) |
| 06 | ✅ resuelto | [levels/level06](levels/level06/README.md) |
| 07 | ✅ resuelto | [levels/level07](levels/level07/README.md) |
| 08 | ✅ resuelto | [levels/level08](levels/level08/README.md) |
| 09 | ✅ resuelto | [levels/level09](levels/level09/README.md) |
| 10 | ✅ resuelto | [levels/level10](levels/level10/README.md) |
| 11 | ✅ resuelto | [levels/level11](levels/level11/README.md) |
| 12 | ✅ resuelto | [levels/level12](levels/level12/README.md) |
| 13 | ✅ resuelto | [levels/level13](levels/level13/README.md) |
| 14 | ✅ resuelto | [levels/level14](levels/level14/README.md) |
| 15 | ✅ resuelto | [levels/level15](levels/level15/README.md) |
| 16 | ✅ resuelto | [levels/level16](levels/level16/README.md) |
| 17 | ✅ resuelto | [levels/level17](levels/level17/README.md) |
| 18 | ✅ resuelto | [levels/level18](levels/level18/README.md) |
| 19 | ✅ resuelto | [levels/level19](levels/level19/README.md) |
| 20 | ✅ resuelto | [levels/level20](levels/level20/README.md) |
| 21 | ✅ resuelto | [levels/level21](levels/level21/README.md) |
| 22 | ✅ resuelto | [levels/level22](levels/level22/README.md) |
| 23 | ✅ resuelto | [levels/level23](levels/level23/README.md) |
| 24 | ✅ resuelto | [levels/level24](levels/level24/README.md) |
| 25 | ✅ resuelto | [levels/level25](levels/level25/README.md) |
| 26 | ✅ resuelto | [levels/level26](levels/level26/README.md) |
| 27 | ✅ resuelto | [levels/level27](levels/level27/README.md) |
| 28 | ✅ resuelto | [levels/level28](levels/level28/README.md) |
| 29 | ✅ resuelto | [levels/level29](levels/level29/README.md) |
| 30 | ✅ resuelto | [levels/level30](levels/level30/README.md) |
| 31 | ✅ resuelto | [levels/level31](levels/level31/README.md) |
| 32 | ✅ resuelto | [levels/level32](levels/level32/README.md) |
| 33 | ✅ resuelto | [levels/level33](levels/level33/README.md) |
| 34 | ✅ resuelto (nivel final) | [levels/level34](levels/level34/README.md) |

**Fase 1 completa: 35 niveles (0-34) resueltos y documentados.** Natas termina en el nivel 34.

## Fases del proyecto
1. ✅ **Resolver los 35 niveles (0-34) con writeups** — completo
2. ✅ **Notas de arquitectura del host** (`notes/host-characteristics.md`) — completo, recopiladas durante la fase 1
3. ⏳ **Contenedor de práctica local** replicando la estructura — futuro
4. ⏳ **Mejora pedagógica de la secuencia** para estudiantes — futuro

## Notas de progreso
- Resuelto con `curl` (autenticación básica, cookies, multipart, headers) y Python (`requests`) para ataques automatizados (blind SQLi carácter a carácter, brute-force de sesiones, generación de payloads XOR/PHP object injection).
- Niveles con dificultades destacadas, corregidas o investigadas a fondo durante la sesión:
  - **15/16/17**: la comparación de cadenas en MySQL es *case-insensitive* por la collation por defecto; hubo que forzar `BINARY` en las condiciones SQL para extraer contraseñas con mayúsculas/minúsculas exactas.
  - **27**: requirió reproducir con cuidado una inconsistencia muy específica entre `createUser` (trunca a 64 bytes) y `dumpData` (recorta espacios) — el primer intento ingenuo (asumir equivalencia de espacios finales en la comparación SQL) no reprodujo en el servidor actual; hubo que iniciar sesión con el nombre de usuario "sucio" completo (64 bytes con espacios) para que fuera `dumpData`, y solo `dumpData`, quien introdujera la colisión.
  - **31**: la explotación inicial (con `cat ... |` como varias "keywords") en realidad solo lograba lectura de archivo (LFI), no ejecución de comandos — se corrigió el writeup tras verificarlo con el nivel 32, que exige demostrar ejecución real y reveló el verdadero mecanismo (`%20` en vez de `+` para mantener una única entrada de `@ARGV` con espacios internos).
  - **33**: resuelto con deserialización de metadatos de Phar (`phar://`), generando un `.phar` malicioso localmente con PHP (instalado vía Homebrew para esta sesión) cuyos metadatos son un objeto `Executor` forjado.
- Helper genérico en `scripts/natas_get.sh` para peticiones GET autenticadas rápidas desde la terminal.
- **[scripts/solve_level.py](scripts/solve_level.py)**: script único en Python puro (solo `requests`, sin dependencias exóticas) que automatiza la explotación de los 34 niveles (0→33), reproduciendo exactamente la técnica de cada writeup. Uso: `python3 scripts/solve_level.py --level N [--password XXX] [--all]`; guarda cada contraseña obtenida en `scripts/passwords.json` (no versionado, ver `.gitignore`), así que en llamadas siguientes `--password` es opcional. **Validado en vivo de punta a punta contra el servidor real, dos veces** (una encadenando desde el nivel 11 tras corregir varios bugs, otra desde el nivel 0 en limpio): las 34 contraseñas obtenidas coinciden exactamente con `scripts/creds.txt`.
- Bugs reales encontrados y corregidos mientras se probaba el script (más allá de los ya reflejados en los writeups):
  - Un helper `first_pw()` que buscaba "la primera cadena de 32 alfanuméricos" en la respuesta a veces capturaba la propia contraseña del nivel actual (visible en `wechallinfo`) o, en el nivel 30, una subcadena desplazada porque el Perl imprime `usuario+contraseña` pegados sin separador.
  - El nivel 11 (cookie XOR) fallaba si el keystream derivado no se reducía a su período real antes de cifrar un texto de longitud distinta al original.
  - El nivel 17 (SQLi basada en tiempo) podía dar un carácter erróneo si otra petición concurrente al mismo servidor añadía suficiente jitter como para simular un `SLEEP()`; se corrigió exigiendo dos mediciones lentas consecutivas antes de aceptar un carácter, y evitando lanzar el script en paralelo con otras peticiones al mismo nivel.
  - El nivel 22 requería `allow_redirects=False`, porque el propio bug del nivel (falta de `exit()` tras `header("Location: ...")`) solo es observable si el cliente HTTP no sigue la redirección.
  - El nivel 26 usaba por error el nombre de cookie `data` (del nivel 11) en vez de `drawing`.
  - `requests` no aplica ningún timeout por defecto: una única petición colgada (carga puntual del servidor compartido) podía bloquear el script indefinidamente sin ningún error visible; se parcheó un timeout global de 20s más reintentos automáticos por nivel.
