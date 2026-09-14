# Natas Level03

## Descripción
> **Level Goal (natas3.natas.labs.overthewire.org):** "No hay nada en esta página. Ni siquiera Google lo va a encontrar esta vez." Es una pista de que la fuga de información ya no está en un directorio adivinable a mano, sino en algo que un buscador indexaría: `robots.txt`.

## Solución
`robots.txt` le dice a los crawlers qué rutas no indexar, pero es un archivo público que cualquiera puede leer. En este caso declara `Disallow: /s3cr3t/`, revelando la existencia de ese directorio, que a su vez tiene listado de directorios habilitado.

```bash
curl -s -u natas3:K30JrSRHzjxq3paUQuwozY4MNvmNFyhI http://natas3.natas.labs.overthewire.org/robots.txt
# Disallow: /s3cr3t/

curl -s -u natas3:K30JrSRHzjxq3paUQuwozY4MNvmNFyhI http://natas3.natas.labs.overthewire.org/s3cr3t/users.txt
# natas4:JDrPnuZAKyl6MkiqQGFIddrqpvgOASth
```

## Notas adicionales
- `robots.txt` es una convención para buscadores "bien portados"; no impone ninguna restricción de acceso real y no debería usarse para ocultar contenido sensible.
- Mismo patrón que el nivel 2: directorio con `Indexes` activado exponiendo un `users.txt`.

## Referencias
- Reto original: http://natas3.natas.labs.overthewire.org/
- Apoyo: https://www.robotstxt.org/robotstxt.html (especificación de robots.txt)
