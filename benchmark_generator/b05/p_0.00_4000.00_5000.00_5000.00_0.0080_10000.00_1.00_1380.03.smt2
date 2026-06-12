(set-option :pp.decimal true)
(set-logic HORN)
(declare-fun Inv (Real Real Real Real) Bool)

(assert (forall 
	((currentvalue Real)
	 (error Real) 
	 (controlsignal Real) (i Real)
	)

	(=>
		(and
			(<= 0.000000 currentvalue) (<= currentvalue 4000.000000)
			(= i 0.0)
		)
		( Inv currentvalue error controlsignal i))
))

(assert (forall 
	((currentvalue Real) (error Real) 
	 (controlsignal Real) (i Real)
	 (currentvalue0 Real) (error0 Real) 
	 (controlsignal0 Real) (i0 Real)
	)

	(=> 
		(and
			( Inv currentvalue error controlsignal i)
			(= error0 (- 10000.0 currentvalue))
			(= controlsignal0 (* 0.008000 error0))
			(= currentvalue0 (+ currentvalue controlsignal0))
			(= i0 (+ i 1.0))
		)
		(Inv currentvalue0 error0 controlsignal0 i0))
))

(assert (forall 
	((currentvalue Real) (error Real)
	 (controlsignal Real) (i Real)
	)

	(=> 
		(and
			( Inv currentvalue error controlsignal i)
			(not (=> 
				(>= i 10000.000000) 
				(and
					(<= (- 0.0 1380.034483) (- 10000.0 currentvalue)) (<= (- 10000.0 currentvalue) 1380.034483)
				)))
		)
		false)
))

(check-sat)
(get-model)
