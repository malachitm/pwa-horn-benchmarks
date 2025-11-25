(set-option :pp.decimal true)
(set-logic HORN)
(declare-fun Inv (Real Real Real) Bool)

(assert (forall 
	((i Real) (s Real) (t Real)
	)

	(=>
		(and 
			(= t 1.0)
			(= s 1.0)
			(= i 0.0)
		)
		( Inv t s i))
))

(assert (forall 
	((i Real) (s Real) (t Real)
        (i0 Real) (s0 Real) (t0 Real)
        )
    
        (=> 
            (and
                ( Inv t s i)
                (= i0 (+ i 1.0))
                (= t0 (+ t 2.0))
                (= s0 (+ s (* t0 0.5)))
            )
            (Inv t0 s0 i0))
	))

(assert (forall 
	((i Real) (s Real) (t Real) (i0 Real) (s0 Real) (t0 Real))

	(=> 
		(and
            (and
                ( Inv t s i)
                
                (= i0 (+ i 1.0))
                (= t0 (+ t 2.0))
                (= s0 (+ s (* t0 0.5)))
                (not (=> (< i0 50.0) (< s0 100000000.0)))
            ))
		false)
))

(check-sat)
(get-model)