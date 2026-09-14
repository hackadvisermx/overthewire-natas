# Natas Level11

## Descripción
> **Level Goal (natas11.natas.labs.overthewire.org):** "Las cookies están protegidas con cifrado XOR." Hay un formulario para cambiar el color de fondo, y una cookie `data` (JSON con `showpassword` y `bgcolor`) cifrada con XOR de clave repetida y luego codificada en base64.

## Solución
XOR con clave repetida es vulnerable a un ataque de "known plaintext": si conocemos el texto plano de una cookie y su versión cifrada, podemos recuperar la clave con un simple XOR entre ambos (porque `(P xor K) xor P = K`). La cookie por defecto tiene un JSON predecible: `{"showpassword":"no","bgcolor":"#ffffff"}`.

```bash
# 1. Pedimos la cookie por defecto (loggedin implícito, aquí es "data")
curl -s -u natas11:VUMQDmuITOEHzhviLE5V0VG9cPMQkyxd -c cookies.jar \
  http://natas11.natas.labs.overthewire.org/ -o /dev/null
# data=EGAgHwQ1IxYYMSQYGSZxTUksPFVHYDEQCC0/GBlgaVVIJDURDSQ1VRY=

python3 -c '
import base64
cookie = "EGAgHwQ1IxYYMSQYGSZxTUksPFVHYDEQCC0/GBlgaVVIJDURDSQ1VRY="
cipher = base64.b64decode(cookie)
known = b"{\"showpassword\":\"no\",\"bgcolor\":\"#ffffff\"}"
key = bytes([c ^ p for c, p in zip(cipher, known)])
print(key)
'
# b"kBSwkBSwkBSw..." -> la clave es "kBSw" (4 bytes) repetida

# 2. Con la clave recuperada, ciframos un JSON con showpassword=yes
python3 -c '
import base64
key = b"kBSw"
plain = b"{\"showpassword\":\"yes\",\"bgcolor\":\"#ffffff\"}"
out = bytes([p ^ key[i % len(key)] for i, p in enumerate(plain)])
print(base64.b64encode(out).decode())
'
# EGAgHwQ1IxYYMSQYGSZxTUk7NgRJbnEVDCE8GwQwcU1JYTURDSQ1EUk/

curl -s -u natas11:VUMQDmuITOEHzhviLE5V0VG9cPMQkyxd \
  -b "data=EGAgHwQ1IxYYMSQYGSZxTUk7NgRJbnEVDCE8GwQwcU1JYTURDSQ1EUk%2F" \
  http://natas11.natas.labs.overthewire.org/
# The password for natas12 is EAGkE8uzFTxeoTT2mMst9Xy7PX6guEng
```

## Notas adicionales
- El servidor valida `bgcolor` contra una regex (`^#[a-f\d]{6}$`), por eso se mantiene `#ffffff` sin cambios en el plaintext forjado — solo interesa modificar `showpassword`.
- XOR con clave corta y repetida es esencialmente un cifrado de Vigenère; si se conoce (o se puede adivinar) cualquier fragmento de texto plano correspondiente a un cifrado dado, la clave (o parte de ella) queda expuesta.

## Referencias
- Reto original: http://natas11.natas.labs.overthewire.org/
- Apoyo: https://en.wikipedia.org/wiki/Known-plaintext_attack (ataque de texto plano conocido)
