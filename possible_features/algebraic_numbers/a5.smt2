(set-option :pp.decimal true)
(set-logic HORN)

;; Declare the invariant with 1 state variable: x1, plus the step counter i
(declare-fun Inv (Real Real) Bool)

;; 1. Base Case: Initial Conditions
(assert (forall 
    ((x1 Real) (i Real))

    (=>
        (and
            ;; Variable initialized between -5 and 5
            (<= (- 5.0) x1) (<= x1 5.0)
            (= i 0.0)
        )
        (Inv x1 i)
    )
))

;; 2. Inductive Step: Transition Relation based on a 1x1 Matrix
(assert (forall 
    ((x1 Real) (i Real)
     (x1_next Real) (i_next Real))

    (=> 
        (and
            (Inv x1 i)
            
            ;; Calculate the new term: -1 * x1
            (= x1_next (* (- 1.0) x1))
            
            (= i_next (+ i 1.0))
        )
        (Inv x1_next i_next)
    )
))

;; 3. Error State: Checking the Safety Property
(assert (forall 
    ((x1 Real) (i Real)
     (x1_next Real) (i_next Real))

    (=> 
        (and
            (Inv x1 i)
            
            (= x1_next (* (- 1.0) x1))
            (= i_next (+ i 1.0))
            
            ;; The safety property demands the new term is always between -5 and 5.
            ;; We assert the negation to trigger 'false' (the error state).
            (not (and (<= (- 5.0) x1_next) (<= x1_next 5.0)))
        )
        false
    )
))

(check-sat)
(get-model)