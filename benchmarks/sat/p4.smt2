(set-option :pp.decimal true)
(set-logic HORN)
(declare-fun Inv (Real Real) Bool)

(assert (forall 
	((currentvalue Real) (i Real))
	(=>
		(and 
			(= currentvalue -20.0)
			(= i 0.0)
		)
		(Inv currentvalue i))
))

(assert (forall 
	((currentvalue Real) (i Real)
	 (currentvalue0 Real) (i0 Real)
	)

	(=> 
		(and
			( Inv currentvalue i)
			(= i0 (+ i 1))
			(= currentvalue0 (+ currentvalue (* 0.09 (- 100 currentvalue))))
		)
		(Inv currentvalue0 i0))
))

(assert (forall 
	((currentvalue Real) (i Real)
	 (currentvalue0 Real)  (i0 Real)
	)

	(=> 
		(and
			( Inv currentvalue i)
			(= i0 (+ i 1))
			(= currentvalue0 (+ currentvalue (* 0.09 (- 100 currentvalue))))
			(not (=> 
				(>= i0 500) (and
					(<= (- 0 0.1) (- 100 currentvalue0)) (<= (- 100 currentvalue0) 0.1)
				)))
		)
		false)
))

(check-sat)
(get-model)