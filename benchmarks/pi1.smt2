(set-option :pp.decimal true)
(set-logic HORN)
(declare-fun Inv (Real Real Real Real Real Real) Bool)

(assert (forall 
	((currentvalue Real)
	 (error Real) (integral Real) (controloutput Real)
	 (controlsignal Real) (i Real)
	)

	(=>
		(and 
			(= currentvalue 95.0)
			(= controlsignal 0.0)
			(= integral 0.0)
			(= i 0.0)
		)
		( Inv currentvalue error integral controloutput controlsignal i))
))

(assert (forall 
	((currentvalue Real)
	 (error Real) (integral Real) (controloutput Real)
	 (controlsignal Real) (i Real)
	 (currentvalue0 Real)
	 (error0 Real) (integral0 Real) (controloutput0 Real)
	 (controlsignal0 Real) (i0 Real)
	)

	(=> 
		(and
			( Inv currentvalue error integral controloutput controlsignal i)
			(= error0 (- 100 currentvalue))
			(= integral0 (+ integral (* error0 0.1)))
			(= controloutput0 (+ (* 2.0 error0) (* integral0 0.1)))
			(= controlsignal0 controloutput0)
			(= currentvalue0 (+ currentvalue (* controlsignal0 0.1)))
			(= i0 (+ i 1.0))
		)
		(Inv currentvalue0 error0 integral0 controloutput0 controlsignal0 i0))
))

(assert (forall 
	((currentvalue Real)
	 (error Real) (integral Real) (controloutput Real)
	 (controlsignal Real) (i Real)
	 (currentvalue0 Real)
	 (error0 Real) (integral0 Real) (controloutput0 Real)
	 (controlsignal0 Real) (i0 Real)
	)

	(=> 
		(and
			( Inv currentvalue error integral controloutput controlsignal i)
			(= error0 (- 100 currentvalue))
			(= integral0 (+ integral (* error0 0.1)))
			(= controloutput0 (+ (* 2.0 error0) (* integral0 0.1)))
			(= controlsignal0 controloutput0)
			(= currentvalue0 (+ currentvalue (* controlsignal0 0.1)))
			(= i0 (+ i 1.0))
			(not (=> 
				(>= i0 500) 
				(and
					(<= (- 0 0.2) (- 10 currentvalue0)) (<= (- 10 currentvalue0) 0.2)
				)))
		)
		false)
))

(check-sat)
(get-model)