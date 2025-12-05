#include <iostream>
#include <fstream>
#include <vector>
#include <string>
#include <random>
#include <tuple>
#include <format>
#include <filesystem>
#include <format>
#include <iostream>
#include <set>
#include <string>
#include <string_view>

// Template content stitched from the provided source fragments
const std::string SMT_TEMPLATE = R"((set-option :pp.decimal true)
(set-logic HORN)
(declare-fun Inv (Real Real Real Real Real) Bool)

(assert (forall 
	((currentvalue Real)
	 (error Real) (controloutput Real)
	 (controlsignal Real) (i Real)
	)

	(=>
		(and
			(= currentvalue {{REAL1}})
			(= controlsignal {{REAL1}})
			(= i 0.0)
		)
		( Inv currentvalue error controloutput controlsignal i))
))

(assert (forall 
	((currentvalue Real)
	 (error Real) (controloutput Real)
	 (controlsignal Real) (i Real)
	 (currentvalue0 Real)
	 (error0 Real) (controloutput0 Real)
	 (controlsignal0 Real) (i0 Real)
	)

	(=> 
		(and
			( Inv currentvalue error controloutput controlsignal i)
            
			(= error0 (- {{REAL3}} currentvalue))
			(= controloutput0 (* {{REAL4}} error0))
			(= controlsignal0 controloutput0)
			(= currentvalue0 (+ currentvalue controlsignal0))
			(= i0 (+ i 1.0))
		)
		(Inv currentvalue0 error0 controloutput0 controlsignal0 i0))
))

(assert (forall 
	((currentvalue Real)
	 (error Real) (controloutput Real)
	 (controlsignal Real) (i Real)
	 (currentvalue0 Real)
	 (error0 Real) (controloutput0 Real)
	 (controlsignal0 Real) (i0 Real)
	)

	(=> 
		(and
			( Inv currentvalue error controloutput controlsignal i)

			(= error0 (- {{REAL3}} currentvalue))
			(= controloutput0 (* {{REAL4}} error0))
			(= controlsignal0 controloutput0)
			(= currentvalue0 (+ currentvalue controlsignal0))
			(= i0 (+ i 1.0))
			(not (=> 
				(>= i0 {{REAL5}}) 
				(and
					(<= (- 0.0 {{REAL6}}) (- {{REAL3}} currentvalue0)) (<= (- {{REAL3}} currentvalue0) {{REAL7}})
				)))
		)
		false)
))

(check-sat)
(get-model)
)";

// Helper to replace all occurrences of a substring
void replace_all(std::string &str, const std::string &from, const std::string &to)
{
    if (from.empty())
        return;
    size_t start_pos = 0;
    while ((start_pos = str.find(from, start_pos)) != std::string::npos)
    {
        str.replace(start_pos, from.length(), to);
        start_pos += to.length();
    }
}

int main()
{
    // Random Number Generation Setup
    std::random_device rd;
    std::mt19937 gen(rd());

    // Distributions
    // REAL1, REAL2, REAL3: -100 to 100 inclusive
    std::uniform_real_distribution<double> dist_100(0, 100.0);

    // REAL4: 0 to 1 exclusive
    // Note: standard distribution is [a, b). We need to handle 0.0 case manually to make it (0, 1).
    std::uniform_real_distribution<double> dist_0_1(0.1, 0.3);

    // REAL5: 2000 to 100 (Assuming 100 to 2000 inclusive)
    std::uniform_real_distribution<double> dist_2000(100.0, 2000.0);

    // REAL6, REAL7: -75 to 75 inclusive
    std::uniform_real_distribution<double> dist_75(0, 25.0);

    std::cout << "Generating 100 SMT2 files..." << std::endl;

    for (int i = 0; i < 100; ++i)
    {
        // Generate values
        double r1 = dist_100(gen);
        double r2 = dist_100(gen);
        double r3 = dist_100(gen);

        // Ensure r4 is strictly > 0.0
        double r4 = 0.0;
        while (r4 <= 0.000001)
        {
            r4 = dist_0_1(gen);
        }

        double r5 = dist_2000(gen);
        double r6 = dist_75(gen);
        double r7 = dist_75(gen);

        // Create file content
        std::string content = SMT_TEMPLATE;

        // Perform replacements
        // Note: formatted with high precision to ensure SMT solver consistency
        replace_all(content, "{{REAL1}}", std::format("{:.6f}", r1));
        replace_all(content, "{{REAL2}}", std::format("{:.6f}", r2)); // Generated but not present in template text
        replace_all(content, "{{REAL3}}", std::format("{:.6f}", r3));
        replace_all(content, "{{REAL4}}", std::format("{:.6f}", r4));
        replace_all(content, "{{REAL5}}", std::format("{:.6f}", r5));
        replace_all(content, "{{REAL6}}", std::format("{:.6f}", r6));
        replace_all(content, "{{REAL7}}", std::format("{:.6f}", r7));

        // Write to file
        std::string filename = std::format("p{}.smt2", i);
        std::ofstream outfile(filename);
        if (outfile.is_open())
        {
            outfile << content;
            outfile.close();
        }
        else
        {
            std::cerr << "Error writing to " << filename << std::endl;
        }
    }

    std::cout << "Done. Generated p0.smt2 to p99.smt2." << std::endl;

    return 0;
}