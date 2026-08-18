"""IntelliHire Module 2: transparent mock-IRT adaptive assessment engine."""
from dataclasses import dataclass, asdict
from math import exp
from typing import List, Dict, Optional

@dataclass
class Question:
    id: str
    section: str
    topic: str
    difficulty: float
    discrimination: float
    prompt: str
    options: List[str]
    answer: int
    explanation: str
    hint: str
    kind: str = "mcq"

QUESTION_BANK = [
    Question("py-01","Python","Data structures",-0.7,1.0,"Which Python type maps keys to values?",["set","dict","tuple","bytes"],1,"dict stores key/value pairs.","Think key/value lookup."),
    Question("py-02","Python","Decorators",0.1,1.1,"What does a decorator primarily do?",["Compile Python","Wrap or modify callable behavior","Create a database","Free memory"],1,"A decorator wraps a callable.","Think @syntax."),
    Question("py-03","Python","Concurrency",0.9,1.25,"For CPU-bound Python work, which approach commonly bypasses the GIL for parallel execution?",["Threads only","Multiprocessing","Global variables","List comprehensions"],1,"Separate processes use independent interpreters.","Processes have separate interpreters."),
    Question("algo-01","Algorithms","Complexity",-0.2,1.0,"Binary search on a sorted array has which typical complexity?",["O(1)","O(log n)","O(n)","O(n²)"],1,"Each comparison halves the search interval.","The search space halves."),
    Question("algo-02","Algorithms","Graphs",0.7,1.2,"Which algorithm finds shortest paths from one source with non-negative edge weights?",["Dijkstra","Kruskal","DFS","Floyd cycle detection"],0,"Dijkstra uses a priority queue for this case.","Think shortest path."),
    Question("sql-01","SQL","Aggregation",0.0,1.0,"Which clause filters grouped rows after aggregation?",["WHERE","HAVING","ORDER BY","LIMIT"],1,"HAVING filters groups after GROUP BY.","WHERE operates before grouping."),
    Question("ml-01","Machine Learning","Classification",0.3,1.1,"What does precision measure?",["True positives among predicted positives","True positives among actual positives","All correct predictions","Negative predictions only"],0,"Precision = TP / (TP + FP).","Focus on predicted positives."),
    Question("ml-02","Machine Learning","Generalization",1.0,1.25,"Which technique directly penalizes large model coefficients?",["Normalization","L1/L2 regularization","One-hot encoding","Shuffling"],1,"L1/L2 regularization adds coefficient penalties.","It changes the loss function."),
]

def probability(theta: float, difficulty: float, discrimination: float = 1.0) -> float:
    return 1.0 / (1.0 + exp(-discrimination * (theta - difficulty)))

def information(theta: float, difficulty: float, discrimination: float = 1.0) -> float:
    p = probability(theta, difficulty, discrimination)
    return discrimination ** 2 * p * (1.0 - p)

def update_ability(theta: float, question: Question, correct: bool, learning_rate: float = 0.75) -> float:
    p = probability(theta, question.difficulty, question.discrimination)
    return theta + learning_rate * question.discrimination * ((1.0 if correct else 0.0) - p)

def select_next(theta: float, answered: List[str], section: Optional[str] = None) -> Optional[Question]:
    pool = [q for q in QUESTION_BANK if q.id not in answered]
    if section:
        preferred = [q for q in pool if q.section == section]
        if preferred:
            pool = preferred
    return max(pool, key=lambda q: information(theta, q.difficulty, q.discrimination), default=None)

def evaluate_answer(theta: float, question: Question, answer_index: int) -> Dict:
    correct = answer_index == question.answer
    new_theta = update_ability(theta, question, correct)
    return {"correct": correct, "probability": round(probability(theta, question.difficulty, question.discrimination),4), "ability_before": round(theta,4), "ability_after": round(new_theta,4), "confidence": round(min(0.99,0.5 + abs(new_theta)/4),4), "question": asdict(question)}

def score_assessment(events: List[Dict]) -> Dict:
    total = len(events)
    correct = sum(1 for e in events if e.get("correct"))
    accuracy = correct / total * 100 if total else 0
    theta = events[-1].get("ability_after",0) if events else 0
    sections = {}
    for event in events:
        sections.setdefault(event["question"]["section"], []).append(event)
    section_scores = {name: round(sum(1 for e in rows if e["correct"]) / len(rows) * 100,1) for name,rows in sections.items()}
    return {"score":round(accuracy,1),"accuracy":round(accuracy,1),"ability":round(theta,2),"questions":total,"correct":correct,"section_scores":section_scores}
