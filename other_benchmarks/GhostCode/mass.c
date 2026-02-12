/*The bounds used for the computation of the executable code's floating-point errors are the following:
|y| <= 2.2803;
|xc1| <= 2.6205;
|xc2| <= 2.3859;
|xc3| <= 1.5325;
|xc4| <= 2.4305;
|delta| <= 1;
*/

// This lemma facilitates the proof of the pwIQC lemma
/*@ lemma delta_bound:
  @ \forall real delta, real alpha; (alpha >= 0 && -alpha <= delta <= alpha) ==> alpha*alpha - delta*delta >= 0;
*/

// Defining the Positive Semidefinite Matrix axiom:
/*@ axiomatic PositiveDefinite_5x5 {
  @ logic real X11_5x5;
  @ logic real X12_5x5;
  @ logic real X13_5x5;
  @ logic real X14_5x5;
  @ logic real X15_5x5;
  @ logic real X22_5x5;
  @ logic real X23_5x5;
  @ logic real X24_5x5;
  @ logic real X25_5x5;
  @ logic real X33_5x5;
  @ logic real X34_5x5;
  @ logic real X35_5x5;
  @ logic real X44_5x5;
  @ logic real X45_5x5;
  @ logic real X55_5x5;
  @
  @ axiom positive_definite_5x5:
  @ \forall real r1, r2, r3, r4, r5;
  @ X11_5x5 * r1 * r1 + 2 * X12_5x5 * r1 * r2 + 2 * X13_5x5 * r1 * r3 +
  @ 2 * X14_5x5 * r1 * r4 + 2 * X15_5x5 * r1 * r5 +
  @ X22_5x5 * r2 * r2 + 2 * X23_5x5 * r2 * r3 + 2 * X24_5x5 * r2 * r4 +
  @ 2 * X25_5x5 * r2 * r5 + X33_5x5 * r3 * r3 +
  @ 2 * X34_5x5 * r3 * r4 + 2 * X35_5x5 * r3 * r5 +
  @ X44_5x5 * r4 * r4 + 2 * X45_5x5 * r4 * r5 + X55_5x5 * r5 * r5 >= 0;
  @ }
*/

// Validating the general condition that implies the IQC condition. Specifically, validating that [(alpha^2-delta^2)*r^T*X*r >= 0] where X is positive semidefinite, alpha>0, and |delta| <= alpha.
/*@ lemma pwIQC_5x5:
  @ \forall real r1, r2, r3, r4, r5, alpha, delta;
  @ alpha >= 0 && delta <= alpha && delta >= -alpha ==> (alpha * alpha - delta * delta >= 0) &&
  @ (alpha * alpha * (X11_5x5 * r1 * r1 + 2 * X12_5x5 * r1 * r2 + 2 * X13_5x5 * r1 * r3 +
  @ 2 * X14_5x5 * r1 * r4 + 2 * X15_5x5 * r1 * r5 +
  @ X22_5x5 * r2 * r2 + 2 * X23_5x5 * r2 * r3 + 2 * X24_5x5 * r2 * r4 +
  @ 2 * X25_5x5 * r2 * r5 + X33_5x5 * r3 * r3 +
  @ 2 * X34_5x5 * r3 * r4 + 2 * X35_5x5 * r3 * r5 +
  @ X44_5x5 * r4 * r4 + 2 * X45_5x5 * r4 * r5 + X55_5x5 * r5 * r5) -
  @ delta * delta * (X11_5x5 * r1 * r1 + 2 * X12_5x5 * r1 * r2 + 2 * X13_5x5 * r1 * r3 +
  @ 2 * X14_5x5 * r1 * r4 + 2 * X15_5x5 * r1 * r5 +
  @ X22_5x5 * r2 * r2 + 2 * X23_5x5 * r2 * r3 + 2 * X24_5x5 * r2 * r4 +
  @ 2 * X25_5x5 * r2 * r5 + X33_5x5 * r3 * r3 +
  @ 2 * X34_5x5 * r3 * r4 + 2 * X35_5x5 * r3 * r5 +
  @ X44_5x5 * r4 * r4 + 2 * X45_5x5 * r4 * r5 + X55_5x5 * r5 * r5) >= 0);
*/

typedef struct
{
    double x1, x2, x3, x4;
} state;
typedef struct
{
    double u1;
} control_input;

