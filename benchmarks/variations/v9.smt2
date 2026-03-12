; v1.smt2
; + auxiliary statements of n (real) and r0
; - transition formula
; + closed forms of property variables
; + bounds of r
; + have property written in terms of r and n
(set-option :pp.decimal true)
(set-logic HORN)
(declare-fun Inv (Real Real) Bool)

(assert (forall 
	((r0 Real) (n Real))
	(=>
		(and
			; auxiliary statements
			(= n 0.0)
            (= r0 1.0)
		)
		( Inv n r0))
))

(assert (forall 
	((r0 Real) (n Real)
     (r00 Real) (n0 Real)
	)
	(=> 
		(and
			( Inv n r0)
			; auxiliay statements
			(< 0.0 r0) (<= r0 1.0) (<= 0.0 n); assumption
            (= n0 (+ n 1.0))
            (= r00 (* r0 0.9))
		)
		(Inv n0 r00))
))

(assert (forall 
	((r0 Real) (n Real))
	(=> 
		(and
			( Inv n r0)
			(not (=> 
				(>= n 200.0) 
				(and
					(<= (- 1.0) (- 100.0 (+ 100.0 (* (- 100.0) r00)))) (<= (- 100.0 (+ 100.0 (* (- 100.0) r00))) 1.0)
				)))
		)
		false)
))

(check-sat)
(get-model)