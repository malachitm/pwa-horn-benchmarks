(set-option :pp.decimal true)
(set-logic HORN)
(declare-fun Inv (Real Real Real Real Real Real) Bool)

(assert (forall 
	((currentvalue Real)
	 (error Real) (controloutput Real)
	 (controlsignal Real) (init Real) (i Real)
	)

	(=>
		(and 
			(<= init 200.0)
			(>= init 0.0)
			(= currentvalue init)
			(= controlsignal 0.0)
			(= i 0)
		)
		( Inv currentvalue error controloutput controlsignal init i))
))

(assert (forall 
	((currentvalue Real)
	 (error Real) (controloutput Real)
	 (controlsignal Real) (init Real) (i Real)
	 (currentvalue0 Real)
	 (error0 Real) (controloutput0 Real)
	 (controlsignal0 Real) (init0 Real) (i0 Real)
	)

	(=> 
		(and
			( Inv currentvalue error controloutput controlsignal init i)
            
			(= error0 (- 100 currentvalue))
			(= controloutput0 (* 0.1 error0))
			(= controlsignal0 controloutput0)
			(= currentvalue0 (+ currentvalue controlsignal0))
			(= init0 init)
			(= i0 (+ i 1))
		)
		(Inv currentvalue0 error0 controloutput0 controlsignal0 init0 i0))
))

(assert (forall 
	((currentvalue Real)
	 (error Real) (controloutput Real)
	 (controlsignal Real) (init Real) (i Real)
	 (currentvalue0 Real)
	 (error0 Real) (controloutput0 Real)
	 (controlsignal0 Real) (init0 Real) (i0 Real)
	)

	(=> 
		(and
			( Inv currentvalue error controloutput controlsignal init i)

			(= error0 (- 100 currentvalue))
			(= controloutput0 (* 0.1 error0))
			(= controlsignal0 controloutput0)
			(= currentvalue0 (+ currentvalue controlsignal0))
			(= init0 init)
			(= i0 (+ i 1))
			(not (=> 
				(>= i0 200) 
				(and
					(<= (- 0 0.1) (- 100 currentvalue0)) (<= (- 100 currentvalue0) 0.1)
				)))
		)
		false)
))

(check-sat)
(get-model)