// Logic Functions to Construct phi
/*@
  logic real compute_phi1 (real pre_xc1, real pre_xc2, real pre_xc3, real pre_xc4, real y) = -0.15503 * pre_xc1 + 0.03198 * pre_xc2 + -0.09787999999999999 * pre_xc3 + -0.00532 * pre_xc4 + 0 * y;
  logic real compute_phi2 (real pre_xc1, real pre_xc2, real pre_xc3, real pre_xc4, real y) = 0.65434 * pre_xc1 + -0.14282 * pre_xc2 + 0.30492 * pre_xc3 + 0.03626 * pre_xc4 + 0 * y;
  logic real compute_phi3 (real pre_xc1, real pre_xc2, real pre_xc3, real pre_xc4, real y) = 0.6169 * pre_xc1 + -0.12217 * pre_xc2 + 0.34429 * pre_xc3 + 0.03196 * pre_xc4 + 1.0053 * y;
  logic real compute_phi4 (real pre_xc1, real pre_xc2, real pre_xc3, real pre_xc4, real y) = 2.29189 * pre_xc1 + -0.51695 * pre_xc2 + 1.15661 * pre_xc3 + 0.10179 * pre_xc4 + 0 * y;
  logic real compute_phi5 (real pre_xc1, real pre_xc2, real pre_xc3, real pre_xc4, real y) = 0.24126 * pre_xc1 + -0.04778 * pre_xc2 + 0.13465 * pre_xc3 + 0.0125 * pre_xc4 + -2.57059 * y;
*/

// Logic Functions to Compute the Updated States of the Augmented System H_tilde
/*@
  logic real update_xHtilde_1 (real pre_xc1, real pre_xc2, real pre_xc3, real pre_xc4, real theta1, real theta2, real theta3, real theta4, real theta5, real y) = 1.17757 * pre_xc1 + 0.15468 * pre_xc2 + 0.3614 * pre_xc3 + 0.07437000000000001 * pre_xc4 + 0.61714 * theta1 + -0.78684 * theta2 + 0.20519 * theta3 + 0.15518 * theta4 + 0.03225 * theta5 + -0.34712 * y;
  logic real update_xHtilde_2 (real pre_xc1, real pre_xc2, real pre_xc3, real pre_xc4, real theta1, real theta2, real theta3, real theta4, real theta5, real y) = -3.70972 * pre_xc1 + 1.5429 * pre_xc2 + -2.65686 * pre_xc3 + -0.19578 * pre_xc4 + 0.11973 * theta1 + -0.15266 * theta2 + -0.82326 * theta3 + 0.03011 * theta4 + -0.62547 * theta5 + 4.32037 * y;
  logic real update_xHtilde_3 (real pre_xc1, real pre_xc2, real pre_xc3, real pre_xc4, real theta1, real theta2, real theta3, real theta4, real theta5, real y) = -2.28481 * pre_xc1 + 0.18366 * pre_xc2 + -1.01544 * pre_xc3 + -0.17827 * pre_xc4 + 0.66816 * theta1 + 0.46416 * theta2 + -0.09265 * theta3 + -0.09154 * theta4 + -0.07739 * theta5 + 2.82567 * y;
  logic real update_xHtilde_4 (real pre_xc1, real pre_xc2, real pre_xc3, real pre_xc4, real theta1, real theta2, real theta3, real theta4, real theta5, real y) = 0.82117 * pre_xc1 + -0.37183 * pre_xc2 + 0.04747 * pre_xc3 + 0.73553 * pre_xc4 + 0.46416 * theta1 + 0.44041 * theta2 + 0.05392 * theta3 + 0.11672 * theta4 + 0.26285 * theta5 + -0.74581 * y;
*/

// Logic Function to Compute the Control Input of the Augmented System H_tilde
/*@
  logic real compute_uHtilde(real pre_xc1, real pre_xc2, real pre_xc3, real pre_xc4, real theta1, real theta2, real theta3, real theta4, real theta5, real y) = 21.28825 * pre_xc1 + -5.09412 * pre_xc2 + 11.70845 * pre_xc3 + -1.79242 * pre_xc4 + -0.23417 * theta1 + 0.29857 * theta2 + -0.94052 * theta3 + 2.58161 * theta4 + 2.20277 * theta5 + -23.56524 * y;
*/

