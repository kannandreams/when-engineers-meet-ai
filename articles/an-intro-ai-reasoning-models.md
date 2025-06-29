

#### Rs in Strawberry Problem - diagram code

```mermaid
sequenceDiagram
    participant U as User
    participant RM as Reasoning Model
    participant TR as Traditional Model
    
    rect rgb(240, 248, 255)
        Note over U,TR: Traditional Model Processing
        U->>+TR: Question: How many Rs in "strawberry"?
        TR-->>-U: Answer: 3
    end
    
    rect rgb(255, 245, 238)
        Note over U,RM: Reasoning Model Processing
        U->>+RM: Question: How many Rs in "strawberry"?
        activate RM
        
        Note over RM: Chain-of-Thought Process
        RM->>RM: 1. Analyze task: Need to count Rs in "strawberry"
        RM->>RM: 2. Break down word: s-t-r-a-w-b-e-r-r-y
        RM->>RM: 3. Count Rs systematically:
        RM->>RM:   - First R after 't'
        RM->>RM:   - Second R after 'e'
        RM->>RM:   - Third R after second 'r'
        RM->>RM: 4. Verification check:
        RM->>RM:   - Double-checked position of each R
        RM->>RM:   - Confirmed total count
        deactivate RM
        
        RM-->>-U: Answer: 3
    end
```

#### Reasoning models challenges - LaTex

```latex
\documentclass{article}
\usepackage[usenames,dvipsnames]{xcolor}
\begin{document}

\section*{Reasoning models challenges}
\begingroup
\setlength{\tabcolsep}{10pt} % Default value: 6pt
\renewcommand{\arraystretch}{2.5} % Default value: 1
\begin{tabular}{| l |l |}\hline
\textbf{Cost and Latency} & More steps = higher token usage and slower inference \\\hline
\textbf{Error Propagation} & One bad step early can derail the whole chain \\\hline
\textbf{Modularity Trade-offs} & Splitting planning/execution helps reasoning but reduces fluency \\\hline
\textbf{Evaluation Difficulty} & No single metric captures quality of reasoning well \\ \hline
\end{tabular}
\endgroup
\end{document}

```

#### Comparison of LLM Types by Reasoning Style - LaTex
```latex
\documentclass{article}
\usepackage{graphicx}
\usepackage[margin=1in]{geometry}
\usepackage{booktabs}
\usepackage{amssymb}

\begin{document}

\section*{Comparison of LLM Types by Reasoning Style}

\begin{tabular}{@{}p{4cm}p{4cm}p{4cm}p{4cm}@{}}
\toprule
\textbf{Feature} &
\textbf{Standard LLMs} &
\textbf{Implicit LRMs} &
\textbf{Explicit LRMs} \\
\midrule
\textbf{Reasoning Type} &
None &
Reasoning but internal &
Visible reasoning \\

\textbf{Step-by-step Output} &
No &
No &
Yes \\

\textbf{Output Behavior} &
Pattern-matching &
Smart, but not explainable &
Shows how it solves \\

\textbf{Examples} &
GPT-2, Mistral-7B, BERT &
GPT-4 (no CoT prompting) &
GPT-4 with CoT, ReAct, ToT \\

\textbf{Tool Use / Modularity} &
No &
Usually not &
Combines tools, memory, search \\

\textbf{Transparency} &
Black box &
Black box with smarter guesses &
White box (or closer to it) \\
\bottomrule
\end{tabular}

\end{document}

```