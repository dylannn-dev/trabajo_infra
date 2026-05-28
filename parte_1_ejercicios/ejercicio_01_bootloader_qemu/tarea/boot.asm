org 0x7C00
bits 16

main:
    ; 1. Configurar la pila y registros de segmento
    cli
    xor ax, ax
    mov ds, ax
    mov ss, ax
    mov sp, 0x7C00
    sti

    ; 2. Limpiar la pantalla usando BIOS
    mov ah, 0x00
    mov al, 0x03
    int 0x10

    ; 3. Preparar la escritura directa en memoria VGA
    mov ax, 0xB800
    mov es, ax      ; ES apunta al segmento de video
    xor di, di      ; DI = 0 (inicio de la pantalla arriba a la izquierda)
    mov si, mensaje ; SI apunta a nuestro texto

.imprimir_bucle:
    lodsb           ; Carga el siguiente byte de 'mensaje' en AL
    cmp al, 0       ; ¿Llegamos al final del string (0)?
    je .halt
    cmp al, 10      ; ¿Es un salto de linea (ASCII 10)?
    je .salto_linea

    ; Imprimir caracter con color
    mov ah, 0x0B    ; Color: 0=Fondo Negro, B=Texto Cyan Claro
    stosw           ; Guarda AL(letra) y AH(color) en video y avanza 2 bytes
    jmp .imprimir_bucle

.salto_linea:
    ; Logica matematica para saltar a la siguiente linea sin pasarnos de 512 bytes
    mov ax, di      ; Copiamos la posicion actual de pantalla
    mov cl, 160     ; Cada linea de pantalla ocupa 160 bytes (80 letras x 2 bytes)
    div cl          ; Dividimos posicion actual / 160
    inc al          ; Sumamos 1 a la fila actual
    mul cl          ; Multiplicamos por 160 para hallar el inicio de la fila nueva
    mov di, ax      ; Movemos el cursor a esa nueva posicion
    jmp .imprimir_bucle

.halt:
    hlt
    jmp .halt

; 4. Zona de datos (Texto Institucional)
; El número 10 funciona como "Enter" (salto de linea)
mensaje db 'Curso: Infraestructura', 10
        db 'Grupo: Ciencia de Datos', 10, 10
        db ' _   _ _____ _____ __  __ ', 10
        db '| | | |_   _|  ___|  \/  |', 10
        db '| |_| | | | | |__ | |\/| |', 10
        db ' \___/  |_| |____||_|  |_|', 10, 10
        db '> CPU: Procesa los calculos del sistema', 10
        db '> Memoria: Almacena datos en ejecucion', 10
        db '> Bootloader: Carga el SO en la RAM', 0

; 5. Relleno y firma de arranque
times 510-($-$$) db 0
dw 0AA55H