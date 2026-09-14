# Natas Level34

## Descripción
> **Level Goal (natas34.natas.labs.overthewire.org):** "Congratulations! You have reached the end... for now."

## Solución
No hay reto que resolver: al iniciar sesión con la contraseña obtenida en el nivel 33, la página simplemente confirma que se ha llegado al final de la secuencia de niveles publicada del wargame Natas. No existe (por ahora) un nivel 35 ni una contraseña adicional que extraer.

```bash
curl -s -u natas34:cT3LVC2sd5RtaRHdAE2xr16nYGuArbbK http://natas34.natas.labs.overthewire.org/
# Congratulations! You have reached the end... for now.
```

## Notas adicionales
- Natas (a fecha de esta sesión) tiene 35 niveles publicados (00 a 34); el 34 es el último y no exige ninguna técnica adicional.
- Recorrido completo: desde comentarios HTML triviales (nivel 0) hasta deserialización de objetos PHP vía metadatos de `.phar` (nivel 33), pasando por inyección de comandos, inyección SQL (booleana, basada en tiempo y con `UNION`), manipulación de sesiones PHP, criptografía en modo ECB, *type juggling*, *object injection* clásica y bugs específicos de Perl (`open()`/`<ARGV>` con tuberías) — un repaso muy completo de vulnerabilidades web reales, cada una aislada en su propio nivel didáctico.

## Referencias
- Reto original: http://natas34.natas.labs.overthewire.org/
