(set-option :pp.decimal true)
(set-logic HORN)
(declare-fun Inv (Real Real Real Real Real Real) Bool)

(assert (forall 
	((currentvalue Real) (i Real) (n Real)
     (r0 Real) (r1 Real)
	)

	(=>
		(and 
			(= currentvalue 95.0)
			(= i 0.0)
            (= n 0.0)
            (= r0 1.0)
            (= r1 1.0)
		)
		( Inv currentvalue i n r0 r1))
))

(assert (forall 
	((currentvalue Real) (currentvalue0 Real)
    (i Real)(i0 Real) (n Real) (n0 Real) (r1 Real) (r0 Real)
    (r00 Real) (r10 Real)
	)

	(=> 
		(and
			( Inv currentvalue i n r0 r1)
			(= i0 (+ i 1.0))
            (and 
                (<= r00 (* (/ 1.0 2000.0) (+ 1799.0 190.7904611) r0)) 
                (<= (* (/ 1.0 2000.0) (+ 1799.0 190.7904610) r0) r00))
            (or
                (and 
                (<= r10 (* (- (/ 1.0 2000.0)) (+ (- 1799.0) 190.7904611) r1)) 
                (<= (* (- (/ 1.0 2000.0)) (+ (- 1799.0) 190.7904610) r1) r10))
                (and 
                (<= r10 (* (- (/ 1.0 2000.0)) (+ (- 1799.0) 190.7904610) r1)) 
                (<= (* (- (/ 1.0 2000.0)) (+ (- 1799.0) 190.7904611) r1) r10))
            )
            (= currentvalue0 )
		)
		(Inv currentvalue0 i0 n0 r00 r10))
))

(assert (forall 
	((currentvalue Real) (i Real) (n Real)
     (r0 Real) (r1 Real)
	)

	(=> 
		(and
			( Inv currentvalue i n r0 r1)
            (>= i 500) 
				(and
					(<= (- 0.2) (- 100 currentvalue)) (<= (- 100 currentvalue) 0.2)
				))
		false)
))

(check-sat)
(get-model)