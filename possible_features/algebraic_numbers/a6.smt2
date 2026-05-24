(set-option :pp.decimal true)
(set-logic HORN)

;; Declare the invariant with 3 state variables and the step counter i
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
            (= i 0.0)
        )
        (Inv x1 x2 x3 i)
    )
))

;; 2. Inductive Step: Dense Matrix Transition
(assert (forall 
    ((x1 Real) (x2 Real) (x3 Real) (i Real)
     (x1_next Real) (x2_next Real) (x3_next Real) (i_next Real))

    (=> 
        (and
            (Inv x1 x2 x3 i)
            
            ;; Dense matrix multiplication
            (= x1_next (+ (* 0.3645 x1) (* (- 0.8225) x2) (* 3.348 x3)))
            (= x2_next (+ (* 0.3645 x1) (* (- 1.8225) x2) (* 4.348 x3)))
            (= x3_next (+ (* 0.3645 x1) (* (- 1.8225) x2) (* 3.348 x3)))
            
            (= i_next (+ i 1.0))
        )
        (Inv x1_next x2_next x3_next i_next)
    )
))

;; 3. Error State: Checking the Safety Property
(assert (forall 
    ((x1 Real) (x2 Real) (x3 Real) (i Real)
     (x1_next Real) (x2_next Real) (x3_next Real) (i_next Real))

    (=> 
        (and
            (Inv x1 x2 x3 i)
            
            (= x1_next (+ (* 0.3645 x1) (* (- 0.8225) x2) (* 3.348 x3)))
            (= x2_next (+ (* 0.3645 x1) (* (- 1.8225) x2) (* 4.348 x3)))
            (= x3_next (+ (* 0.3645 x1) (* (- 1.8225) x2) (* 3.348 x3)))
            
            (= i_next (+ i 1.0))
            
            ;; The safety property demands all variables stay within -20.0 and 20.0
            ;; We assert the negation to trigger 'false' (the error state).
            (not (and 
                (<= (- 20.0) x1_next) (<= x1_next 20.0)
                (<= (- 20.0) x2_next) (<= x2_next 20.0)
                (<= (- 20.0) x3_next) (<= x3_next 20.0)
            ))
        )
        false
    )
))

(check-sat)
(get-model)