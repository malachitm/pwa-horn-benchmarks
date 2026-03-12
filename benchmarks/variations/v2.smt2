; v1.smt2
; + switch i to sort int
(set-option :pp.decimal true)
(set-logic HORN)
(declare-fun Inv (Real Real Real Real Int) Bool)

(assert (forall 
	((currentvalue Real)
	 (error Real) (controloutput Real)
	 (controlsignal Real) (i Int)
	)

	(=>
		(and
			(= currentvalue 0.0)
			(= controlsignal 0.0)
			(= i 0)
		)
		( Inv currentvalue error controloutput controlsignal i))
))

(assert (forall 
	((currentvalue Real)
	 (error Real) (controloutput Real)
	 (controlsignal Real) (i Int)
	 (currentvalue0 Real)
	 (error0 Real) (controloutput0 Real)
	 (controlsignal0 Real) (i0 Int)
	)

	(=> 
		(and
			( Inv currentvalue error controloutput controlsignal i)
            
			(= error0 (- 100.0 currentvalue))
			(= controloutput0 (* 0.1 error0))
			(= controlsignal0 controloutput0)
			(= currentvalue0 (+ currentvalue controlsignal0))
			(= i0 (+ i 1))
		)
		(Inv currentvalue0 error0 controloutput0 controlsignal0 i0))
))

(assert (forall 
	((currentvalue Real)
	 (error Real) (controloutput Real)
	 (controlsignal Real) (i Int)
	 (currentvalue0 Real)
	 (error0 Real) (controloutput0 Real)
	 (controlsignal0 Real) (i0 Int)
	)

	(=> 
		(and
			( Inv currentvalue error controloutput controlsignal i)

			(= error0 (- 100.0 currentvalue))
			(= controloutput0 (* 0.1 error0))
			(= controlsignal0 controloutput0)
			(= currentvalue0 (+ currentvalue controlsignal0))
			(= i0 (+ i 1))
			(not (=> 
				(>= i0 200) 
				(and
					(<= (- 1.0) (- 100.0 currentvalue0)) (<= (- 100.0 currentvalue0) 1.0)
				)))
		)
		false)
))

(check-sat)
(get-model)