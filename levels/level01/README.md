# Natas Level01

## Descripción
> **Level Goal (natas1.natas.labs.overthewire.org):** "No hagas clic derecho." La página bloquea el menú contextual con `onContextMenu`, intentando evitar "Ver código fuente" desde el navegador.

## Solución
El bloqueo del clic derecho es una protección puramente del lado del cliente (JavaScript en el DOM). Como `curl` no ejecuta JavaScript ni respeta eventos del ratón, simplemente pedimos la página igual que en el nivel anterior y el comentario con la contraseña sigue estando en el HTML.

```bash
curl -s -u natas1:scfWG6qNEIdzqVyfRwEGXyNUfFZkZeQ7 http://natas1.natas.labs.overthewire.org/
# <!--The password for natas2 is vsDOxoXyq3wckCP1ZmTZ71ngIA606odB -->
```

## Notas adicionales
- Cualquier restricción implementada solo en JavaScript/HTML del lado del cliente es trivialmente evitable pidiendo el recurso directamente por HTTP.

## Referencias
- Reto original: http://natas1.natas.labs.overthewire.org/
- Apoyo: https://curl.se/docs/manpage.html
