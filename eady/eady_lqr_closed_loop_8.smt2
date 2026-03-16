;; Automatically generated 8D closed-loop LQR CHC for eady
;; Note: Singleton initialization applied (all states start exactly at 0.0)
(set-logic HORN)

(declare-fun Inv (Real Real Real Real Real Real Real Real) Bool)

;; 1. Initialization
(assert
  (forall ((x0 Real) (x1 Real) (x2 Real) (x3 Real) (x4 Real) (x5 Real) (x6 Real) (x7 Real))
    (=>
      (and
        (= x0 0.0)
        (= x1 0.0)
        (= x2 0.0)
        (= x3 0.0)
        (= x4 0.0)
        (= x5 0.0)
        (= x6 0.0)
        (= x7 0.0)
      )
      (Inv x0 x1 x2 x3 x4 x5 x6 x7)
    )
  )
)

;; 2. Transition (Closed-Loop Affine Step)
(assert
  (forall ((x0 Real) (x1 Real) (x2 Real) (x3 Real) (x4 Real) (x5 Real) (x6 Real) (x7 Real)
           (x0_next Real) (x1_next Real) (x2_next Real) (x3_next Real) (x4_next Real) (x5_next Real) (x6_next Real) (x7_next Real))
    (=>
      (and
        (Inv x0 x1 x2 x3 x4 x5 x6 x7)

        (= x0_next (+ (* 0.957777 x0) (+ (* -0.015476 x1) (+ (* -0.001886 x2) (+ (* -0.010074 x3) (+ (* -0.006034 x4) (+ (* -0.011207 x5) (+ (* -0.010387 x6) (* -0.016731 x7)))))))))
        (= x1_next (+ (* 0.004309 x0) (+ (* 0.960824 x1) (+ (* -0.015887 x2) (+ (* -0.002605 x3) (+ (* -0.011228 x4) (+ (* -0.007261 x5) (+ (* -0.013552 x6) (* -0.014114 x7)))))))))
        (= x2_next (+ (* -0.009691 x0) (+ (* 0.003564 x1) (+ (* 0.964683 x2) (+ (* -0.016606 x3) (+ (* -0.003759 x4) (+ (* -0.012455 x5) (+ (* -0.009605 x6) (* -0.017279 x7)))))))))
        (= x3_next (+ (* -0.002222 x0) (+ (* -0.010436 x1) (+ (* 0.003154 x2) (+ (* 0.968483 x3) (+ (* -0.017760 x4) (+ (* -0.004985 x5) (+ (* -0.014799 x6) (* -0.013332 x7)))))))))
        (= x4_next (+ (* -0.007416 x0) (+ (* -0.002967 x1) (+ (* -0.010847 x2) (+ (* 0.002435 x3) (+ (* 0.971812 x4) (+ (* -0.018986 x5) (+ (* -0.007330 x6) (* -0.018526 x7)))))))))
        (= x5_next (+ (* -0.003470 x0) (+ (* -0.008161 x1) (+ (* -0.003378 x2) (+ (* -0.011566 x3) (+ (* 0.001281 x4) (+ (* 0.974753 x5) (+ (* -0.021331 x6) (* -0.011057 x7)))))))))
        (= x6_next (+ (* -0.006634 x0) (+ (* -0.004215 x1) (+ (* -0.008572 x2) (+ (* -0.004097 x3) (+ (* -0.012719 x4) (+ (* 0.000055 x5) (+ (* 0.976057 x6) (* -0.025058 x7)))))))))
        (= x7_next (+ (* -0.004018 x0) (+ (* -0.007379 x1) (+ (* -0.004625 x2) (+ (* -0.009291 x3) (+ (* -0.005250 x4) (+ (* -0.013946 x5) (+ (* -0.002290 x6) (* 0.975360 x7)))))))))
      )
      (Inv x0_next x1_next x2_next x3_next x4_next x5_next x6_next x7_next)
    )
  )
)

;; 3. Safety Query (Actuator Saturation > 12.0V or < -12.0V)
(assert
  (forall ((x0 Real) (x1 Real) (x2 Real) (x3 Real) (x4 Real) (x5 Real) (x6 Real) (x7 Real))
    (=>
      (and
        (Inv x0 x1 x2 x3 x4 x5 x6 x7)
        (or
          (> (+ (* -0.521106 x0) (+ (* -0.595605 x1) (+ (* -0.636668 x2) (+ (* -0.708570 x3) (+ (* -0.823915 x4) (+ (* -0.946583 x5) (+ (* -1.181061 x6) (* -1.553729 x7)))))))) 12.0)
          (< (+ (* -0.521106 x0) (+ (* -0.595605 x1) (+ (* -0.636668 x2) (+ (* -0.708570 x3) (+ (* -0.823915 x4) (+ (* -0.946583 x5) (+ (* -1.181061 x6) (* -1.553729 x7)))))))) -12.0)
        )
      )
      false
    )
  )
)

(check-sat)
(get-model)
