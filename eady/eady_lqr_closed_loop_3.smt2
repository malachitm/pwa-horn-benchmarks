;; Automatically generated 3D closed-loop LQR CHC for eady
;; Note: Singleton initialization applied (all states start exactly at 0.0)
(set-logic HORN)

(declare-fun Inv (Real Real Real) Bool)

;; 1. Initialization
(assert
  (forall ((x0 Real) (x1 Real) (x2 Real))
    (=>
      (and
        (= x0 0.0)
        (= x1 0.0)
        (= x2 0.0)
      )
      (Inv x0 x1 x2)
    )
  )
)

;; 2. Transition (Closed-Loop Affine Step)
(assert
  (forall ((x0 Real) (x1 Real) (x2 Real)
           (x0_next Real) (x1_next Real) (x2_next Real))
    (=>
      (and
        (Inv x0 x1 x2)

        (= x0_next (+ (* 0.954183 x0) (+ (* -0.019689 x1) (* -0.006851 x2))))
        (= x1_next (+ (* 0.000716 x0) (+ (* 0.956611 x1) (* -0.020851 x2))))
        (= x2_next (+ (* -0.013285 x0) (+ (* -0.000648 x1) (* 0.959718 x2))))
      )
      (Inv x0_next x1_next x2_next)
    )
  )
)

;; 3. Safety Query (Actuator Saturation > 12.0V or < -12.0V)
(assert
  (forall ((x0 Real) (x1 Real) (x2 Real))
    (=>
      (and
        (Inv x0 x1 x2)
        (or
          (> (+ (* -0.880480 x0) (+ (* -1.016870 x1) (* -1.133098 x2))) 12.0)
          (< (+ (* -0.880480 x0) (+ (* -1.016870 x1) (* -1.133098 x2))) -12.0)
        )
      )
      false
    )
  )
)

(check-sat)
(get-model)
