(set-option :pp.decimal true)
(set-logic HORN)
(declare-fun Inv (Real Real Real) Bool)
; Kp, Ki, step_time, max_output, min_output, target_program are constant throughout program

(assert (forall 
	((currentvalue Real) (controloutput Real)
	 (controlsignal Real) (i Real)
	)

	(=>
		(and 
			(= currentvalue 40.0)
			(= i 0.0)
		)
		(Inv currentvalue controloutput i))
))

(assert (forall 
	((currentvalue Real) (controloutput Real) (i Real)
	 (currentvalue0 Real) (controloutput0 Real) (i0 Real)
	)

	(=> 
		(and
			( Inv currentvalue controloutput i)
			(= controloutput0 (* 0.2 (- 100 currentvalue)))
			(= currentvalue0 (+ currentvalue controloutput0))
			(= i0 (+ i 1))
		)
		(Inv currentvalue0 controloutput0 i0))
))

(assert (forall 
	((currentvalue Real) (controloutput Real) (i Real)
	 (currentvalue0 Real) (controloutput0 Real) (i0 Real)
	)

	(=> 
		(and
			( Inv currentvalue controloutput i)
			(= controloutput0 (* 0.2 (- 100 currentvalue)))
			(= currentvalue0 (+ currentvalue controloutput0))
			(= i0 (+ i 1))
			(not (=> 
				(>= i0 50) 
					(<= (abs (- 100 currentvalue0)) 0.5)
				))
		)
		false)
))

(check-sat)
(get-model)