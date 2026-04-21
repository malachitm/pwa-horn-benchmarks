#include <iostream>
#include <fstream>
#include <vector>
#include <string>
#include <tuple>
#include <format>
#include <filesystem>
#include <set>
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
			(<= {{REAL1}} currentvalue)
            (<= currentvalue {{REAL2}})
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

// Helper to generate evenly spaced values
std::vector<double> linspace(double start, double end, int num_steps)
{
    std::vector<double> values;
    if (num_steps <= 0)
        return values;
    if (num_steps == 1)
    {
        values.push_back(start);
        return values;
    }

    double step = (end - start) / (num_steps - 1);
    for (int i = 0; i < num_steps; ++i)
    {
        values.push_back(start + (step * i));
    }
    return values;
}

int main()
{
    // ================= CONFIGURATION =================
    // Define the number of steps for each parameter.
    // WARNING: Total files = steps^6.
    // 3 steps = 729 files.
    // 5 steps = 15,625 files.
    // 10 steps = 1,000,000 files.
    const int STEPS = 30;

    // Ranges based on your original distribution logic
    const double R1_MIN = 0.0, R1_MAX = 0.0;
    const double R2_MIN = 0.0, R2_MAX = 300.0;
    const double R3_MIN = 100.0, R3_MAX = 100.0;
    const double R4_MIN = 0.1, R4_MAX = 0.1;
    const double R5_MIN = 200.0, R5_MAX = 200.0;
    const double R6_MIN = 1.0, R6_MAX = 1.0;
    const double R7_MIN = 1.0, R7_MAX = 1.0;
    // =================================================

    // Pre-calculate the values for each parameter
    auto r1_vals = linspace(R1_MIN, R1_MAX, 1);
    auto r2_vals = linspace(R2_MIN, R2_MAX, STEPS);
    auto r3_vals = linspace(R3_MIN, R3_MAX, 1);
    auto r4_vals = linspace(R4_MIN, R4_MAX, 1);
    auto r5_vals = linspace(R5_MIN, R5_MAX, 1);
    auto r6_vals = linspace(R6_MIN, R6_MAX, 1);
    auto r7_vals = linspace(R7_MIN, R7_MAX, 1);

    // Calculate total expected files
    size_t total_files = r1_vals.size() * r2_vals.size() * r3_vals.size() * r4_vals.size() * r5_vals.size() * r6_vals.size() * r7_vals.size();

    std::cout << "Generating " << total_files << " SMT2 files..." << std::endl;
    std::cout << "Values per parameter: " << STEPS << std::endl;

    int counter = 0;

    // Iterate through all combinations
    for (double r1 : r1_vals)
    {
        for (double r2 : r2_vals)
        {
            for (double r3 : r3_vals)
            {
                for (double r4 : r4_vals)
                {
                    for (double r5 : r5_vals)
                    {
                        for (double r6 : r6_vals)
                        {
                            for (double r7 : r7_vals)
                            {

                                std::string content = SMT_TEMPLATE;

                                // Perform replacements
                                // We use high precision for the content
                                replace_all(content, "{{REAL1}}", std::format("{:.6f}", r1));
                                replace_all(content, "{{REAL2}}", std::format("{:.6f}", r2));
                                // REAL2 is not in the template, so we skip it to save loops/logic
                                replace_all(content, "{{REAL3}}", std::format("{:.6f}", r3));
                                replace_all(content, "{{REAL4}}", std::format("{:.6f}", r4));
                                replace_all(content, "{{REAL5}}", std::format("{:.6f}", r5));
                                replace_all(content, "{{REAL6}}", std::format("{:.6f}", r6));
                                replace_all(content, "{{REAL7}}", std::format("{:.6f}", r7));

                                // Create Filename
                                // Format: p_R1_R3_R4_R5_R6_R7.smt2
                                // We use 2 decimal places for the filename to keep it readable
                                std::string filename = std::format(
                                    "p_{:.2f}_{:.2f}_{:.2f}_{:.4f}_{:.2f}_{:.2f}_{:.2f}.smt2",
                                    r1, r2, r3, r4, r5, r6, r7);

                                std::ofstream outfile(filename);
                                if (outfile.is_open())
                                {
                                    outfile << content;
                                    outfile.close();
                                    counter++;
                                }
                                else
                                {
                                    std::cerr << "Error writing to " << filename << std::endl;
                                }
                            }
                        }
                    }
                }
            }
        }
    }

    std::cout << "Done. Generated " << counter << " files." << std::endl;

    return 0;
}