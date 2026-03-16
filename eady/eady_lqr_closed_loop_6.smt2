;; Automatically generated 6D closed-loop LQR CHC for eady
;; Note: Singleton initialization applied (all states start exactly at 0.0)
(set-logic HORN)

(declare-fun Inv (Real Real Real Real Real Real) Bool)

;; 1. Initialization
(assert
  (forall ((x0 Real) (x1 Real) (x2 Real) (x3 Real) (x4 Real) (x5 Real))
    (=>
      (and
        (= x0 0.0)
        (= x1 0.0)
        (= x2 0.0)
        (= x3 0.0)
        (= x4 0.0)
        (= x5 0.0)
      )
      (Inv x0 x1 x2 x3 x4 x5)
    )
  )
)

;; 2. Transition (Closed-Loop Affine Step)
(assert
  (forall ((x0 Real) (x1 Real) (x2 Real) (x3 Real) (x4 Real) (x5 Real)
           (x0_next Real) (x1_next Real) (x2_next Real) (x3_next Real) (x4_next Real) (x5_next Real))
    (=>
      (and
        (Inv x0 x1 x2 x3 x4 x5)

        (= x0_next (+ (* 0.956568 x0) (+ (* -0.016806 x1) (+ (* -0.003474 x2) (+ (* -0.012058 x3) (+ (* -0.008422 x4) (* -0.015303 x5)))))))
        (= x1_next (+ (* 0.003100 x0) (+ (* 0.959494 x1) (+ (* -0.017474 x2) (+ (* -0.004589 x3) (+ (* -0.013616 x4) (* -0.011356 x5)))))))
        (= x2_next (+ (* -0.010901 x0) (+ (* 0.002234 x1) (+ (* 0.963096 x2) (+ (* -0.018590 x3) (+ (* -0.006147 x4) (* -0.016550 x5)))))))
        (= x3_next (+ (* -0.003432 x0) (+ (* -0.011766 x1) (+ (* 0.001566 x2) (+ (* 0.966500 x3) (+ (* -0.020148 x4) (* -0.009081 x5)))))))
        (= x4_next (+ (* -0.008626 x0) (+ (* -0.004297 x1) (+ (* -0.012434 x2) (+ (* 0.000451 x3) (+ (* 0.969424 x4) (* -0.023082 x5)))))))
        (= x5_next (+ (* -0.004679 x0) (+ (* -0.009491 x1) (+ (* -0.004965 x2) (+ (* -0.013550 x3) (+ (* -0.001107 x4) (* 0.970658 x5)))))))
      )
      (Inv x0_next x1_next x2_next x3_next x4_next x5_next)
    )
  )
)

;; 3. Safety Query (Actuator Saturation > 12.0V or < -12.0V)
(assert
  (forall ((x0 Real) (x1 Real) (x2 Real) (x3 Real) (x4 Real) (x5 Real))
    (=>
      (and
        (Inv x0 x1 x2 x3 x4 x5)
        (or
          (> (+ (* -0.642050 x0) (+ (* -0.728599 x1) (+ (* -0.795392 x2) (+ (* -0.906917 x3) (+ (* -1.062752 x4) (* -1.356144 x5)))))) 12.0)
          (< (+ (* -0.642050 x0) (+ (* -0.728599 x1) (+ (* -0.795392 x2) (+ (* -0.906917 x3) (+ (* -1.062752 x4) (* -1.356144 x5)))))) -12.0)
        )
      )
      false
    )
  )
)

(check-sat)
(get-model)
