; v1.smt2
; + auxiliary statements for symbols n, r0, r1
; + switch i to sort int
(set-option :pp.decimal true)
(set-logic HORN)
(declare-fun Inv (Real Real Real Real Int Real Real Real) Bool)

(assert (forall 
	((currentvalue Real)
	 (error Real) (controloutput Real)
	 (controlsignal Real) (i Int) (r0 Real)
     (r1 Real) (n Real)
	)

	(=>
		(and
			(= currentvalue 0.0)
			(= controlsignal 0.0)
			(= i 0)
            (= r0 1.0)
            (= r1 1.0)
            (= n 1.0)
		)
		( Inv currentvalue error controloutput controlsignal i r0 r1 n))
))

(assert (forall 
	((currentvalue Real)
	 (error Real) (controloutput Real)
	 (controlsignal Real) (i Int)
	 (currentvalue0 Real)
	 (error0 Real) (controloutput0 Real)
	 (controlsignal0 Real) (i0 Int)
     (r0 Real) (r1 Real) (n Real)
     (r00 Real) (r10 Real) (n0 Real)
	)

	(=> 
		(and
			( Inv currentvalue error controloutput controlsignal i r0 r1 n)
            
			(= error0 (- 100.0 currentvalue))
			(= controloutput0 (* 0.1 error0))
			(= controlsignal0 controloutput0)
			(= currentvalue0 (+ currentvalue controlsignal0))
			(= i0 (+ i 1))
            (= n0 (+ n 1.0))
            (= r00 (* r0 (/ 9.0 10.0)))
            (= r10 (* r1 1.0))
		)
		(Inv currentvalue0 error0 controloutput0 controlsignal0 i0 r00 r10 n0))
))

(assert (forall 
	((currentvalue Real)
	 (error Real) (controloutput Real)
	 (controlsignal Real) (i Int)
	 (currentvalue0 Real)
	 (error0 Real) (controloutput0 Real)
	 (controlsignal0 Real) (i0 Int)
     (r0 Real) (r1 Real) (n Real)
     (r00 Real) (r10 Real) (n0 Real)
	)

	(=> 
		(and
			( Inv currentvalue error controloutput controlsignal i r0 r1 n)

			(= error0 (- 100.0 currentvalue))
			(= controloutput0 (* 0.1 error0))
			(= controlsignal0 controloutput0)
			(= currentvalue0 (+ currentvalue controlsignal0))
			(= i0 (+ i 1))
            (= n0 (+ n 1.0))
            (= r00 (* r0 (/ 9.0 10.0)))
            (= r10 (* r1 1.0))
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