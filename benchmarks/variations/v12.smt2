; v9.smt2
; + index "n" is Int
(set-option :pp.decimal true)
(set-logic HORN)
(declare-fun Inv (Real Real Int Real) Bool)

(assert (forall 
	((currentvalue Real) (i Real) (r0 Real) (n Real))
	(=>
		(and
			; auxiliary statements
			(= n 0)
            (= r0 1.0)

			; closed forms
			(= currentvalue (+ 100.0 (* (- 100.0) r0)))
			(= i (to_real n))
		)
		( Inv currentvalue i n r0))
))

(assert (forall 
	((currentvalue Real) (i Real)
	 (currentvalue0 Real) (i0 Real)
     (r0 Real) (n Int)
     (r00 Real) (n0 Int)
	)
	(=> 
		(and
			( Inv currentvalue i n r0)

			; bounds
			(< 0.0 r0) (<= r0 1.0) (<= 0.0 n)

			; auxiliay statements
            (= n0 (+ n 1))
            (= r00 (* r0 0.9))

			; closed forms
			(= i0 (to_real n0))
			(= currentvalue0 (+ 100.0 (* (- 100.0) r00)))
		)
		(Inv currentvalue0 i0 n0 r00))
))

(assert (forall 
	((currentvalue Real) (i Real) (r0 Real) (n Int))
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