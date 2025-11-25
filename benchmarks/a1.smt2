(set-logic HORN)
(declare-fun Inv (Real Real Real) Bool)

(assert (forall ((x Real) (y Real) (i Real)) 
    (=> 
        (and 
            (< -10.0 x) (< x 10.0)
            (< -10.0 y) (< y 10.0)
            (= i 0)
        )
        (Inv x y i)
    )
))

(assert (forall ((x Real) (y Real) (i Real) (x0 Real) (y0 Real) (i0 Real)) 
    (=> 
        (and 
            (Inv x y i)
            (= x0 (+ (* 0.81 x) (* -0.43 y)))
            (= y0 (+ (* 0.9 x) (* 0.223 y)))
            (= i0 (+ i 1.0))
        )
        (Inv x0 y0 i0)
    )
))

(assert (forall ((x Real) (y Real) (i Real) (x0 Real) (y0 Real) (i0 Real)) 
    (=> 
        (and 
            (Inv x y i)
            (= x0 (+ (* 0.81 x) (* -0.43 y)))
            (= y0 (+ (* 0.9 x) (* 0.223 y)))
            (= i0 (+ i 1.0))
            (not (=> 
                (> i0 200.0)
                (and (< -10.0 x0) (< x0 10.0)
                (< -10.0 y0) (< y0 10.0))
            ))
        )
        false
    )
))
(check-sat)
(get-model)