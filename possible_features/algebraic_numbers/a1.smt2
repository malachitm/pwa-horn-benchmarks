(set-option :pp.decimal true)
(set-logic HORN)

;; Declare the invariant with 10 variables: x1 through x9, plus the step counter i
(declare-fun Inv (Real Real Real Real Real Real Real Real Real Real) Bool)

;; 1. Base Case: Initial Conditions
(assert (forall 
    ((x1 Real) (x2 Real) (x3 Real) (x4 Real) (x5 Real) 
     (x6 Real) (x7 Real) (x8 Real) (x9 Real) (i Real))

    (=>
        (and
            ;; Each of the 9 variables is initialized between -1 and 1
            (<= (- 1.0) x1) (<= x1 1.0)
            (<= (- 1.0) x2) (<= x2 1.0)
            (<= (- 1.0) x3) (<= x3 1.0)
            (<= (- 1.0) x4) (<= x4 1.0)
            (<= (- 1.0) x5) (<= x5 1.0)
            (<= (- 1.0) x6) (<= x6 1.0)
            (<= (- 1.0) x7) (<= x7 1.0)
            (<= (- 1.0) x8) (<= x8 1.0)
            (<= (- 1.0) x9) (<= x9 1.0)
            (= i 0.0)
        )
        (Inv x1 x2 x3 x4 x5 x6 x7 x8 x9 i)
    )
))

;; 2. Inductive Step: Transition Relation based on the 9x9 Companion Matrix
(assert (forall 
    ((x1 Real) (x2 Real) (x3 Real) (x4 Real) (x5 Real) 
     (x6 Real) (x7 Real) (x8 Real) (x9 Real) (i Real)
     (x1_next Real) (x2_next Real) (x3_next Real) (x4_next Real) (x5_next Real) 
     (x6_next Real) (x7_next Real) (x8_next Real) (x9_next Real) (i_next Real))

    (=> 
        (and
            (Inv x1 x2 x3 x4 x5 x6 x7 x8 x9 i)
            
            ;; The top 8 rows of the matrix simply shift the values
            (= x1_next x2)
            (= x2_next x3)
            (= x3_next x4)
            (= x4_next x5)
            (= x5_next x6)
            (= x6_next x7)
            (= x7_next x8)
            (= x8_next x9)
            
            ;; The bottom row computes the new 9th term
            (= x9_next (+ (* (- 21.0) x1) (* 19.0 x2) (* (- 7.0) x4)))
            
            (= i_next (+ i 1.0))
        )
        (Inv x1_next x2_next x3_next x4_next x5_next x6_next x7_next x8_next x9_next i_next)
    )
))

;; 3. Error State: Checking the Time-Bounded Safety Property
(assert (forall 
    ((x1 Real) (x2 Real) (x3 Real) (x4 Real) (x5 Real) 
     (x6 Real) (x7 Real) (x8 Real) (x9 Real) (i Real)
     (x1_next Real) (x2_next Real) (x3_next Real) (x4_next Real) (x5_next Real) 
     (x6_next Real) (x7_next Real) (x8_next Real) (x9_next Real) (i_next Real))

    (=> 
        (and
            (Inv x1 x2 x3 x4 x5 x6 x7 x8 x9 i)
            
            (= x1_next x2)
            (= x2_next x3)
            (= x3_next x4)
            (= x4_next x5)
            (= x5_next x6)
            (= x6_next x7)
            (= x7_next x8)
            (= x8_next x9)
            (= x9_next (+ (* (- 21.0) x1) (* 19.0 x2) (* (- 7.0) x4)))
            
            (= i_next (+ i 1.0))
            
            ;; The safety property demands that for the first 5 steps, the new term is bounded by -50 and 50.
            ;; We assert the negation of this property to trigger 'false' (the error state).
            (not (=> (<= i_next 5.0) (and (<= (- 50.0) x9_next) (<= x9_next 50.0))))
        )
        false
    )
))

(check-sat)
(get-model)