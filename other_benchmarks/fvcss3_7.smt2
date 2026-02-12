; Modification of Figure 3.7 from Formal Verification of Control System Software (2019)
; In particular, it limits it in the sense that yd is fixed after the initial step, but
; expands it by having xp1 become a parameter instead of strictly 0.

(set-logic HORN)
(declare-fun Inv (Real Real Real Real Real Real) Bool)

(assert (forall 
	((xc1 Real) (xc2 Real) (xp1 Real)
	 (xp2 Real) (yd Real) (i Real)
	)

	(=>
		(and 
			(= xc1 0.0)
            (= xc2 0.0)
            (<= -0.5 xp1) (<= xp1 0.5)
            (= xp2 0.0)
            (<= -0.5 yd) (<= yd 0.5)
			(= i 0)
		)
		(Inv xc1 xc2 xp1 xp2 yd i))
))

(assert (forall 
	((xc1 Real) (xc2 Real) (xp1 Real)
	 (xp2 Real) (yd Real) (i Real)
     (xc10 Real) (xc20 Real) (xp10 Real)
	 (xp20 Real) (i0 Real)
	)

	(=> 
		(and
			(Inv xc1 xc2 xp1 xp2 yd i)
            ; xc1 = 0.499 * oxc1 - 0.05 * oxc2 + (oxp1 - yd)
            (= xc10 (+ (* 0.499 xc1) (* (- 0.05) xc2) (- xp1 yd)))
            ; xc2 = 0.01 * oxc1 + oxc2
            (= xc20 (+ (* 0.01 xc1) xc2))
            ; xp1 = 0.028224 * oxc1 + oxp1 + 0.01 * oxp2 - 0.064 * (oxp1 - yd)
            (= xp10 (+ (* 0.028224 xc1) xp1 (* 0.01 xp2) (* (- 0.064) (- xp1 yd))))
            ; xp2 = 5.6448 * oxc1 - 0.01 * oxp1 + oxp2 - 12.8 * (oxp1 - yd)
            (= xp20 (+ (* 5.6448 xc1) (* (- 0.01) xp1) xp2 (* (- 12.8) (- xp1 yd))))
			(= i0 (+ i 1.0))
		)
		(Inv xc10 xc20 xp10 xp20 yd i0))
))

(assert (forall 
	((xc1 Real) (xc2 Real) (xp1 Real)
	 (xp2 Real) (yd Real) (i Real)
     (xc10 Real) (xc20 Real) (xp10 Real)
	 (xp2 Real) (i0 Real)
	)

	(=> 
		(and
			(Inv xc1 xc2 xp1 xp2 yd i)
			;(not (<= (* xp1 xp1) 1.0))
            (not (=> 
				(>= i 150) 
				(and
					(<= (- 0 0.01) (- yd xp1)) (<= (- yd xp1) 0.01)
				)))
		)
		false)
))

(check-sat)
(get-model)