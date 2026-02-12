
extern float __VERIFIER_nondet_float(void);
extern void __assert_fail(const char *assertion, const char *file,
                          unsigned int line, const char *function);

int main()
{
    float xc1, xc2, xp1, xp2;
    xc1 = 0;
    xc2 = 0;
    xp1 = __VERIFIER_nondet_float();
    __VERIFIER_assume(xp1 <= 0.5);
    __VERIFIER_assume(-0.5 <= xp1);
    xp2 = 0;
    int i = 0;
    while (1)
    {
        float oxc1, oxc2, oxp1, oxp2, yd;
        yd = __VERIFIER_nondet_float();
	__VERIFIER_assume(yd <= 0.5);
	__VERIFIER_assume(-0.5 <= yd);
        oxc1 = xc1;
        oxc2 = xc2;
        oxp1 = xp1;
        oxp2 = xp2;
        xc1 = 0.499 * oxc1 - 0.05 * oxc2 + (oxp1 - yd);
        xc2 = 0.01 * oxc1 + oxc2;
        xp1 = 0.028224 * oxc1 + oxp1 + 0.01 * oxp2 - 0.064 * (oxp1 - yd);
        xp2 = 5.6448 * oxc1 - 0.01 * oxp1 + oxp2 - 12.8 * (oxp1 - yd);
        i++;
	
	if(i > 150.0){
		__VERIFIER_assert(xp1 + 0.3 <= 0.1);
		__VERIFIER_assert(-0.1 <= xp1 + 0.3);
		//__assert_fail("0", "test.c", 41, "main");
	}
    }
    return 0;
}
