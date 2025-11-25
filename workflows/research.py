"""Research workflow for gathering and synthesizing information."""
from typing import Optional, List
from dataclasses import dataclass
from local_bridge import LocalBridge


@dataclass 
class ResearchSource:
    """A research source with findings."""
    query: str
    findings: str
    confidence: float
    sources: List[str]


class ResearchWorkflow:
    """Multi-agent research and synthesis workflow."""
    
    def __init__(self, bridge: Optional[LocalBridge] = None):
        self.bridge = bridge or LocalBridge()
        self.research_cache = {}
    
    def research(self, topic: str, depth: str = "standard") -> dict:
        """Run full research workflow on a topic."""
        # Phase 1: Generate research questions
        questions = self._generate_questions(topic, depth)
        
        # Phase 2: Research each question
        findings = []
        for question in questions:
            result = self._research_question(question)
            findings.append(result)
        
        # Phase 3: Synthesize findings
        synthesis = self._synthesize(topic, findings)
        
        # Phase 4: Generate final report
        report = self._generate_report(topic, findings, synthesis)
        
        return {
            "topic": topic,
            "questions": questions,
            "findings": findings,
            "synthesis": synthesis,
            "report": report
        }
    
    def _generate_questions(self, topic: str, depth: str) -> List[str]:
        """Generate research questions for the topic."""
        num_questions = {"quick": 3, "standard": 5, "deep": 8}.get(depth, 5)
        
        prompt = f"""Generate {num_questions} specific research questions about: {topic}

Make questions diverse, covering different aspects.
Format: One question per line, numbered 1-{num_questions}."""
        
        response = self.bridge.generate(prompt)
        questions = []
        for line in response.split('\n'):
            line = line.strip()
            if line and line[0].isdigit():
                # Remove numbering
                q = line.lstrip('0123456789.)-: ')
                if q:
                    questions.append(q)
        
        return questions[:num_questions]
    
    def _research_question(self, question: str) -> ResearchSource:
        """Research a specific question."""
        if question in self.research_cache:
            return self.research_cache[question]
        
        prompt = f"""Research this question thoroughly: {question}

Provide:
1. Key findings (factual information)
2. Confidence level (high/medium/low)
3. What sources would typically have this info

Be concise but comprehensive."""
        
        response = self.bridge.generate(prompt)
        
        # Parse confidence
        confidence = 0.5
        if "high" in response.lower():
            confidence = 0.9
        elif "low" in response.lower():
            confidence = 0.3
        
        result = ResearchSource(
            query=question,
            findings=response,
            confidence=confidence,
            sources=["LLM knowledge base"]
        )
        
        self.research_cache[question] = result
        return result
    
    def _synthesize(self, topic: str, findings: List[ResearchSource]) -> str:
        """Synthesize all findings into coherent understanding."""
        findings_text = "\n\n".join(
            f"Q: {f.query}\nA: {f.findings[:500]}" for f in findings
        )
        
        prompt = f"""Synthesize these research findings about "{topic}":

{findings_text}

Provide a coherent synthesis that:
1. Identifies key themes
2. Notes areas of agreement/disagreement
3. Highlights gaps in knowledge
4. Draws conclusions"""
        
        return self.bridge.generate(prompt)
    
    def _generate_report(self, topic: str, findings: List[ResearchSource], 
                        synthesis: str) -> str:
        """Generate final research report."""
        prompt = f"""Create a concise research report on "{topic}".

Synthesis: {synthesis[:1000]}

Format:
- Executive Summary (2-3 sentences)
- Key Findings (bullet points)
- Conclusions
- Recommendations for further research"""
        
        return self.bridge.generate(prompt)
