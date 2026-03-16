(set-option :pp.decimal true)
; What this shows, to me, is that simply stating the relation between
; roots of two separate variables is enough to show inequalities between variables
(declare-fun x () Real)
(declare-fun y () Real)
(declare-fun i () Real)
(declare-fun xinit () Real)
(declare-fun yinit () Real)
(declare-fun r1 () Real)
(declare-fun r2 () Real)
(declare-fun i0 () Real)
(declare-fun x0 () Real)
(declare-fun y0 () Real)
(declare-fun r10 () Real)
(declare-fun r20 () Real)

(define-fun Inv ((a Real) (b Real) (c Real) (ainit Real) (binit Real) (r1 Real) (r2 Real)) Bool (and 
    (<= ainit binit)
    (>= binit 0.0)
    (>= r1 1.0)
    (>= r2 1.0)
    (<= r1 r2)
    (= a (* ainit r1))
    (= b (* binit r2))
    (<= a b)
))

; initiation
(push 1)
(assert (and 
    (<= x y)
	(>= y 0)
    (= xinit x)
    (= yinit y)
    (= r1 1.0)
    (= r2 1.0)
	(= i 0.0)
	(not ( Inv x y i xinit yinit r1 r2))
))
(check-sat)
(get-model)
(pop 1)

; consecution
(push 1)
(assert (and
    ( Inv x y i xinit yinit r1 r2)
    (= i0 (+ i 1.0))
    (= x0 (* x 1.5))
    (= y0 (* y 1.6))
    (= r10 (* r1 1.5))
    (= r20 (* r2 1.6))        
    (not (Inv x0 y0 i0 xinit yinit r10 r20))   
))
(check-sat)
(get-model)
(pop 1)

; query
(push 1)
(assert (and
    ( Inv x y i xinit yinit r1 r2)
    (= x0 (* x 1.5))
    (= y0 (* y 1.6))
    (= i0 (+ i 1.0))
    (= r10 (* r1 1.5))
    (= r20 (* r2 1.6))
    (not (<= x0 y0))
))

(check-sat)
(get-model)