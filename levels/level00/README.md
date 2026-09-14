# Natas Level00

## Descripción
> **Level Goal (natas0.natas.labs.overthewire.org):** "La contraseña de este nivel está en esta misma página."

## Solución
El acceso HTTP usa autenticación básica (usuario `natas0`, contraseña pública `natas0`). La contraseña del siguiente nivel está escondida en un comentario HTML dentro del código fuente de la página, no visible al renderizarla normalmente.

```bash
curl -s -u natas0:natas0 http://natas0.natas.labs.overthewire.org/
# <!--The password for natas1 is scfWG6qNEIdzqVyfRwEGXyNUfFZkZeQ7 -->
```

## Notas adicionales
- Todos los niveles de Natas usan HTTP Basic Auth con usuario `natasN` sobre el host `natasN.natas.labs.overthewire.org` (puerto 80).
- `curl -u user:pass` evita tener que interactuar con un navegador; es la base de todo el flujo de trabajo de este wargame.

## Referencias
- Reto original: http://natas0.natas.labs.overthewire.org/
- Apoyo: https://curl.se/docs/manpage.html (opción `-u` para autenticación básica)
