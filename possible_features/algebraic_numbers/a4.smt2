(set-option :pp.decimal true)
(set-logic HORN)

;; Declare the invariant with 2 variables: x1, x2, plus the step counter i
(declare-fun Inv (Real Real Real) Bool)

;; 1. Base Case: Initial Conditions
(assert (forall 
    ((x1 Real) (x2 Real) (i Real))

    (=>
        (and
            ;; Variables initialized between -1 and 1
            (<= (- 1.0) x1) (<= x1 1.0)
            (<= (- 1.0) x2) (<= x2 1.0)
            (= i 0.0)
        )
        (Inv x1 x2 i)
    )
))

;; 2. Inductive Step: Transition Relation based on the 2x2 Matrix
(assert (forall 
    ((x1 Real) (x2 Real) (i Real)
     (x1_next Real) (x2_next Real) (i_next Real))

    (=> 
        (and
            (Inv x1 x2 i)
            
            ;; Shift x1 up
            (= x1_next x2)
            
            ;; Calculate the new term: x2 - 0.5(x1)
            (= x2_next (+ x2 (* (- 0.5) x1)))
            
            (= i_next (+ i 1.0))
        )
        (Inv x1_next x2_next i_next)
    )
))

;; 3. Error State: Checking the Safety Property
(assert (forall 
    ((x1 Real) (x2 Real) (i Real)
     (x1_next Real) (x2_next Real) (i_next Real))

    (=> 
        (and
            (Inv x1 x2 i)
            
            (= x1_next x2)
            (= x2_next (+ x2 (* (- 0.5) x1)))
            (= i_next (+ i 1.0))
            
            ;; The safety property demands the new term is always between -10 and 10.
            ;; We assert the negation to trigger 'false' (the error state).
            (not (and (<= (- 10.0) x2_next) (<= x2_next 10.0)))
        )
        false
    )
))

(check-sat)
(get-model)