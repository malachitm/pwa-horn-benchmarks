(set-option :pp.decimal true)
(set-logic HORN)
(declare-fun Inv (Real Real Real) Bool)

(assert
    (forall ((x Real) (y Real) (i Real))
        (=>
            (and
                (= x 1.0)
                (= y 0.0)
                (= i 0.0))
            (Inv x y i))))

(assert
    (forall ((x Real) (y Real) (i Real)
             (x0 Real) (y0 Real) (i0 Real))
        (=>
            (and
                (Inv x y i)
                (= x0 (+ x (* (- 1.0) y)))
                (= y0 (+ x y))
                (= i0 (+ i 1.0)))
            (Inv x0 y0 i0))))

(assert
    (forall ((x Real) (y Real) (i Real)
             (x0 Real) (y0 Real) (i0 Real))
        (=>
            (and
                (Inv x y i)
                (= x0 (+ x (* (- 1.0) y)))
                (= y0 (+ x y))
                (= i0 (+ i 1.0))
                (not (<= (- 1000000.0) x0)))
            false)))

(check-sat)
(get-model)