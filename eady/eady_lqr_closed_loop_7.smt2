;; Automatically generated 7D closed-loop LQR CHC for eady
;; Note: Singleton initialization applied (all states start exactly at 0.0)
(set-logic HORN)

(declare-fun Inv (Real Real Real Real Real Real Real) Bool)

;; 1. Initialization
(assert
  (forall ((x0 Real) (x1 Real) (x2 Real) (x3 Real) (x4 Real) (x5 Real) (x6 Real))
    (=>
      (and
        (= x0 0.0)
        (= x1 0.0)
        (= x2 0.0)
        (= x3 0.0)
        (= x4 0.0)
        (= x5 0.0)
        (= x6 0.0)
      )
      (Inv x0 x1 x2 x3 x4 x5 x6)
    )
  )
)

;; 2. Transition (Closed-Loop Affine Step)
(assert
  (forall ((x0 Real) (x1 Real) (x2 Real) (x3 Real) (x4 Real) (x5 Real) (x6 Real)
           (x0_next Real) (x1_next Real) (x2_next Real) (x3_next Real) (x4_next Real) (x5_next Real) (x6_next Real))
    (=>
      (and
        (Inv x0 x1 x2 x3 x4 x5 x6)

        (= x0_next (+ (* 0.957333 x0) (+ (* -0.016280 x1) (+ (* -0.002398 x2) (+ (* -0.011302 x3) (+ (* -0.006800 x4) (+ (* -0.013146 x5) (* -0.012919 x6))))))))
        (= x1_next (+ (* 0.003865 x0) (+ (* 0.960021 x1) (+ (* -0.016398 x2) (+ (* -0.003833 x3) (+ (* -0.011994 x4) (+ (* -0.009200 x5) (* -0.016083 x6))))))))
        (= x2_next (+ (* -0.010135 x0) (+ (* 0.002761 x1) (+ (* 0.964171 x2) (+ (* -0.017833 x3) (+ (* -0.004524 x4) (+ (* -0.014394 x5) (* -0.012137 x6))))))))
        (= x3_next (+ (* -0.002666 x0) (+ (* -0.011240 x1) (+ (* 0.002642 x2) (+ (* 0.967256 x3) (+ (* -0.018525 x4) (+ (* -0.006925 x5) (* -0.017331 x6))))))))
        (= x4_next (+ (* -0.007860 x0) (+ (* -0.003770 x1) (+ (* -0.011358 x2) (+ (* 0.001207 x3) (+ (* 0.971047 x4) (+ (* -0.020925 x5) (* -0.009862 x6))))))))
        (= x5_next (+ (* -0.003914 x0) (+ (* -0.008964 x1) (+ (* -0.003889 x2) (+ (* -0.012793 x3) (+ (* 0.000516 x4) (+ (* 0.972814 x5) (* -0.023862 x6))))))))
        (= x6_next (+ (* -0.007078 x0) (+ (* -0.005018 x1) (+ (* -0.009083 x2) (+ (* -0.005324 x3) (+ (* -0.013485 x4) (+ (* -0.001884 x5) (* 0.973526 x6))))))))
      )
      (Inv x0_next x1_next x2_next x3_next x4_next x5_next x6_next)
    )
  )
)

;; 3. Safety Query (Actuator Saturation > 12.0V or < -12.0V)
(assert
  (forall ((x0 Real) (x1 Real) (x2 Real) (x3 Real) (x4 Real) (x5 Real) (x6 Real))
    (=>
      (and
        (Inv x0 x1 x2 x3 x4 x5 x6)
        (or
          (> (+ (* -0.565498 x0) (+ (* -0.675922 x1) (+ (* -0.687794 x2) (+ (* -0.831294 x3) (+ (* -0.900483 x4) (+ (* -1.140489 x5) (* -1.434206 x6))))))) 12.0)
          (< (+ (* -0.565498 x0) (+ (* -0.675922 x1) (+ (* -0.687794 x2) (+ (* -0.831294 x3) (+ (* -0.900483 x4) (+ (* -1.140489 x5) (* -1.434206 x6))))))) -12.0)
        )
      )
      false
    )
  )
)

(check-sat)
(get-model)
