(set-option :pp.decimal true)
(set-logic HORN)
(declare-fun Inv (Real Real Real) Bool)

(assert (forall 
	((i Real) (x Real) (y Real)
	)

	(=>
		(and 
            (= x 2.0)
			(= y 3.0)
			(= i 0.0)
		)
		( Inv x y i))
))

(assert (forall 
	((i Real) (x Real) (y Real)
        (i0 Real) (x0 Real) (y0 Real)
        )
    
        (=> 
            (and
                ( Inv x y i)
                (= x0 (* x 100.0))
                (= y0 (* y 1.2))
                (= i0 (+ i 1.0))
            )
            (Inv x0 y0 i0))
	))

(assert (forall 
	((i Real) (x Real) (y Real)
        (i0 Real) (x0 Real) (y0 Real)
        )
    
        (=> 
            (and
                ( Inv x y i)
                (= x0 (* x 100.0))
                (= y0 (* y 1.2))
                (= i0 (+ i 1.0))
                (not (< x0 y0))
            )
            false)
	))

(check-sat)
(get-model)