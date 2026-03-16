;; Automatically generated 2D closed-loop LQR CHC for eady
;; Note: Singleton initialization applied (all states start exactly at 0.0)
(set-logic HORN)

(declare-fun Inv (Real Real) Bool)

;; 1. Initialization
(assert
  (forall ((x0 Real) (x1 Real))
    (=>
      (and
        (= x0 0.0)
        (= x1 0.0)
      )
      (Inv x0 x1)
    )
  )
)

;; 2. Transition (Closed-Loop Affine Step)
(assert
  (forall ((x0 Real) (x1 Real)
           (x0_next Real) (x1_next Real))
    (=>
      (and
        (Inv x0 x1)

        (= x0_next (+ (* 0.952962 x0) (* -0.020970 x1)))
        (= x1_next (+ (* -0.000506 x0) (* 0.955331 x1)))
      )
      (Inv x0_next x1_next)
    )
  )
)

;; 3. Safety Query (Actuator Saturation > 12.0V or < -12.0V)
(assert
  (forall ((x0 Real) (x1 Real))
    (=>
      (and
        (Inv x0 x1)
        (or
          (> (+ (* -1.002606 x0) (* -1.144928 x1)) 12.0)
          (< (+ (* -1.002606 x0) (* -1.144928 x1)) -12.0)
        )
      )
      false
    )
  )
)

(check-sat)
(get-model)
