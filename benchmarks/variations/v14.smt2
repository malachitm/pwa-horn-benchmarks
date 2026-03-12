; v14.smt2
; + change index "n" to Real
(set-option :pp.decimal true)
(set-logic HORN)
(declare-fun Inv (Real Real Real Real Real) Bool)

(assert (forall 
	((currentvalue Real) (i Real) (r0 Real) (n Real) (cv_init Real))
	(=>
		(and
			; auxiliary statements
			(= n 0.0)
            (= r0 1.0)
            (= cv_init 0.0)

			; closed forms
            (= i n)
			(= currentvalue (+ 100.0 (* (+ (- 100.0) cv_init) r0)))
		)
		( Inv currentvalue i n r0 cv_init))
))

(assert (forall 
	((currentvalue Real) (i Real)
	 (currentvalue0 Real) (i0 Real)
     (r0 Real) (n Real)
     (r00 Real) (n0 Real)
     (cv_init Real)
	)
	(=> 
		(and
			( Inv currentvalue i n r0 cv_init)

			; bounds
			(< 0.0 r0) (<= r0 1.0) (<= 0.0 n)

			; auxiliay statements
            (= n0 (+ n 1.0))
            (= r00 (* r0 0.9))

			; closed forms
			(= i0 n0)
			(= currentvalue0 (+ 100.0 (* (+ (- 100.0) cv_init) r00)))
		)
		(Inv currentvalue0 i0 n0 r00 cv_init))
))

(assert (forall 
	((currentvalue Real) (i Real) (r0 Real) (n Real) (cv_init Real))
	(=> 
		(and
			( Inv currentvalue i n r0 cv_init)
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