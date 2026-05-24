(set-option :pp.decimal true)
(set-logic HORN)

;; Declare the invariant with 6 variables: x1 through x5, plus the step counter i
(declare-fun Inv (Real Real Real Real Real Real) Bool)

;; 1. Base Case: Initial Conditions
(assert (forall 
    ((x1 Real) (x2 Real) (x3 Real) (x4 Real) (x5 Real) (i Real))

    (=>
        (and
            ;; Each of the 5 variables is initialized between -1 and 1
            (<= (- 1.0) x1) (<= x1 1.0)
            (<= (- 1.0) x2) (<= x2 1.0)
            (<= (- 1.0) x3) (<= x3 1.0)
            (<= (- 1.0) x4) (<= x4 1.0)
            (<= (- 1.0) x5) (<= x5 1.0)
            (= i 0.0)
        )
        (Inv x1 x2 x3 x4 x5 i)
    )
))

;; 2. Inductive Step: Transition Relation based on the 5x5 Matrix
(assert (forall 
    ((x1 Real) (x2 Real) (x3 Real) (x4 Real) (x5 Real) (i Real)
     (x1_next Real) (x2_next Real) (x3_next Real) (x4_next Real) (x5_next Real) (i_next Real))

    (=> 
        (and
            (Inv x1 x2 x3 x4 x5 i)
            
            ;; The top 4 rows of the matrix shift the values up
            (= x1_next x2)
            (= x2_next x3)
            (= x3_next x4)
            (= x4_next x5)
            
            ;; The bottom row computes the new 5th term using the polynomial coefficients
            ;; 6(x1) - 6(x2) - 5(x3) + 5(x4) + 1(x5)
            (= x5_next (+ (* 6.0 x1) (* (- 6.0) x2) (* (- 5.0) x3) (* 5.0 x4) x5))
            
            (= i_next (+ i 1.0))
        )
        (Inv x1_next x2_next x3_next x4_next x5_next i_next)
    )
))

;; 3. Error State: Checking the Safety Property
(assert (forall 
    ((x1 Real) (x2 Real) (x3 Real) (x4 Real) (x5 Real) (i Real)
     (x1_next Real) (x2_next Real) (x3_next Real) (x4_next Real) (x5_next Real) (i_next Real))

    (=> 
        (and
            (Inv x1 x2 x3 x4 x5 i)
            
            (= x1_next x2)
            (= x2_next x3)
            (= x3_next x4)
            (= x4_next x5)
            (= x5_next (+ (* 6.0 x1) (* (- 6.0) x2) (* (- 5.0) x3) (* 5.0 x4) x5))
            
            (= i_next (+ i 1.0))
            
            ;; The safety property demands that the 5th variable (x5) is always > -20.
            ;; We assert the negation of this property to trigger 'false' (the error state).
            (not (> x5_next (- 20.0)))
        )
        false
    )
))

(check-sat)
(get-model)