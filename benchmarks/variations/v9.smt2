; v1.smt2
; + auxiliary statements of n (real) and r0
; - transition formula
; + closed forms of property variables
; + bounds of r
(set-option :pp.decimal true)
(set-logic HORN)
(declare-fun Inv (Real Real Real Real) Bool)

(assert (forall 
	((currentvalue Real) (i Real) (r0 Real) (n Real))
	(=>
		(and
			; auxiliary statements
			(= n 0.0)
            (= r0 1.0)

			; closed forms
			(= currentvalue (+ 100.0 (* (- 100.0) r0)))
			(= i n)
			;(= i 0.0)
			;(= currentvalue 0.0)
		)
		( Inv currentvalue i n r0))
))

(assert (forall 
	((currentvalue Real) (i Real)
	 (currentvalue0 Real) (i0 Real)
     (r0 Real) (n Real)
     (r00 Real) (n0 Real)
	)
	(=> 
		(and
			( Inv currentvalue i n r0)
			; auxiliay statements
			(< 0.0 r0) (<= r0 1.0) (<= 0.0 n); assumption
            (= n0 (+ n 1.0))
            (= r00 (* r0 0.9))
			; closed forms
			(= i0 n0)
			(= currentvalue0 (+ 100.0 (* (- 100.0) r00)))
		)
		(Inv currentvalue0 i0 n0 r00))
))

(assert (forall 
	((currentvalue Real) (i Real) (r0 Real) (n Real))
	(=> 
		(and
			( Inv currentvalue i n r0)
			(not (=> 
				(>= i 200.0) 
				(and
					(<= (- 1.0) (- 100.0 currentvalue)) (<= (- 100.0 currentvalue) 1.0)
				)))
		)
		false)
))

(check-sat)
(get-model)