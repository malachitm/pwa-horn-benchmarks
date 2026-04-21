(set-option :pp.decimal true)
(set-logic HORN)
(declare-fun Inv (Real Real Real Real Real) Bool)

(assert (forall 
	((currentvalue Real)
	 (error Real) (controloutput Real)
	 (controlsignal Real) (i Real)
	)

	(=>
		(and
			(<= 0.000000 currentvalue)
            (<= currentvalue 165.517241)
			(= i 0.0)
		)
		( Inv currentvalue error controloutput controlsignal i))
))

(assert (forall 
	((currentvalue Real)
	 (error Real) (controloutput Real)
	 (controlsignal Real) (i Real)
	 (currentvalue0 Real)
	 (error0 Real) (controloutput0 Real)
	 (controlsignal0 Real) (i0 Real)
	)

	(=> 
		(and
			( Inv currentvalue error controloutput controlsignal i)
            
			(= error0 (- 100.000000 currentvalue))
			(= controloutput0 (* 0.100000 error0))
			(= controlsignal0 controloutput0)
			(= currentvalue0 (+ currentvalue controlsignal0))
			(= i0 (+ i 1.0))
		)
		(Inv currentvalue0 error0 controloutput0 controlsignal0 i0))
))

(assert (forall 
	((currentvalue Real)
	 (error Real) (controloutput Real)
	 (controlsignal Real) (i Real)
	 (currentvalue0 Real)
	 (error0 Real) (controloutput0 Real)
	 (controlsignal0 Real) (i0 Real)
	)

	(=> 
		(and
			( Inv currentvalue error controloutput controlsignal i)

			(= error0 (- 100.000000 currentvalue))
			(= controloutput0 (* 0.100000 error0))
			(= controlsignal0 controloutput0)
			(= currentvalue0 (+ currentvalue controlsignal0))
			(= i0 (+ i 1.0))
			(not (=> 
				(>= i0 200.000000) 
				(and
					(<= (- 0.0 1.000000) (- 100.000000 currentvalue0)) (<= (- 100.000000 currentvalue0) 1.000000)
				)))
		)
		false)
))

(check-sat)
(get-model)
