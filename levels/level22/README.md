# Natas Level22

## Descripción
> **Level Goal (natas22.natas.labs.overthewire.org):** El código muestra las credenciales solo si `$_GET["revelio"]` está presente **y** se es admin; si no se es admin, hace `header("Location: /");` para redirigir fuera de la página.

## Solución
El bug está en que, tras llamar a `header("Location: /")`, el código **no llama a `exit`/`die`**. En PHP, `header()` solo añade una cabecera HTTP a la respuesta; no detiene la ejecución del script por sí sola. El resto del script sigue ejecutándose y generando el cuerpo de la respuesta con normalidad — incluida la sección que imprime las credenciales cuando `revelio` está presente, **sin volver a comprobar si el usuario es admin en ese bloque**.

Un navegador real seguiría la redirección (código 302) y nunca vería ese cuerpo, pero cualquier cliente HTTP que no siga automáticamente el `Location` (como `curl` sin `-L`) recibe igualmente el cuerpo completo de la respuesta, incluyendo el contenido "sensible" que se suponía protegido.

```bash
curl -s -u natas22:964laB0r7TuDqJj5b3HFtwsQoc0GhjBF \
  "http://natas22.natas.labs.overthewire.org/index.php?revelio=1"
# You are an admin. The credentials for the next level are:
# Username: natas23
# Password: CH1OBxJy8uAxMM15Nx6VXSMwcJbBbnS5
```

## Notas adicionales
- No hace falta ni sesión ni cookies: basta con no seguir la redirección para ver el contenido que se suponía descartado.
- Regla general en PHP (y en cualquier lenguaje donde emitir una redirección no detenga el flujo del programa): **toda redirección de control de acceso debe ir seguida de `exit`/`die`** inmediatamente después de `header("Location: ...")`, de lo contrario el código "protegido" que sigue se ejecuta igual.

## Referencias
- Reto original: http://natas22.natas.labs.overthewire.org/
- Apoyo: https://www.php.net/manual/en/function.header.php (manual de PHP — nota explícita de que `header()` no interrumpe la ejecución del script)
