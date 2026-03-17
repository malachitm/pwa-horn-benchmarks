#include <iostream>

int main()
{
    double cv = 0;
    double s = 3250;
    int index = 0;
    while (1)
    {
        double err = s - cv;
        double control = 0.0009 * err;
        cv += control;
        index++;
        if (index > 9000)
        {
            std::cout << "Current Value:" << cv << "\n";
            exit(EXIT_SUCCESS);
        }
    }
    return 0;
}