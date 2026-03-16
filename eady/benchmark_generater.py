import subprocess
import sys

def run_batch_generation():
    mat_file = "eady.mat"
    
    # Loop from 10 to 60 (inclusive), stepping by 10
    dimensions_to_generate = range(2, 10, 1)
    
    print(f"Starting batch generation for {mat_file}...")
    print(f"Target dimensions: {list(dimensions_to_generate)}")
    print("-" * 40)
    
    for dim in dimensions_to_generate:
        print(f"\n--- Processing Dimension: {dim} ---")
        
        # Construct the command exactly as you would type it in the terminal
        command = [
            "python3", 
            "mat_to_smt.py", 
            mat_file, 
            str(dim), 
            "--singleton"
        ]
        
        try:
            # Execute the command and wait for it to finish
            subprocess.run(command, check=True)
        except FileNotFoundError:
            print("Error: Could not find 'generate_lqr_chc.py'. Ensure it is in the same folder.")
            sys.exit(1)
        except subprocess.CalledProcessError as e:
            print(f"Error: The generation failed for dimension {dim}.")
            # We don't exit here so it can try the next dimensions even if one fails
            
    print("\n" + "-" * 40)
    print("Batch generation complete! Your benchmark suite is ready.")

if __name__ == "__main__":
    run_batch_generation()