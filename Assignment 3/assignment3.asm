ORG 0H

;pin setup
	E EQU P3.1			;LCD E = P3.1
	RS EQU P3.3			;LCD RS = P3.3	
;set motor control (forward)
	SETB P3.0
	CLR  P3.2
;timer/counter setup
	MOV TMOD, #51H		;put timer 1 in event counting mode, timer 0 mode 1

;LCD Config
;initialize the display
	CLR RS				;clear RS - indicates that instructions are being sent to the module
	MOV P1, #38H		;0011 1000 Set Interface data length to 8 bits, 2 line, 5x7 font
	CALL PulseE
;entry mode set
	MOV P1, #06H		;set increment with no shift
	CALL PulseE			;send instructions to module
;display on/off control
	MOV P1, #0FH		;0000 1111 display on, the cursor is on and blinking is on
	Call PulseE

;send data
MAIN:
	CLR   TR0			;timer off
	CLR   TR1			;counter off
	MOV	  TH1, #0		;
	MOV   TL1, #0		;counter = 0
	CLR   P3.5			;external counter = 0
;initialize LCD
CLR RS
MOV P1, #01H
CALL PULSEE

;initialize registers
	MOV R1, #0 			;index
	MOV R2, #0 			;overflow
	MOV R3, #0 			;digit - most significant
	MOV R4, #0 			;digit
	MOV R5, #0 			;digit
	MOV R6, #0 			;digit
	MOV R7, #0 			;digit - least significant
;get count for 2.5 ms
	ACALL COUNT 		;go to count subroutine
;multiply count by 4 (add 2 0s later)
	MOV A, TL1 			;revolution count
	MOV B, #4
	MUL AB
	MOV R2, B 			;store overflow
;convert A from hex to decimal into one register
	MOV B, #10
	DIV AB
	MOV R5, B
	MOV B, #10
	DIV AB
	MOV R4, B
	MOV R3, A
;add 256 if R2<0
	MOV A, R2
	JZ DISPLAY
ADD256:
	MOV A, R5 			;least significant digit
	ADD A, #6 			;add 6
	CJNE A, #9H, CHECK1	;checks if sum=9
	JMP SECONDDIGIT 	;if equal to 9, jump
CHECK1:
	JC LESS1
	SUBB A, #10 		;if sum>9
	MOV R5, A
	INC R4
	JMP SECONDDIGIT
LESS1: 					;if sum<9
	MOV R5, A
SECONDDIGIT: 			;2nd digit
	MOV A, R4
	ADDC A, #5 			;add 5
	CJNE A, #09H,CHECK2 ;checks if sum=9
	JMP THIRDDIGIT 		;if equal to 9, jump
CHECK2:
	JC LESS2 			;if less than
	SUBB A, #10 		;if sum>9
	MOV R4, A
	INC R3
	JMP THIRDDIGIT
LESS2: 					;if sum<9
	MOV R4, A
THIRDDIGIT:
	MOV A, R3
	ADDC A, #2
	MOV R3, A
	DJNZ R2, ADD256

;display on LCD panel
DISPLAY:
	SETB RS 			;data send to module
	MOV R1, #5 			;sends 5 digits
	MOV R0, #3 			;starts sending from R3
LOOP:
	MOV A, @R0
	ADD A, #30H
	CALL sendChar
	INC R0
	DJNZ R1, LOOP

	SJMP MAIN			;jump back to the beginning of the program and restart

;function library
COUNT:
	MOV TL0, #32H 		;
	MOV TH0, #0F6H 		;timer counts up to
	SETB TR1		 	;start counter
	SETB P3.5		 	;start counter?
	SETB TR0 			;starts timer 0
HERE:
	JNB TF0, HERE 		;repeat for 500 us
	CLR P3.5 			;increment TL1 if P3.5=0
	CLR TF0 			;stops timer 0
	RET
sendChar:
	MOV P1, A
	Call PulseE
	RET
delay:
	MOV R7, #50		;loop for 50 cycles
	DJNZ R7, $		;$ means same address
	RET				;return to function call
PulseE:
	SETB E
	CLR  E
	CALL delay
	RET
clearTimer:
	CLR A						; reset revolution count in A to zero
	CLR TR1						; stop timer 1
	MOV TL1, #0					; reset timer 1 low byte to zero
	SETB TR1					; start timer 1
	RET							; return from subroutine