// Executable code of the affine LPV controller K_tilde
/*@
requires \valid(xc) && \valid(u);
requires \separated(&(xc->x1),&(xc->x2),&(xc->x3),&(xc->x4),&(u->u1));
requires -1 <= delta <= 1;
assigns *xc, *u;
behavior model_verification:
    ensures \let phi1 = compute_phi1 (\old(xc->x1), \old(xc->x2), \old(xc->x3), \old(xc->x4), y);
        \let phi2 = compute_phi2 (\old(xc->x1), \old(xc->x2), \old(xc->x3), \old(xc->x4), y);
        \let phi3 = compute_phi3 (\old(xc->x1), \old(xc->x2), \old(xc->x3), \old(xc->x4), y);
        \let phi4 = compute_phi4 (\old(xc->x1), \old(xc->x2), \old(xc->x3), \old(xc->x4), y);
        \let phi5 = compute_phi5 (\old(xc->x1), \old(xc->x2), \old(xc->x3), \old(xc->x4), y);
        \let theta1 = delta * phi1;
        \let theta2 = delta * phi2;
        \let theta3 = delta * phi3;
        \let theta4 = delta * phi4;
        \let theta5 = delta * phi5;
        \let xH1 = update_xHtilde_1 (\old(xc->x1), \old(xc->x2), \old(xc->x3), \old(xc->x4), theta1, theta2, theta3, theta4, theta5, y);
        \let xH2 = update_xHtilde_2 (\old(xc->x1), \old(xc->x2), \old(xc->x3), \old(xc->x4), theta1, theta2, theta3, theta4, theta5, y);
        \let xH3 = update_xHtilde_3 (\old(xc->x1), \old(xc->x2), \old(xc->x3), \old(xc->x4), theta1, theta2, theta3, theta4, theta5, y);
        \let xH4 = update_xHtilde_4 (\old(xc->x1), \old(xc->x2), \old(xc->x3), \old(xc->x4), theta1, theta2, theta3, theta4, theta5, y);
        \let uH = compute_uHtilde (\old(xc->x1), \old(xc->x2), \old(xc->x3), \old(xc->x4), theta1, theta2, theta3, theta4, theta5, y);
        xH1 == xc->x1 && xH2 == xc->x2 && xH3 == xc->x3 && xH4 == xc->x4 && uH == u->u1;

*/

