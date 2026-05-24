(set-option :pp.decimal true)
(set-logic HORN)

;; Declare the invariant with 3 state variables and the step counter i
(declare-fun Inv (Real Real Real Real) Bool)

;; 1. Base Case: Initial Conditions
(assert (forall 
    ((x1 Real) (x2 Real) (x3 Real) (i Real))

    (=>
        (and
            ;; Initialized anywhere within a 1x1x1 box
            (<= 0.0 x1) (<= x1 1.0)
            (<= 0.0 x2) (<= x2 1.0)
            (<= 0.0 x3) (<= x3 1.0)
            (= i 0.0)
        )
        (Inv x1 x2 x3 i)
    )
))

;; 2. Inductive Step: Dense Matrix Transition (Undamped Oscillation)
(assert (forall 
    ((x1 Real) (x2 Real) (x3 Real) (i Real)
     (x1_next Real) (x2_next Real) (x3_next Real) (i_next Real))

    (=> 
        (and
            (Inv x1 x2 x3 i)
            
            ;; The exact dense matrix multiplication
            (= x1_next (+ (* 0.62 x1) (* 0.36 x2) (* (- 0.06) x3)))
            (= x2_next (+ (* (- 1.20) x1) (* 1.40 x2) (* 0.60 x3)))
            (= x3_next (+ (* 0.84 x1) (* (- 0.48) x2) (* 0.08 x3)))
            
            (= i_next (+ i 1.0))
        )
        (Inv x1_next x2_next x3_next i_next)
    )
))

;; 3. Error State: The Relational Hyperplane
(assert (forall 
    ((x1 Real) (x2 Real) (x3 Real) (i Real)
     (x1_next Real) (x2_next Real) (x3_next Real) (i_next Real))

    (=> 
        (and
            (Inv x1 x2 x3 i)
            
            (= x1_next (+ (* 0.62 x1) (* 0.36 x2) (* (- 0.06) x3)))
            (= x2_next (+ (* (- 1.20) x1) (* 1.40 x2) (* 0.60 x3)))
            (= x3_next (+ (* 0.84 x1) (* (- 0.48) x2) (* 0.08 x3)))
            
            (= i_next (+ i 1.0))
            
            ;; The safety property demands that (x1 - x2 + x3) is always <= 6.0
            ;; We assert the negation to trigger 'false' (the error state).
            (not (<= (+ x1_next (- x2_next) x3_next) 6.0))
        )
        false
    )
))

(check-sat)
(get-model)