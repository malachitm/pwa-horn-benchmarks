/*
 * Generated System Parameters
 * ---------------------------
 * Seed: 42
 *
 * INPUT RANGES (Struct Values):
 * varCount  (Total Vars): [3, 5]
 * varVal    (Init Val)  : [0, 10]
 * coeffVal  (Coeffs)    : [-2, 2]
 * propLen   (Atoms/Assert): [2, 3]
 * propCount (Vars/Atom) : [1, 2]
 *
 * ACTUAL VALUES (Chosen for this system):
 * varCount  : 4
 * propLen   : 3
 * propCount : 2
 */

#include <assert.h>

void main()
{
    float x0 = 7.3199f;
    float x1 = 5.9866f;
    float x2 = 1.5602f;
    float x3 = 1.5599f;
    int i = 0;

    while (i < 300)
    {
        float x0_prime = x0;
        float x1_prime = x1;
        float x2_prime = x2;
        float x3_prime = x3;

        x0 = -1.7677f * x0_prime + 1.4647f * x1_prime + 0.4045f * x2_prime + 0.8323f * x3_prime - 1.9177f;
        x1 = 1.8796f * x0_prime + 1.3298f * x1_prime - 1.1506f * x2_prime - 1.2727f * x3_prime - 1.2664f;
        x2 = -0.7830f * x0_prime + 0.0990f * x1_prime - 0.2722f * x2_prime - 0.8351f * x3_prime + 0.4474f;
        x3 = -1.4420f * x0_prime - 0.8314f * x1_prime - 0.5346f * x2_prime - 0.1757f * x3_prime + 1.1407f;

        assert((0.0569f * x2 + 0.3697f * x1 - 1.8142f >= 0) || (-1.3179f * x0 - 1.7398f * x2 + 1.7955f >= 0) || (1.2336f * x0 - 0.7815f * x1 - 1.6093f >= 0));

        i++;
    }
}
