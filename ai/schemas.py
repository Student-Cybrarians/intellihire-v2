MODULE1_SCHEMA = {
    "type": "object",
    "required": ["summary", "strengths", "matchedSkills", "missingSkills", "weakEvidence", "recommendations", "resumeImprovements", "atsExplanation", "confidence", "evidence"],
    "properties": {
        "summary": {"type": "string"}, "strengths": {"type": "array"}, "matchedSkills": {"type": "array"},
        "missingSkills": {"type": "array"}, "weakEvidence": {"type": "array"}, "recommendations": {"type": "array"},
        "resumeImprovements": {"type": "array"}, "atsExplanation": {"type": "array"}, "confidence": {"type": "number"},
        "evidence": {"type": "array"},
    },
}

MODULE2_SCHEMA = {"type": "object", "required": ["explanation", "hint", "misconception", "nextFocus"], "properties": {
    "explanation": {"type": "string"}, "hint": {"type": "string"}, "misconception": {"type": "string"}, "nextFocus": {"type": "string"}
}}

INTERVIEW_SCHEMA = {"type": "object", "required": ["feedback", "strengths", "improvements", "followUp"], "properties": {
    "feedback": {"type": "string"}, "strengths": {"type": "array"}, "improvements": {"type": "array"}, "followUp": {"type": "string"}
}}

MODULE5_SCHEMA = {"type": "object", "required": ["summary", "strengths", "weaknesses", "skillGaps", "priorities", "nextActions", "roadmapExplanation"], "properties": {
    "summary": {"type": "string"}, "strengths": {"type": "array"}, "weaknesses": {"type": "array"}, "skillGaps": {"type": "array"},
    "priorities": {"type": "array"}, "nextActions": {"type": "array"}, "roadmapExplanation": {"type": "array"}
}}

RESEARCH_SCHEMA = {"type": "object", "required": ["answer", "key_findings", "implications_for_candidate", "learning_actions", "citations"], "properties": {
    "answer": {"type": "string"}, "key_findings": {"type": "array"}, "implications_for_candidate": {"type": "array"},
    "learning_actions": {"type": "array"}, "citations": {"type": "array"}
}}
