(set-option :pp.decimal true)
(set-logic HORN)
(declare-fun Inv (Real) Bool)

(assert (forall ((i Real))
	(=>
		(and
			(= i 0.0)
            (<= i 100.0)        ; loop guard
		)
		( Inv i))
))

(assert (forall ((i Real) (i0 Real))
	(=> 
		(and
			( Inv i)
            (<= i 100.0)        ; loop guard
			(= i0 (+ i 1.0))    ; transition
		)
		(Inv i0))
))

(assert (forall ((i Real) (i0 Real))
	(=> 
		(and
			( Inv i)
			(> i 100.0)         ; loop guard
			(not (= i 101.0))   ; safety
		)
		false)
))

(check-sat)
(get-model)