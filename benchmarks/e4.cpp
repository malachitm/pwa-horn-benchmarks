#include <stdio.h>
// #include <cassert>

int main()
{
    double x = 2.0;
    double y = 3.0;
    for (int i = 0; i < 10; i++)
    {
        x *= 100.0;
        y *= 1.2;
        // assert(x < y);
    }
}