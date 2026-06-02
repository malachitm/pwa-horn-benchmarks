(set-option :pp.decimal true)
(set-logic HORN)

;; Declare the invariant with only the 3 state variables
(declare-fun Inv (Real Real Real) Bool)

;; 1. Base Case: Initial Conditions
(assert (forall 
    ((x1 Real) (x2 Real) (x3 Real))

    (=>
        (and
            ;; Initialized between -1.0 and 1.0
            (<= (- 1.0) x1) (<= x1 1.0)
            (<= (- 1.0) x2) (<= x2 1.0)
            (<= (- 1.0) x3) (<= x3 1.0)
        )
        (Inv x1 x2 x3)
    )
))

;; 2. Inductive Step: Dense Matrix Transition
(assert (forall 
    ((x1 Real) (x2 Real) (x3 Real)
     (x1_next Real) (x2_next Real) (x3_next Real))

    (=> 
        (and
            (Inv x1 x2 x3)
            
            ;; Dense matrix multiplication
            (= x1_next (+ (* 0.3645 x1) (* (- 0.8225) x2) (* 3.348 x3)))
            (= x2_next (+ (* 0.3645 x1) (* (- 1.8225) x2) (* 4.348 x3)))
            (= x3_next (+ (* 0.3645 x1) (* (- 1.8225) x2) (* 3.348 x3)))
        )
        (Inv x1_next x2_next x3_next)
    )
))

;; 3. Error State: Checking the Safety Property
(assert (forall 
    ((x1 Real) (x2 Real) (x3 Real))

    (=> 
        (and
            (Inv x1 x2 x3)
            
            ;; The safety property demands all variables stay within -20.0 and 20.0
            ;; We assert the negation to trigger 'false' (the error state).
            (not (and 
                (<= (- 20.0) x1) (<= x1 20.0)
                (<= (- 20.0) x2) (<= x2 20.0)
                (<= (- 20.0) x3) (<= x3 20.0)
            ))
        )
        false
    )
))

(check-sat)
(get-model)