(set-option :pp.decimal true)
(set-logic HORN)
(declare-fun Inv (Real Real Real) Bool)

(assert (forall 
	((i Real) (x Real) (y Real))

	(=>
		(and 
            (<= x 10.0)
			(>= y 11.0)
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
                (= i0 (+ i 1.0))
                (= x0 (* x 1.5))
                (= y0 (* y 1.6))
            )
            (Inv x0 y0 i0))
        )
)

(assert (forall 
	((i Real) (x Real) (y Real)
        (i0 Real) (x0 Real) (y0 Real))
        
        (=> 
            (and
                ( Inv x y i)
                (= x0 (* x 1.5))
                (= y0 (* y 1.6))
                (= i0 (+ i 1.0))
                (not (<= x0 y0))
            )
            false)
	))

(check-sat)
(get-model)