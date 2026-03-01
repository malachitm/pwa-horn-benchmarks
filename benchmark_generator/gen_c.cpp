#include <iostream>
#include <fstream> // Added for file I/O
#include <string>
#include <vector>
#include <sstream>
#include <random>
#include <algorithm> // for shuffle
#include <iomanip>   // for setprecision

using namespace std;

// 1. Defined Struct
struct GenParameters
{
    pair<uint16_t, uint16_t> varCount;  // Range for TOTAL variables in program
    pair<uint16_t, uint16_t> varVal;    // Range for initial values (uint16 bounds -> double)
    pair<int16_t, int16_t> coeffVal;    // Range for coefficients (int16 bounds -> double)
    pair<uint16_t, uint16_t> propLen;   // Range for number of atoms (disjunctions)
    pair<uint16_t, uint16_t> propCount; // Range for number of variables INSIDE each atom
};

// Helper: Get random integer in range [min, max]
template <typename T>
T randInt(mt19937 &gen, pair<T, T> range)
{
    if (range.first == range.second)
        return range.first;
    T minVal = min(range.first, range.second);
    T maxVal = max(range.first, range.second);
    uniform_int_distribution<long long> dist(minVal, maxVal);
    return static_cast<T>(dist(gen));
}

// Helper: Get random double in range [min, max]
double randDouble(mt19937 &gen, double minVal, double maxVal)
{
    if (minVal == maxVal)
        return minVal;
    if (minVal > maxVal)
        swap(minVal, maxVal);
    uniform_real_distribution<double> dist(minVal, maxVal);
    return dist(gen);
}

// Helper: Format double to string
string fmt(double val)
{
    stringstream ss;
    ss << fixed << setprecision(4) << val;
    return ss.str() + "f";
}

// 2. Generator Function
string generateCode(unsigned int seed, GenParameters params)
{
    mt19937 gen(seed);
    stringstream code;
    stringstream header;

    // --- A. Determine System Parameters (The "Actuals") ---
    // We determine these upfront so we can log them in the comments
    uint16_t actualVarCount = randInt(gen, params.varCount);
    uint16_t actualPropLen = randInt(gen, params.propLen);

    // Determine subset size (vars per atom) for the whole system
    uint16_t actualPropCount = randInt(gen, params.propCount);
    if (actualPropCount > actualVarCount)
        actualPropCount = actualVarCount;
    if (actualPropCount == 0 && actualVarCount > 0)
        actualPropCount = 1;

    // --- B. Generate Header Comments ---
    header << "/*\n";
    header << " * Generated System Parameters\n";
    header << " * ---------------------------\n";
    header << " * Seed: " << seed << "\n";
    header << " *\n";
    header << " * INPUT RANGES (Struct Values):\n";
    header << " * varCount  (Total Vars): [" << params.varCount.first << ", " << params.varCount.second << "]\n";
    header << " * varVal    (Init Val)  : [" << params.varVal.first << ", " << params.varVal.second << "]\n";
    header << " * coeffVal  (Coeffs)    : [" << params.coeffVal.first << ", " << params.coeffVal.second << "]\n";
    header << " * propLen   (Atoms/Assert): [" << params.propLen.first << ", " << params.propLen.second << "]\n";
    header << " * propCount (Vars/Atom) : [" << params.propCount.first << ", " << params.propCount.second << "]\n";
    header << " *\n";
    header << " * ACTUAL VALUES (Chosen for this system):\n";
    header << " * varCount  : " << actualVarCount << "\n";
    header << " * propLen   : " << actualPropLen << "\n";
    header << " * propCount : " << actualPropCount << "\n";
    header << " */\n\n";

    code << header.str();
    code << "#include <assert.h>\n\n";
    code << "void test_loop() {\n";

    // --- C. Setup Variables ---
    vector<string> allVars;
    for (int i = 0; i < actualVarCount; ++i)
        allVars.push_back("x" + to_string(i));

    // --- D. Initialization ---
    // Initialize user variables
    for (const string &v : allVars)
    {
        double initVal = randDouble(gen, (double)params.varVal.first, (double)params.varVal.second);
        code << "    float " << v << " = " << fmt(initVal) << ";\n";
    }

    // Initialize Loop Index
    code << "    int i = 0;\n";

    // --- E. Loop Guard (i < 300) ---
    code << "\n    while(i < 300) {\n";

    // --- F. Priming ---
    for (const string &v : allVars)
    {
        code << "        float " << v << "_prime = " << v << ";\n";
    }
    code << "\n";

    // --- G. Assignments ---
    for (const string &v : allVars)
    {
        code << "        " << v << " = ";

        bool firstTerm = true;
        for (const string &v_prime : allVars)
        {
            double coeff = randDouble(gen, (double)params.coeffVal.first, (double)params.coeffVal.second);

            if (!firstTerm && coeff >= 0)
                code << " + ";
            if (coeff < 0)
                code << " - ";
            code << fmt(abs(coeff)) << "*" << v_prime << "_prime";
            firstTerm = false;
        }

        double constVal = randDouble(gen, (double)params.coeffVal.first, (double)params.coeffVal.second);
        if (constVal >= 0)
            code << " + ";
        else
            code << " - ";
        code << fmt(abs(constVal)) << ";\n";
    }
    code << "\n";

    // --- H. Assertions ---
    if (actualPropLen > 0)
    {
        code << "        assert(";
        for (int j = 0; j < actualPropLen; ++j)
        {
            if (j > 0)
                code << " || ";

            code << "(";

            // Select Subset of Variables
            vector<string> shuffledVars = allVars;
            shuffle(shuffledVars.begin(), shuffledVars.end(), gen);

            // Use the pre-calculated actualPropCount
            uint16_t subsetSize = actualPropCount;

            bool firstInAtom = true;
            for (int k = 0; k < subsetSize; ++k)
            {
                double coeff = randDouble(gen, (double)params.coeffVal.first, (double)params.coeffVal.second);

                if (!firstInAtom && coeff >= 0)
                    code << " + ";
                if (coeff < 0)
                    code << " - ";
                code << fmt(abs(coeff)) << "*" << shuffledVars[k];
                firstInAtom = false;
            }

            double atomConst = randDouble(gen, (double)params.coeffVal.first, (double)params.coeffVal.second);
            if (atomConst >= 0)
                code << " + ";
            else
                code << " - ";
            code << fmt(abs(atomConst));

            code << " >= 0)";
        }
        code << ");\n";
    }

    // --- I. Increment Index ---
    code << "\n        i++;\n";
    code << "    }\n";
    code << "}\n";

    return code.str();
}

int main()
{
    GenParameters params;

    params.varCount = {3, 5};  // Total variables
    params.varVal = {0, 10};   // Init values
    params.coeffVal = {-2, 2}; // Coeffs
    params.propLen = {2, 3};   // Atoms in assertion
    params.propCount = {1, 2}; // Vars per atom

    string generatedC = generateCode(42, params);

    // Open file "test.c" for writing
    ofstream outFile("test.c");

    if (outFile.is_open())
    {
        outFile << generatedC;
        outFile.close();
        cout << "Successfully generated 'test.c'" << endl;
    }
    else
    {
        cerr << "Error: Could not open 'test.c' for writing." << endl;
        return 1;
    }

    return 0;
}