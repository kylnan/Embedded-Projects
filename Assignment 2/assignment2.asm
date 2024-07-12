	;starting code
	;test cases are entered here
	ORG 00H
	LJMP MAIN

	ORG 30H
N1: DB "44" ;30H = 0x34H, 31H = 0x34H
	DB 0
N2: DB "28" ;33H = 0x32H, 34H = 0x38H
	DB 0
	 	
		
		;first instruction of the program
MAIN:   MOV DPTR, #N1 ;DPTR = N1
		MOV R0, #0H ;clearing all registers to ensure
		MOV R1, #0H ;no corrupted data
		MOV R3, #0H
		MOV R4, #0H
		;first loop that converts N1 from ASCII to decimal
LOOP1:  MOV A, #0H ;reading over the string and reading each char/byte
        MOVC A, @A+DPTR ;Loading N1 -> A ;ie 4 in ascii
        JZ INP2 ;A == 0? Read N2 
        SUBB A, #30H ;convert ascii to decimal, ie 4 from ascii to decimal 4
        MOV R4, A ;store read value into temp reg ie R4 = 4
        MOV A, R0 ;move running total into A ,ie if R0 is 1, A is now 1
        MOV B, #10 ;shift running total, ie if A was 1 it will become 10
        MUL AB    
        ADD A, R4 ;add read value to shifted running val, ie: 10 + 4 = 14
        MOV R0, A ;move the new running total to the reg for running total
        INC DPTR
        JNZ LOOP1

		;second loop that converts N2 from ASCII to decimal
INP2: 	MOV DPTR, #N2 ;DPTR = N2
LOOP2:  MOV A, #0H ;reading over the string and reading each char/byte
        MOVC A, @A+DPTR ;Loading N1 -> A ;ie 4 in ascii
        JZ MULT ;A == 0? Perform N1*N2 
        SUBB A, #30H ;convert ascii to decimal, ie 4 from ascii to decimal 4
        MOV R3, A ;store read value into temp reg for ex. R3 = 4
        MOV A, R1 ;move running total into A ,ie if R0 is 1, A is now 1
        MOV B, #10 ;shift running total, ie if A was 1 it will become 10
        MUL AB    
        ADD A, R3 ;add read value to shifted running val, ie: 10 + 4 = 14
        MOV R1, A ;move the new running total to the reg for running total
        INC DPTR
        JNZ LOOP2

MULT:	;performing N1*N2
		MOV A, #0H ;clearing to 
		MOV B, #0H ;ensure no corruption
		MOV A, R0  ;N1 converted to decimal -> A
		MOV B, R1  ;N2 converted to decimal -> B
		MUL AB	   ;AB = N1*N2
		MOV 50H, B ;storing B(MSB) into 50H
		MOV 51H, A ;storing A(LSB) into 51H
		
		END ;End Assembly
		JMP $;keeping exectuion here so PC doesn't continue
