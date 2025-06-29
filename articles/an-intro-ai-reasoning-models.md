

```
sequenceDiagram
    participant U as User
    participant RM as Reasoning Model
    participant TR as Traditional Model
    
    rect rgb(240, 248, 255)
        Note over U,TR: Traditional Model Processing
        U->>+TR: Question: How many Rs in "strawberry"?
        TR-->>-U: Answer: 2
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