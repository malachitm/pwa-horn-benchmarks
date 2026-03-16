;; Automatically generated 5D closed-loop LQR CHC for eady
;; Note: Singleton initialization applied (all states start exactly at 0.0)
(set-logic HORN)

(declare-fun Inv (Real Real Real Real Real) Bool)

;; 1. Initialization
(assert
  (forall ((x0 Real) (x1 Real) (x2 Real) (x3 Real) (x4 Real))
    (=>
      (and
        (= x0 0.0)
        (= x1 0.0)
        (= x2 0.0)
        (= x3 0.0)
        (= x4 0.0)
      )
      (Inv x0 x1 x2 x3 x4)
    )
  )
)

;; 2. Transition (Closed-Loop Affine Step)
(assert
  (forall ((x0 Real) (x1 Real) (x2 Real) (x3 Real) (x4 Real)
           (x0_next Real) (x1_next Real) (x2_next Real) (x3_next Real) (x4_next Real))
    (=>
      (and
        (Inv x0 x1 x2 x3 x4)

        (= x0_next (+ (* 0.955958 x0) (+ (* -0.017783 x1) (+ (* -0.004239 x2) (+ (* -0.013456 x3) (* -0.010256 x4))))))
        (= x1_next (+ (* 0.002490 x0) (+ (* 0.958518 x1) (+ (* -0.018239 x2) (+ (* -0.005987 x3) (* -0.015450 x4))))))
        (= x2_next (+ (* -0.011511 x0) (+ (* 0.001258 x1) (+ (* 0.962330 x2) (+ (* -0.019987 x3) (* -0.007981 x4))))))
        (= x3_next (+ (* -0.004042 x0) (+ (* -0.012743 x1) (+ (* 0.000801 x2) (+ (* 0.965102 x3) (* -0.021982 x4))))))
        (= x4_next (+ (* -0.009236 x0) (+ (* -0.005274 x1) (+ (* -0.013199 x2) (+ (* -0.000946 x3) (* 0.967590 x4))))))
      )
      (Inv x0_next x1_next x2_next x3_next x4_next)
    )
  )
)

;; 3. Safety Query (Actuator Saturation > 12.0V or < -12.0V)
(assert
  (forall ((x0 Real) (x1 Real) (x2 Real) (x3 Real) (x4 Real))
    (=>
      (and
        (Inv x0 x1 x2 x3 x4)
        (or
          (> (+ (* -0.703028 x0) (+ (* -0.826255 x1) (+ (* -0.871902 x2) (+ (* -1.046685 x3) (* -1.246121 x4))))) 12.0)
          (< (+ (* -0.703028 x0) (+ (* -0.826255 x1) (+ (* -0.871902 x2) (+ (* -1.046685 x3) (* -1.246121 x4))))) -12.0)
        )
      )
      false
    )
  )
)

(check-sat)
(get-model)
