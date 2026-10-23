from src.samples import BENCHMARK_SAMPLES
from src.evaluator import run_evaluation
from src.metrics import extract_transcript_metrics

def run_tests():
    print("=" * 60)
    print("TESTING 8x8 BENCHMARK CASES ACROSS ALL TIERS")
    print("=" * 60)
    
    passed = 0
    total = len(BENCHMARK_SAMPLES)
    
    for name, data in BENCHMARK_SAMPLES.items():
        metrics = extract_transcript_metrics(data["transcript"])
        eval_res = run_evaluation(
            transcript=data["transcript"],
            visual_info={
                "camera_status": data["camera_status"],
                "background_status": data["background_status"],
                "lighting_status": data["lighting_status"]
            },
            api_choice="Offline"
        )
        
        expected = data["expected_quality"]
        predicted = eval_res["overall_quality"]
        is_match = (expected == predicted)
        if is_match:
            passed += 1
            
        print(f"  * Expected:  {expected}")
        print(f"  * Predicted: {predicted} (Score: {eval_res['overall_score']}/100) -> {'[MATCH OK]' if is_match else '[DIFF]'}")
        print(f"  * Students:  {metrics['detected_students']} (Called {metrics['name_mentions_count']} times)")
        print(f"  * Questions: {metrics['questions_count']} | Affirmations: {metrics['positive_affirmations_count']} | HW: {metrics['has_homework']}")
        print(f"  * Strengths: {eval_res['key_strengths'][:2]}")
        print(f"  * Growth:    {eval_res['growth_areas'][:2]}")
        
    print("\n" + "=" * 60)
    print(f"SUMMARY: {passed}/{total} benchmarks matched ground-truth quality tiers!")
    print("=" * 60)

if __name__ == "__main__":
    run_tests()
