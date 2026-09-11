import csv
import re
import os

# The new orthogonal buckets we want to inject
BUCKETS = [
    'bucket(rank(cap), range="0, 1, 0.1")',
    'bucket(rank(ts_mean(volume, 20)), range="0, 1, 0.1")'
]

def apply_bucket_orthogonalization(code):
    """
    Replaces standard neutralizations (industry, subindustry, sector) 
    with custom quantitative buckets.
    """
    variants = []
    
    # Check if the code has a standard neutralization
    if re.search(r',\s*(industry|subindustry|sector)\)', code):
        for bucket in BUCKETS:
            # Variant 1: Direct Replacement
            variant1 = re.sub(r',\s*(industry|subindustry|sector)\)', f', {bucket})', code)
            variants.append(variant1)
            
            # Variant 2: Double Neutralization
            # Replaces group_neutralize(X, industry) with group_neutralize(group_neutralize(X, industry), bucket)
            variant2 = re.sub(
                r'group_neutralize\((.+?),\s*(industry|subindustry|sector)\)', 
                rf'group_neutralize(group_neutralize(\1, \2), {bucket})', 
                code
            )
            if variant2 != variant1:
                variants.append(variant2)
                
    return list(set(variants))

def process_csv_for_buckets():
    csv_file = "simulation_results.csv"
    if not os.path.exists(csv_file):
        print(f"Error: {csv_file} not found.")
        return

    elite_candidates = []
    
    with open(csv_file, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get("Status") == "SUCCESS":
                try:
                    sharpe = float(row.get("Sharpe", 0))
                    fitness = float(row.get("Fitness", 0))
                    checks = row.get("FailedChecks", "")
                    
                    # Target strong alphas that suffer from correlation
                    if sharpe > 1.4 and fitness > 1.0 and "CONCENTRATED_WEIGHT" not in checks:
                        code = row.get("Code", "").strip('"')
                        if code and code not in elite_candidates:
                            elite_candidates.append(code)
                except ValueError:
                    continue

    print(f"Found {len(elite_candidates)} base elite alphas to orthogonalize.")
    
    generated_variants = []
    for code in elite_candidates:
        generated_variants.extend(apply_bucket_orthogonalization(code))
        
    # Write to a new file to easily copy-paste or auto-simulate
    with open("bucket_candidates.txt", "w", encoding="utf-8") as out:
        for v in set(generated_variants):
            out.write(v + "\n")
            
    print(f"Successfully generated {len(set(generated_variants))} Decorrelated Bucket Variants!")
    print("Saved to bucket_candidates.txt")

if __name__ == "__main__":
    process_csv_for_buckets()