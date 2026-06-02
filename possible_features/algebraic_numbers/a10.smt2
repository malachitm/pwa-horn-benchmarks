(set-option :pp.decimal true)
(set-logic HORN)

(declare-fun Inv (Real Real Real Real) Bool)

;; 1. Base Case: Initial Conditions
(assert (forall 
    ((x1 Real) (x2 Real) (x3 Real) (i Real))

    (=>
        (and
            ;; Initialized between -1.0 and 1.0
            (<= (- 1.0) x1) (<= x1 1.0)
            (<= (- 1.0) x2) (<= x2 1.0)
            (<= (- 1.0) x3) (<= x3 1.0)
            (= i 1.0)
        )
        (Inv x1 x2 x3 i)
    )
))

;; 2. Inductive Step: Non-Normal Matrix Transition
(assert (forall 
    ((x1 Real) (x2 Real) (x3 Real) (i Real)
     (x1_next Real) (x2_next Real) (x3_next Real) (i_next Real))

    (=> 
        (and
            (Inv x1 x2 x3 i)
            
            ;; Transient Growth Matrix
            ;; Eigenvalues are 0.7 (guarantees eventual convergence to 0)
            ;; The large 2.0 off-diagonal weights drive the initial expansion
            (= x1_next (+ (* 0.7 x1) (* 2.0 x2) (* 0.0 x3)))
            (= x2_next (+ (* 0.0 x1) (* 0.7 x2) (* 2.0 x3)))
            (= x3_next (+ (* 0.0 x1) (* 0.0 x2) (* 0.7 x3)))
            (= i_next (+ i 1.0))
        )
        (Inv x1_next x2_next x3_next i_next)
    )
))

;; 3. Error State: Checking the Safety Property
(assert (forall 
    ((x1 Real) (x2 Real) (x3 Real) (i Real))

    (=> 
        (and
            (Inv x1 x2 x3 i)
            
            ;; The safety property demands all variables stay within -20.0 and 20.0
            (not 
                (=> (> i 0.0) 
                    (and 
                    (<= (- 20.0) x1) (<= x1 20.0)
                    (<= (- 20.0) x2) (<= x2 20.0)
                    (<= (- 20.0) x3) (<= x3 20.0))
            ))
        )
        false
    )
))

(check-sat)
(get-model)