void controller(state *xc, control_input *u, double delta, double y)
{
    double pre_xc1 = xc->x1, pre_xc2 = xc->x2, pre_xc3 = xc->x3, pre_xc4 = xc->x4;

    // Compute Control Input
    u->u1 = 21.28825 * pre_xc1 + -5.09412 * pre_xc2 + 11.70845 * pre_xc3 + -1.79242 * pre_xc4 + -0.23417 * (-0.15503 * delta * pre_xc1 + 0.03198 * delta * pre_xc2 + -0.09787999999999999 * delta * pre_xc3 + -0.00532 * delta * pre_xc4) + 0.29857 * (0.65434 * delta * pre_xc1 + -0.14282 * delta * pre_xc2 + 0.30492 * delta * pre_xc3 + 0.03626 * delta * pre_xc4) + -0.94052 * (0.6169 * delta * pre_xc1 + -0.12217 * delta * pre_xc2 + 0.34429 * delta * pre_xc3 + 0.03196 * delta * pre_xc4 + 1.0053 * delta * y) + 2.58161 * (2.29189 * delta * pre_xc1 + -0.51695 * delta * pre_xc2 + 1.15661 * delta * pre_xc3 + 0.10179 * delta * pre_xc4) + 2.20277 * (0.24126 * delta * pre_xc1 + -0.04778 * delta * pre_xc2 + 0.13465 * delta * pre_xc3 + 0.0125 * delta * pre_xc4 + -2.57059 * delta * y) + -23.56524 * y;

    // Update Controller States
    xc->x1 = 1.17757 * pre_xc1 + 0.15468 * pre_xc2 + 0.3614 * pre_xc3 + 0.07437000000000001 * pre_xc4 + 0.61714 * (-0.15503 * delta * pre_xc1 + 0.03198 * delta * pre_xc2 + -0.09787999999999999 * delta * pre_xc3 + -0.00532 * delta * pre_xc4) + -0.78684 * (0.65434 * delta * pre_xc1 + -0.14282 * delta * pre_xc2 + 0.30492 * delta * pre_xc3 + 0.03626 * delta * pre_xc4) + 0.20519 * (0.6169 * delta * pre_xc1 + -0.12217 * delta * pre_xc2 + 0.34429 * delta * pre_xc3 + 0.03196 * delta * pre_xc4 + 1.0053 * delta * y) + 0.15518 * (2.29189 * delta * pre_xc1 + -0.51695 * delta * pre_xc2 + 1.15661 * delta * pre_xc3 + 0.10179 * delta * pre_xc4) + 0.03225 * (0.24126 * delta * pre_xc1 + -0.04778 * delta * pre_xc2 + 0.13465 * delta * pre_xc3 + 0.0125 * delta * pre_xc4 + -2.57059 * delta * y) + -0.34712 * y;
    xc->x2 = -3.70972 * pre_xc1 + 1.5429 * pre_xc2 + -2.65686 * pre_xc3 + -0.19578 * pre_xc4 + 0.11973 * (-0.15503 * delta * pre_xc1 + 0.03198 * delta * pre_xc2 + -0.09787999999999999 * delta * pre_xc3 + -0.00532 * delta * pre_xc4) + -0.15266 * (0.65434 * delta * pre_xc1 + -0.14282 * delta * pre_xc2 + 0.30492 * delta * pre_xc3 + 0.03626 * delta * pre_xc4) + -0.82326 * (0.6169 * delta * pre_xc1 + -0.12217 * delta * pre_xc2 + 0.34429 * delta * pre_xc3 + 0.03196 * delta * pre_xc4 + 1.0053 * delta * y) + 0.03011 * (2.29189 * delta * pre_xc1 + -0.51695 * delta * pre_xc2 + 1.15661 * delta * pre_xc3 + 0.10179 * delta * pre_xc4) + -0.62547 * (0.24126 * delta * pre_xc1 + -0.04778 * delta * pre_xc2 + 0.13465 * delta * pre_xc3 + 0.0125 * delta * pre_xc4 + -2.57059 * delta * y) + 4.32037 * y;
    xc->x3 = -2.28481 * pre_xc1 + 0.18366 * pre_xc2 + -1.01544 * pre_xc3 + -0.17827 * pre_xc4 + 0.66816 * (-0.15503 * delta * pre_xc1 + 0.03198 * delta * pre_xc2 + -0.09787999999999999 * delta * pre_xc3 + -0.00532 * delta * pre_xc4) + 0.46416 * (0.65434 * delta * pre_xc1 + -0.14282 * delta * pre_xc2 + 0.30492 * delta * pre_xc3 + 0.03626 * delta * pre_xc4) + -0.09265 * (0.6169 * delta * pre_xc1 + -0.12217 * delta * pre_xc2 + 0.34429 * delta * pre_xc3 + 0.03196 * delta * pre_xc4 + 1.0053 * delta * y) + -0.09154 * (2.29189 * delta * pre_xc1 + -0.51695 * delta * pre_xc2 + 1.15661 * delta * pre_xc3 + 0.10179 * delta * pre_xc4) + -0.07739 * (0.24126 * delta * pre_xc1 + -0.04778 * delta * pre_xc2 + 0.13465 * delta * pre_xc3 + 0.0125 * delta * pre_xc4 + -2.57059 * delta * y) + 2.82567 * y;
    xc->x4 = 0.82117 * pre_xc1 + -0.37183 * pre_xc2 + 0.04747 * pre_xc3 + 0.73553 * pre_xc4 + 0.46416 * (-0.15503 * delta * pre_xc1 + 0.03198 * delta * pre_xc2 + -0.09787999999999999 * delta * pre_xc3 + -0.00532 * delta * pre_xc4) + 0.44041 * (0.65434 * delta * pre_xc1 + -0.14282 * delta * pre_xc2 + 0.30492 * delta * pre_xc3 + 0.03626 * delta * pre_xc4) + 0.05392 * (0.6169 * delta * pre_xc1 + -0.12217 * delta * pre_xc2 + 0.34429 * delta * pre_xc3 + 0.03196 * delta * pre_xc4 + 1.0053 * delta * y) + 0.11672 * (2.29189 * delta * pre_xc1 + -0.51695 * delta * pre_xc2 + 1.15661 * delta * pre_xc3 + 0.10179 * delta * pre_xc4) + 0.26285 * (0.24126 * delta * pre_xc1 + -0.04778 * delta * pre_xc2 + 0.13465 * delta * pre_xc3 + 0.0125 * delta * pre_xc4 + -2.57059 * delta * y) + -0.74581 * y;
}