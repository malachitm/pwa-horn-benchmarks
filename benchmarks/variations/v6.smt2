; v1.smt2
; + auxiliary statements of n (int) and r0
; - transition formula
; + closed forms of property variables
(set-option :pp.decimal true)
(set-logic HORN)
(declare-fun Inv (Real Real Int Real Real) Bool)

(assert (forall 
	((currentvalue Real) (i Real) 
	 (r0 Real) (n Int) (a0 Real))

	(=>
		(and
			(= 0 (+ (* a0 a0) (- 2)))
			(< 0 a0)
			(= currentvalue 0.0)
			(= i 0.0)
			; auxiliary statements
			(= n 1)
            (= r0 1.0)
		)
		( Inv currentvalue i n r0 a0))
))

(assert (forall 
	((currentvalue Real) (i Real)
	 (currentvalue0 Real) (i0 Real)
     (r0 Real) (n Int)
     (r00 Real) (n0 Int) (a0 Real)
	)

	(=> 
		(and
			( Inv currentvalue i n r0 a0)
			; auxiliay statements
            (= n0 (+ n 1))
            (= r00 (* r0 (/ 9.0 10.0)))
			; closed forms
			(= i0 (to_real n0))
			(= currentvalue0 (+ 100.0 (* (- 100.0) r00)))
		)
		(Inv currentvalue0 i0 n0 r00 a0))
))

(assert (forall 
	((currentvalue Real) (i Real)
	 (currentvalue0 Real) (i0 Real)
     (r0 Real) (n Int)
     (r00 Real) (n0 Int) (a0 Real)
	)

	(=> 
		(and
			( Inv currentvalue i n r0 a0)
			; auxiliary statements
            (= n0 (+ n 1))
            (= r00 (* r0 (/ 9.0 10.0)))
			; closed forms
			(= i0 (to_real n0))
			(= currentvalue0 (+ 100.0 (* (- 100.0) r00)))
			(not (=> 
				(>= i0 200.0) 
				(and
					(<= (- 1.0) (- 100.0 currentvalue0)) (<= (- 100.0 currentvalue0) 1.0)
				)))
		)
		false)
))

(check-sat)
(get-model)