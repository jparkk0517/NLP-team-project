from langgraph.graph import END
import logging

def route_by_classification(state):
    result = state.get("classification", "other")
    if not result:
        logging.warning("No classification result found. Defaulting to END.")
        return END
    
    if result == "resume":
        return "generate_question_reasoning"
    elif result == "interview_answer":
        return "evaluate_answer"
    else:
        return END  # 기타 입력은 더 이상 진행 안 함

def route_by_evaluation(state):
    logging.info(f"[route_by_evaluation] state: {state}")
    result = state.get("evaluation")
    if not isinstance(result, dict):
        logging.warning("Invalid or missing evaluation result. Defaulting to END.")
        return END
    
    avg = result.get("averageScore", 0)
    if avg < 6:
        return "generate_followup_reasoning"
    else:
        return END
