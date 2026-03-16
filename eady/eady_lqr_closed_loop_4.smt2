;; Automatically generated 4D closed-loop LQR CHC for eady
;; Note: Singleton initialization applied (all states start exactly at 0.0)
(set-logic HORN)

(declare-fun Inv (Real Real Real Real) Bool)

;; 1. Initialization
(assert
  (forall ((x0 Real) (x1 Real) (x2 Real) (x3 Real))
    (=>
      (and
        (= x0 0.0)
        (= x1 0.0)
        (= x2 0.0)
        (= x3 0.0)
      )
      (Inv x0 x1 x2 x3)
    )
  )
)

;; 2. Transition (Closed-Loop Affine Step)
(assert
  (forall ((x0 Real) (x1 Real) (x2 Real) (x3 Real)
           (x0_next Real) (x1_next Real) (x2_next Real) (x3_next Real))
    (=>
      (and
        (Inv x0 x1 x2 x3)

        (= x0_next (+ (* 0.955025 x0) (+ (* -0.018534 x1) (+ (* -0.005464 x2) (* -0.015027 x3)))))
        (= x1_next (+ (* 0.001557 x0) (+ (* 0.957766 x1) (+ (* -0.019464 x2) (* -0.007558 x3)))))
        (= x2_next (+ (* -0.012443 x0) (+ (* 0.000506 x1) (+ (* 0.961105 x2) (* -0.021558 x3)))))
        (= x3_next (+ (* -0.004974 x0) (+ (* -0.013494 x1) (+ (* -0.000424 x2) (* 0.963531 x3)))))
      )
      (Inv x0_next x1_next x2_next x3_next)
    )
  )
)

;; 3. Safety Query (Actuator Saturation > 12.0V or < -12.0V)
(assert
  (forall ((x0 Real) (x1 Real) (x2 Real) (x3 Real))
    (=>
      (and
        (Inv x0 x1 x2 x3)
        (or
          (> (+ (* -0.796290 x0) (+ (* -0.901391 x1) (+ (* -0.994407 x2) (* -1.203802 x3)))) 12.0)
          (< (+ (* -0.796290 x0) (+ (* -0.901391 x1) (+ (* -0.994407 x2) (* -1.203802 x3)))) -12.0)
        )
      )
      false
    )
  )
)

(check-sat)
(get-model)
