		ORG 0H 			;starting address/program start
		N EQU 12 		;defining N
		MOV R0, #40H	;starting memory location
		MOV R7, #N
		DEC R7
		DEC R7
		MOV R1, #0H
		MOV @R0, #0H
		INC R0
		MOV @R0, #01H
		MOV R2, #01H

FIB:	INC R0
		MOV A, R1
		ADD A, R2		;(n-1) + (n-2)
		MOV @R0, A		;Store in mem
		MOV B, R2
		MOV R1, B
		MOV R2, A
		DJNZ R7, FIB
		END
		
