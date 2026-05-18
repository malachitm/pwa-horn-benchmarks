(set-option :pp.decimal true)
(set-logic HORN)
(declare-fun Inv (Real Real) Bool)

(assert (forall 
	((x Real) (y Real))

	(=>
		(and
			(= x (- 5.0)) 
            (= y 0.0)
		)
		(Inv x y))
))

(assert (forall 
	( (x Real) (x0 Real) (y Real) (y0 Real))

	(=> 
		(and
			(Inv x y)
            ; loop condition
            (< x 5.0)

			; loop body
            (= y0 (ite (< x 0.0) (+ y x) (+ y (* 2.0 x))))
            (= x0 (+ x 1.0))
		)
		(Inv x0 y0))
))

(assert (forall 
	((x Real) (y Real))
	(=> 
		(and
			(Inv x y)

            ; exit condition
            (> x 5.0)

            ; negation of safety
            (not (= x y))
		)
		false)
))

(check-sat)
(get-model)