// Box.asm  -  Mayank, K = 53
//
// While ANY key is pressed a black box is drawn; when the key is released
// the box is erased again.
//
// The box (all values come from K = 53):
//   top row     : 53
//   height      : 20 rows
//   width       : 16 * ((53 mod 4) + 1) = 32 pixels = 2 words, from the left edge
//
// Screen memory: one row = 32 words, one word = 16 pixels.
//   first word of row 53 = SCREEN + 32*53 = 16384 + 1696 = 18080

(LOOP)
    @KBD
    D=M
    @PRESSED
    D;JNE               // a key is pressed -> draw black

    @color
    M=0                 // no key -> "draw" white (this erases the box)
    @DRAW
    0;JMP

(PRESSED)
    @color
    M=-1                // -1 = sixteen 1-bits = 16 black pixels

(DRAW)
    @18080
    D=A
    @address
    M=D                 // address = first word of row 53

    @20
    D=A
    @rows
    M=D                 // rows left to draw = 20

(ROW)
    @color
    D=M                 // D = what to write (black or white)
    @address
    A=M                 // A = current word on the screen
    M=D                 // left word  = pixels 0..15
    A=A+1
    M=D                 // right word = pixels 16..31

    @32
    D=A
    @address
    M=D+M               // address = address + 32  (next row down)

    @rows
    MD=M-1              // one row less to draw
    @ROW
    D;JGT               // more rows left -> repeat

    @LOOP
    0;JMP               // check the keyboard again
