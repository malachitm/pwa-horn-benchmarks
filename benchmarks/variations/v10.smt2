; v1.smt2
; + auxiliary statements of n (real) and r0
; - transition formula
; + closed forms of property variables
; + currentvalue in interval [0,200]
(set-option :pp.decimal true)
(set-logic HORN)
(declare-fun Inv (Real Real Real Real) Bool)

(assert (forall 
	((currentvalue Real) (i Real) 
	 (r0 Real) (n Real))

	(=>
		(and
			(<= currentvalue 200.0)
            (<= 0.0 currentvalue)
			(= i 0.0)
			; auxiliary statements
			(= n 1.0)
            (= r0 1.0)
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
            (= n0 (+ n 1.0))
            (= r00 (* r0 0.9))
			; closed forms
			(= i0 n0)
			(or 
                (and (<= currentvalue0 (+ 100.0 (* (- 100.0) r00)))
                (<= (+ 100.0 (* 100.0 r00)) currentvalue0))
                (and (<= currentvalue0 (+ 100.0 (* 100.0 r00)))
                (<= (+ 100.0 (* (- 100.0) r00)) currentvalue0))
            )
		)
		(Inv currentvalue0 i0 n0 r00))
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
			; auxiliary statements
            (= n0 (+ n 1.0))
            (= r00 (* r0 0.9))
			; closed forms
			(= i0 n0)
			(or 
                (and (<= currentvalue0 (+ 100.0 (* (- 100.0) r00)))
                (<= (+ 100.0 (* 100.0 r00)) currentvalue0))
                (and (<= currentvalue0 (+ 100.0 (* 100.0 r00)))
                (<= (+ 100.0 (* (- 100.0) r00)) currentvalue0))
            )
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