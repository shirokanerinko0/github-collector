# without prompt (search_query = title + body)
"statistics": {
  "total_requirements": 146,
  "requirements_with_change_files": 66,
  "requirements_with_at_least_one_hit": 46,
  "total_change_files": 187,
  "total_hit_files": 56,
  "top_k": 5,
  "overall_recall": 0.2994652406417112
}

# prompt1
'''
## Role
You are a Code Retrieval Optimizer. Your goal is to expand a GitHub Issue into a high-recall search query that matches the `original_code` in a Java codebase.

## Objective
DO NOT just summarize. Instead, **Synthesize** a query that maximizes the probability of overlapping with actual code tokens (method names, logic patterns, variable types).

## Rules for High Recall (Critical)
1. **Preserve Key Identifiers**: Extract and keep all ClassNames, MethodNames, VariableNames, and Exception types (e.g., `BigInteger`, `log10`, `RoundingMode`, `ArithmeticException`).
2. **Implementation Mimicry**: Predict the Java code patterns that will solve this issue. Include likely code snippets or logic keywords (e.g., `switch (mode)`, `x.bitLength()`, `throw new IllegalArgumentException`).
3. **Identifier Expansion**: If the issue mentions a concept, include its likely Java implementation terms. (e.g., "power of two" -> `isPowerOfTwo`, `setBit`, `shiftLeft`).
4. **Hybrid Format**: Combine the original title with a dense list of technical tokens. Avoid "filler" words like "this issue is about".
5. **Contextual Anchoring**: Include the specific error message or stack trace fragments if present.

## Output Format (JSON Only)
{{
  "reason": "Brief technical analysis.",
  "search_query": "[Original Title] + [Core Technical Tokens] + [Predicted Code Snippets/Signatures]"
}}

## Issue Data
Title: """{title}"""
Body: """{body}"""
'''
"statistics": {
  "total_requirements": 146,
  "requirements_with_change_files": 66,
  "requirements_with_at_least_one_hit": 41,
  "total_change_files": 187,
  "total_hit_files": 50,
  "top_k": 5,
  "overall_recall": 0.26737967914438504
}


# prompt2

## Role
You are an expert Java software architect and search engine engineer. Your task is to transform a GitHub Issue into a highly dense, technical search query optimized for vector-based code retrieval (using jina-code models).

## Objective
Generate a retrieval query that acts as a "semantic bridge" between natural language requirements and Java method implementations. The query should mimic a professional Java Docstring or an API specification.

## Classification Guide
- BUG: Fixes for crashes, logic errors, or unexpected side effects.
- FR (Feature Request): New methods, APIs, or extended functionality.
- NFR (Non-Functional): Optimization (speed/memory), thread-safety, security, refactoring.
- CHORE/DOCS/QUESTION: Maintenance, documentation, or clarification.

## Retrieval Query Construction Rules (Critical for Jina-Code)
1. **Technical Entity Extraction**: 
   - Mandatory: ClassName, MethodName, Exception types (e.g., `IllegalArgumentException`).
   - Signature details: Parameter types (`List<String>`, `Stream`), Return types (`Optional<T>`, `void`).
2. **Behavioral Mapping**:
   - Describe the *algorithm* or *logic* (e.g., "sliding window", "recursive descent", "bitmasking").
   - Define the *contract*: Input state -> Transformation -> Output state.
3. **Keyword Enrichment**: Use industry-standard verbs: `serialize`, `instantiate`, `traverse`, `validate`, `mutate`, `synchronize`.
4. **Noise Reduction**: Remove all "human" context (e.g., "I think we should", "Our team noticed", "Fixes #123").
5. **Structural Format**: 
   - Format: `[Action] [Class].[method]([params]) -> [Returns]: [Technical Logic Description]`

## Output Format (Strict JSON)
{{
  "reason": "Brief technical analysis of the issue's core requirement.",
  "category": "BUG | FR | NFR | CHORE | DOCS | QUESTION",
  "search_query": "The optimized string for jina-code embedding."
}}

## Issue Data
Title: """{title}"""
Body: """{body}"""
'''
  "statistics": {
    "total_requirements": 146,
    "requirements_with_change_files": 66,
    "requirements_with_at_least_one_hit": 46,
    "total_change_files": 187,
    "total_hit_files": 57,
    "top_k": 5,
    "overall_recall": 0.3048128342245989
  }


# prompt3


'''
### Role
You are a Senior Technical Architect and TLR (Traceability Link Recovery) Specialist. Your goal is to transform messy GitHub issues into high-density "Technical Retrieval Queries" that will be converted into vectors for matching source code.

### Task
1. [Information Denoising]: 
   - Discard inherent template headers (e.g., "### 1. What are you trying to do?", "### Concrete Use Cases").
   - Discard standard community noise (e.g., "I agree to follow the code of conduct", "I have read the guidelines", "Thanks in advance").
   - Discard greetings and meta-discussions.
2. [Requirement Classification]: Categorize the issue strictly.
3. [Feature Alignment for Embedding]: Rewrite the core implementation delta into a docstring-style requirement.

### TLR Summarization Rules
- **Preserve Hard Entities**: Keep Package names, Class names, and Method signatures EXACTLY as they appear (e.g., `com.google.common.collect`, `ImmutableSet.Builder`, `reverse()`).
- **Standard Implementation Delta**: Focus on "What code should be added/changed" and "Where". 
- **Javadoc Style**: Write the summary as if it were a high-level comment describing the target code block.
- **Language**: English only for the summary.
- **Constraint**: No conversational filler. Maximum 40 words.

### Output Format (JSON Only)
{{
"reason": "Briefly list the extracted code entities and the core logic change after removing templates.",
"category": "BUG | FR | NFR | DOCS | CHORE | QUESTION | INVALID",
"search_query": "Docstring-style technical requirement (e.g., 'Add reverse(ImmutableIntArray) to com.google.common.primitives to provide a reversed view of primitive arrays without copying.')"
}}

Issue Title: """{title}"""
Issue Body: """{body}"""
'''

"statistics": {
  "total_requirements": 146,
  "requirements_with_change_files": 66,
  "requirements_with_at_least_one_hit": 43,
  "total_change_files": 187,
  "total_hit_files": 52,
  "top_k": 5,
  "overall_recall": 0.27807486631016043
}

# prompt4


'''
## Role
You are a Senior Java Technical Lead. Your task is to transform a GitHub Issue into a **Hybrid Technical Query** that combines a formal API specification with detailed implementation logic.

## Objective
The goal is to match the `original_code` in a vector index. The query should sound like a **professional Java Docstring** mixed with **specific internal implementation details**.

## Construction Rules (Critical for Recall)
1. **Header**: Always start with the exact [Original Issue Title].
2. **Method Signature (The "Where")**: Construct a formal Java signature: `[Modifiers] [ReturnType] [Class].[Method]([Parameters]) [Throws]`.
3. **Implementation Logic (The "What")**: Describe the logic using technical tokens. 
   - Use high-signal verbs: `traverse`, `synchronize`, `mutate`, `validate`, `instantiate`.
   - Include internal logic patterns: `switch-case on enum`, `recursive descent`, `bitmask manipulation`, `try-catch block`.
4. **Preserve Hard Entities**: Keep all original identifiers (e.g., `BigInteger`, `ImmutableList`, `RoundingMode`) and error messages.
5. **No Conversational Noise**: Exclude "The user wants", "I suggest". Use direct, declarative technical language.

## Classification Guide
- BUG | FR | NFR | CHORE | DOCS | QUESTION

## Output Format (Strict JSON)
{{
  "reason": "Technical rationale for extracted entities.",
  "category": "BUG | FR | NFR | CHORE | DOCS | QUESTION",
  "search_query": "[Original Title]. [Java Signature]. [Technical Logic Description with predicted code tokens]."
}}

## Issue Data
Title: """{title}"""
Body: """{body}"""
'''

"statistics": {
  "total_requirements": 146,
  "requirements_with_change_files": 66,
  "requirements_with_at_least_one_hit": 44,
  "total_change_files": 187,
  "total_hit_files": 51,
  "top_k": 5,
  "overall_recall": 0.2727272727272727
}

# prompt5

'''
## Role
You are an expert Java software architect and search engine engineer. Your task is to transform a GitHub Issue into a highly dense, technical search query optimized for vector-based code retrieval (using jina-code models).

## Objective
Generate a retrieval query that acts as a "semantic bridge" between natural language requirements and Java method implementations. The query should mimic a professional Java Docstring or an API specification.

## Classification Guide
- BUG: Fixes for crashes, logic errors, or unexpected side effects.
- FR (Feature Request): New methods, APIs, or extended functionality.
- NFR (Non-Functional): Optimization (speed/memory), thread-safety, security, refactoring.
- CHORE/DOCS/QUESTION: Maintenance, documentation, or clarification.

## Retrieval Query Construction Rules (Critical for Jina-Code)
1. **Technical Entity Extraction**:
   - Mandatory: ClassName, MethodName, Exception types (e.g., `IllegalArgumentException`).
   - Signature details: Parameter types (`List<String>`, `Stream`), Return types (`Optional<T>`, `void`).
2. **Behavioral Mapping**:
   - Describe the *algorithm* or *logic* (e.g., "sliding window", "recursive descent", "bitmasking").
   - Define the *contract*: Input state -> Transformation -> Output state.
3. **Keyword Enrichment**: Use industry-standard verbs: `serialize`, `instantiate`, `traverse`, `validate`, `mutate`, `synchronize`.
4. **Noise Reduction**: Remove all "human" context (e.g., "I think we should", "Our team noticed", "Fixes #123").
5. **Structural Format**:
   - Format: `[Action] [Class].[method]([params]) -> [Returns]: [Technical Logic Description]`

## Output Format (Strict JSON)
{{
"reason": "Brief technical analysis of the issue's core requirement.",
"category": "BUG|FR|NFR|DOCS|CHORE|QUESTION|INVALID",
"search_query": "The optimized string for jina-code embedding."
}}

## Issue Data
Title: """{title}"""
Body: """{body}"""
'''

"statistics": {
  "total_requirements": 146,
  "requirements_with_change_files": 66,
  "requirements_with_at_least_one_hit": 46,
  "total_change_files": 187,
  "total_hit_files": 54,
  "top_k": 5,
  "overall_recall": 0.2887700534759358
}


# prompt6
'''
## Role
You are an expert Java software architect and TLR retrieval engineer.

## Objective
Transform a GitHub Issue into a **high-recall hybrid retrieval query** that maximizes overlap with real Java source code for vector retrieval (jina-code).

The query must act as BOTH:
1. A formal API/docstring description
2. A dense bag of code-like tokens and implementation patterns

---

## Classification Guide
- BUG | FR | NFR | CHORE | DOCS | QUESTION | INVALID

---

## Retrieval Query Construction Rules (CRITICAL)

### 1. Technical Entity Extraction (MANDATORY)
Extract and preserve:
- Class names, method names
- Parameter types (`List<String>`, `Map<K,V>`)
- Return types (`boolean`, `Optional<T>`)
- Exception types (`IllegalArgumentException`, `NullPointerException`)

---

### 2. Signature + Contract (STRUCTURED CORE)
Always include a Java-like signature:

[Modifiers] [ReturnType] Class.method(params) throws Exception

Then describe:
Input → Processing → Output

---

### 3. Implementation Mimicry (BOOST RECALL)
Predict actual Java code patterns:

Include tokens like:
- control flow: `if`, `else`, `switch`, `for`, `while`
- null handling: `null`, `Objects.requireNonNull`
- error handling: `throw new`, `try-catch`
- common APIs: `stream()`, `map()`, `filter()`, `collect()`
- data ops: `add`, `remove`, `contains`, `get`, `put`

---

### 4. Synonym & Expansion (CRITICAL FOR RECALL)
Expand key concepts into likely alternatives:

Example:
- "check" → `validate`, `verify`, `ensure`
- "convert" → `parse`, `transform`, `map`
- "power of two" → `isPowerOfTwo`, `bitCount`, `shiftLeft`

---

### 5. Error & Edge Cases (VERY IMPORTANT)
Include:
- boundary conditions (`empty`, `null`, `zero`)
- exception scenarios
- typical bug patterns (overflow, index out of bounds)

---

### 6. Hybrid Output Format (REQUIRED)

Final query MUST be ONE string combining:

[Action + Signature]  
+ [Core Logic Description]  
+ [Implementation Tokens]  
+ [Synonym Expansion Tokens]

Avoid natural conversation.

---

## Output Format (Strict JSON)

{{
  "reason": "Brief technical analysis of extracted entities and predicted implementation.",
  "category": "BUG | FR | NFR | CHORE | DOCS | QUESTION | INVALID",
  "search_query": "Hybrid high-recall query"
}}

---

## Issue Data
Title: """{title}"""
Body: """{body}"""
'''

"statistics": {
  "total_requirements": 146,
  "requirements_with_change_files": 66,
  "requirements_with_at_least_one_hit": 43,
  "total_change_files": 187,
  "total_hit_files": 53,
  "top_k": 5,
  "overall_recall": 0.28342245989304815
}

# prompt7

## Role
You are an expert Java software architect and search engine engineer. Your task is to transform a GitHub Issue into a highly dense, technical search query optimized for vector-based code retrieval (using jina-code models).

## Objective
Generate a retrieval query that acts as a "semantic bridge" between natural language requirements and Java method implementations. The query should mimic a professional Java Docstring or an API specification.

## Classification Guide
- BUG: Fixes for crashes, logic errors, or unexpected side effects.
- FR (Feature Request): New methods, APIs, or extended functionality.
- NFR (Non-Functional): Optimization (speed/memory), thread-safety, security, refactoring.
- CHORE/DOCS/QUESTION: Maintenance, documentation, or clarification.

## Retrieval Query Construction Rules (Critical for Jina-Code)
1. **Technical Entity Extraction**:
   - Mandatory: ClassName, MethodName, Exception types (e.g., `IllegalArgumentException`).
   - Signature details: Parameter types (`List<String>`, `Stream`), Return types (`Optional<T>`, `void`).
2. **Behavioral Mapping**:
   - Describe the *algorithm* or *logic* (e.g., "sliding window", "recursive descent", "bitmasking").
   - Define the *contract*: Input state -> Transformation -> Output state.
3. **Keyword Enrichment**: Use industry-standard verbs: `serialize`, `instantiate`, `traverse`, `validate`, `mutate`, `synchronize`.
4. **Noise Reduction**: Remove all "human" context (e.g., "I think we should", "Our team noticed", "Fixes #123").
5. **Structural Format**:
   - Format: `[Action] [Class].[method]([params]) -> [Returns]: [Technical Logic Description]`

## Output Format (Strict JSON)
{{
  "reason": "Brief technical analysis of the issue's core requirement.",
  "category": "BUG|FR|NFR|DOCS|CHORE|QUESTION|INVALID",
  "search_query": "The optimized string for jina-code embedding."
}}

## Issue Data
Title: """{title}"""
Body: """{body}"""
'''

"statistics": {
  "total_requirements": 66,
  "requirements_with_change_files": 66,
  "requirements_with_at_least_one_hit": 42,
  "total_change_files": 187,
  "total_hit_files": 51,
  "top_k": 5,
  "overall_recall": 0.2727272727272727
}

# prompt8

'''
## Role
You are a GitHub Issue preprocessor. Your task is to clean the issue content by removing only template sentences while preserving all original user content.

## Objective
Keep the original issue content intact, only remove the template sentences that appear in GitHub issue templates across different repositories.

## Template Sentence Characteristics (REMOVE THESE)
1. **Section Headers**: Lines starting with ### or ## that are part of the template structure
   - Examples: "### Description", "### Steps to Reproduce", "### Expected Behavior"
   - Examples: "## What are you trying to do?", "## Feature Request"

2. **Checklist Items**: Lines starting with "- [x]" or "- [ ]" that are part of template checklists
   - Examples: "- [x] I agree to follow the code of conduct"
   - Examples: "- [ ] This is not a duplicate issue"

3. **Template Instructions**: Sentences that provide instructions for filling out the issue
   - Examples: "Please describe the bug below"
   - Examples: "Include steps to reproduce the issue"

4. **Standard Template Phrases**: Common template phrases found across repositories
   - Examples: "What's the best code you can write to accomplish that without the new feature?"
   - Examples: "What would that same code look like if we added your feature?"

5. **Links**: URLs and hyperlinks
   - Examples: "https://github.com/user/repo/issues/123"
   - Examples: "[code of conduct](https://example.com)"

6. **Issue References**: References to other issues or pull requests
   - Examples: "Fixes #123", "Closes #456", "Related to #789"
   - Examples: "This fixes issue #2211", "See PR #345"

## Instructions
1. **Preserve ALL original user content** except template sentences that match the characteristics above
2. **Do NOT summarize** or change any technical content, code snippets, error messages, or user-provided information
3. **Keep the original formatting** (newlines, code blocks, indentation, etc.)
4. **Classify** the issue according to the categories below

## Classification Guide
- BUG: Crashes, errors, unexpected behavior
- FR: New features, new methods, new APIs
- NFR: Performance, thread-safety, security, refactoring
- DOCS: Documentation only
- CHORE: CI/CD, dependencies, build scripts
- QUESTION: How-to, support requests
- INVALID: Spam, empty

## Output Format (Strict JSON)
{{
  "reason": "Brief explanation of template sentences removed.",
  "category": "BUG|FR|NFR|DOCS|CHORE|QUESTION|INVALID",
  "search_query": "Cleaned issue content with template sentences removed."
}}

## Issue Data
Title: """{title}"""
Body: """{body}"""
'''
"statistics": {
  "total_requirements": 66,
  "requirements_with_change_files": 66,
  "requirements_with_at_least_one_hit": 44,
  "total_change_files": 187,
  "total_hit_files": 53,
  "top_k": 5,
  "overall_recall": 0.28342245989304815
}


# prompt9_varA

''' 
## Role
You are a Java code search query generator.

## Task
Transform the GitHub issue into a structured code retrieval query.

## STRICT OUTPUT FORMAT (MUST FOLLOW)
```
[Action] [Class].[method]([params]) -> [Returns]: [Technical Logic]
```

## Rules
1. Extract: ClassName, MethodName, Parameter types, Return type
2. Keep all technical identifiers exactly as they appear
3. Use verbs: Add, Implement, Fix, Optimize, Refactor
4. Remove: Links, greetings, template headers, issue references

## JSON Output
{{
  "reason": "Brief technical analysis.",
  "category": "BUG|FR|NFR|DOCS|CHORE|QUESTION|INVALID",
  "search_query": "Your query in the EXACT format: [Action] [Class].[method]([params]) -> [Returns]: [Technical Logic]"
}}

## Issue Data
Title: """{title}"""
Body: """{body}"""
'''
"statistics": {
  "total_requirements": 66,
  "requirements_with_change_files": 66,
  "requirements_with_at_least_one_hit": 44,
  "total_change_files": 187,
  "total_hit_files": 52,
  "top_k": 5,
  "overall_recall": 0.27807486631016043
}


# prompt9_varB

''' 
## Role
You are a Java code search expert. Transform GitHub issues into search queries that closely mimic actual Java source code to maximize vector similarity with code embeddings.

## Task
Generate a retrieval query that will have HIGH VECTOR SIMILARITY with real Java method implementations.

## Strategy: Code Pattern Mimicry
The search query should look like actual Java code that would implement the feature/fix described in the issue.

## Rules
1. **Mimic Real Code Structure**:
   - Use Java method signatures: `returnType methodName(paramType param)`
   - Include actual Java keywords: `public`, `static`, `void`, `return`, `if`, `for`, `try`
   - Use real code patterns: `Objects.requireNonNull()`, `checkArgument()`, `throw new`

2. **Preserve ALL Technical Terms**:
   - Class names, method names, variable names exactly as mentioned
   - Generic types: `<T>`, `<K, V>`, `<? extends Foo>`
   - Annotations: `@Nullable`, `@GuardedBy`, `@VisibleForTesting`

3. **Include Implementation Details**:
   - Control flow: loops, conditionals, exception handling
   - Common operations: `add()`, `remove()`, `get()`, `put()`, `contains()`
   - Stream operations: `stream()`, `map()`, `filter()`, `collect()`

4. **Output Format**:
   - First: Brief technical analysis
   - Then: A query that reads like Java code comments mixed with pseudo-code

## JSON Output
{{
  "reason": "Brief analysis of what code patterns to search for.",
  "category": "BUG|FR|NFR|DOCS|CHORE|QUESTION|INVALID",
  "search_query": "Query that mimics Java code structure and includes key technical terms, method signatures, and implementation patterns"
}}

## Issue Data
Title: """{title}"""
Body: """{body}"""
'''
"statistics": {
  "total_requirements": 66,
  "requirements_with_change_files": 66,
  "requirements_with_at_least_one_hit": 45,
  "total_change_files": 187,
  "total_hit_files": 55,
  "top_k": 5,
  "overall_recall": 0.29411764705882354
}


# prompt9_varC

''' 
## Role
You are a code retrieval expert. Transform GitHub issues into search queries that combine the original issue title with extracted technical details.

## Task
Create a search query that:
1. STARTS with the original issue title (keep it intact)
2. APPENDS extracted technical entities and implementation details

## Why This Works
- Original title contains key class/method names in natural order
- Appended technical details add semantic richness for vector search
- Combined query matches both exact names and conceptual patterns

## Extraction Rules
1. **Keep Original Title** - Do not modify the title, use it as the query prefix
2. **Extract from Body**:
   - Class names (e.g., `CacheBuilder`, `ImmutableList`)
   - Method names (e.g., `memoizeWithExpiration`, `build`)
   - Parameter types (e.g., `Duration`, `Supplier<T>`)
   - Return types (e.g., `boolean`, `Optional<T>`)
   - Key technical terms and algorithms

3. **Remove from Body**:
   - URLs and markdown links
   - Issue references (`Fixes #123`)
   - Template headers (`### Description`)
   - Greetings and signatures

## Output Format
Combine title + extracted technical details in a flowing description:
`Original Title: Technical details with class names, methods, and implementation patterns.`

## JSON Output
{{
  "reason": "Brief analysis of the technical requirement.",
  "category": "BUG|FR|NFR|DOCS|CHORE|QUESTION|INVALID",
  "search_query": "Original issue title followed by extracted technical entities and implementation details"
}}

## Issue Data
Title: """{title}"""
Body: """{body}"""
'''
"statistics": {
  "total_requirements": 66,
  "requirements_with_change_files": 66,
  "requirements_with_at_least_one_hit": 43,
  "total_change_files": 187,
  "total_hit_files": 51,
  "top_k": 5,
  "overall_recall": 0.2727272727272727
}


# prompt9_varD

''' 
## Role
You are an expert Java software architect. Transform GitHub issues into professional API documentation-style search queries.

## Objective
Generate a retrieval query that reads like a Java method's Javadoc or API specification. This format has high semantic similarity with actual Java source code.

## Classification Guide
- BUG: Fixes for crashes, logic errors, unexpected behavior
- FR: New methods, APIs, or extended functionality
- NFR: Performance, thread-safety, security, refactoring
- DOCS: Documentation improvements
- CHORE: Maintenance tasks
- QUESTION: Clarification requests
- INVALID: Not a valid issue

## Query Construction Rules
1. **Technical Entity Extraction**:
   - ClassName, MethodName (exact spelling)
   - Parameter types: `List<String>`, `Map<K,V>`, `Duration`
   - Return types: `boolean`, `Optional<T>`, `void`
   - Exception types: `IllegalArgumentException`, `NullPointerException`

2. **Behavioral Description**:
   - Describe the contract: what input → what output
   - Include edge cases and constraints
   - Mention validation logic

3. **Format as Javadoc Style**:
   ```
   [Action] [Class].[method]([params]) -> [Returns]: [Description]
   ```

4. **Keyword Enrichment**:
   Use verbs: `returns`, `throws`, `checks`, `validates`, `converts`, `creates`

5. **Noise Reduction**:
   Remove: URLs, issue references, greetings, template headers

## JSON Output
{{
  "reason": "Brief technical analysis of the issue's core requirement.",
  "category": "BUG|FR|NFR|DOCS|CHORE|QUESTION|INVALID",
  "search_query": "API-style description: [Action] [Class].[method]([params]) -> [Returns]: [Technical logic with validation and edge cases]"
}}

## Issue Data
Title: """{title}"""
Body: """{body}"""
'''
"statistics": {
  "total_requirements": 66,
  "requirements_with_change_files": 66,
  "requirements_with_at_least_one_hit": 46,
  "total_change_files": 187,
  "total_hit_files": 57,
  "top_k": 5,
  "overall_recall": 0.3048128342245989
}


# prompt9_varE

''' 
## Role
You are a vector search optimization expert. Your goal is to maximize token overlap between the query and Java source code for better vector similarity.

## Strategy: Keyword Density Maximization
Generate a query with HIGH DENSITY of technical terms that will appear in actual Java code.

## Rules
1. **Extract ALL technical identifiers** from the issue:
   - Every class name mentioned
   - Every method name mentioned
   - Every parameter type
   - Every return type
   - Every exception type

2. **Include Java keywords** that appear in implementations:
   - `public`, `static`, `final`, `void`, `return`
   - `if`, `else`, `for`, `while`, `try`, `catch`
   - `new`, `this`, `super`, `null`, `true`, `false`

3. **Add common method verbs** from Java libraries:
   - `get`, `set`, `add`, `remove`, `put`, `contains`
   - `create`, `build`, `parse`, `format`, `validate`
   - `check`, `ensure`, `require`, `assert`

4. **Include Guava-specific patterns**:
   - `checkNotNull`, `checkArgument`, `checkState`
   - `Immutable`, `Builder`, `Factory`
   - `Supplier`, `Function`, `Predicate`

5. **Format**: Space-separated dense keyword string
   Example: `ClassName methodName paramType returnType check validate Builder create`

## JSON Output
{{
  "reason": "Analysis of key technical terms for dense keyword extraction.",
  "category": "BUG|FR|NFR|DOCS|CHORE|QUESTION|INVALID",
  "search_query": "Dense space-separated keywords: class names method names types Java keywords Guava patterns action verbs"
}}

## Issue Data
Title: """{title}"""
Body: """{body}"""
'''
"statistics": {
  "total_requirements": 66,
  "requirements_with_change_files": 66,
  "requirements_with_at_least_one_hit": 42,
  "total_change_files": 187,
  "total_hit_files": 51,
  "top_k": 5,
  "overall_recall": 0.2727272727272727
}


# prompt9_varF

''' 
## Role
You are a semantic code matching expert. Transform issues into subject-verb-object triplets that match code structure.

## Strategy: Semantic Triplet Extraction
Code methods naturally follow Subject(Class)-Verb(Method)-Object(Parameters) patterns.

## Rules
1. **Identify the Subject (Class)**:
   - Main class being modified/used
   - Factory/Builder classes
   - Utility classes mentioned

2. **Identify the Verb (Action)**:
   - Method being added/modified
   - Action being performed
   - Use present tense verbs: creates, returns, validates, transforms

3. **Identify the Object (Target)**:
   - Parameters being processed
   - Return value type
   - Side effects or state changes

4. **Create Multiple Triplets**:
   - Primary: Main feature being requested
   - Secondary: Related operations
   - Tertiary: Edge cases or constraints

5. **Format as Flowing Description**:
   Combine triplets into natural language that mirrors code documentation:
   `Subject verb object with parameters and return type handling exceptions`

## JSON Output
{{
  "reason": "Triplet analysis: Subject (class), Verb (method), Object (params/return).",
  "category": "BUG|FR|NFR|DOCS|CHORE|QUESTION|INVALID",
  "search_query": "Flowing description combining subject-verb-object triplets with class names method names parameter types and return types"
}}

## Issue Data
Title: """{title}"""
Body: """{body}"""
'''
"statistics": {
  "total_requirements": 66,
  "requirements_with_change_files": 66,
  "requirements_with_at_least_one_hit": 45,
  "total_change_files": 187,
  "total_hit_files": 54,
  "top_k": 5,
  "overall_recall": 0.2888
}


# prompt9_varG

''' 
## Role
You are a code context analysis expert. Transform GitHub issues into search queries that capture not just what code does, but how it interacts with other code.

## Strategy: Context-Aware Query Generation
Generate queries that include:
1. The primary class/method being discussed
2. Related classes that would interact with it
3. Common usage patterns and call sequences
4. Expected behavior in different contexts

## Extraction Rules
1. **Primary Entity**: Main class or method mentioned in the issue
2. **Related Entities**: Classes that would use, extend, or be used by the primary entity
3. **Usage Patterns**: Common method call sequences (e.g., `builder().setX().build()`)
4. **Context Clues**: Where this code would typically be called from

3. **Implementation Hints**: Any specific algorithms, data structures, or design patterns mentioned

## Output Format
Create a query that describes:
- The main entity and its purpose
- Related classes and their relationships
- Typical usage scenarios
- Key methods involved in the workflow

## JSON Output
{{
  "reason": "Analysis of code context, relationships, and usage patterns.",
  "category": "BUG|FR|NFR|DOCS|CHORE|QUESTION|INVALID",
  "search_query": "Description of primary entity, related classes, usage patterns, and contextual relationships for code retrieval"
}}

## Issue Data
Title: """{title}"""
Body: """{body}"""
'''
"statistics": {
  "total_requirements": 66,
  "requirements_with_change_files": 66,
  "requirements_with_at_least_one_hit": 46,
  "total_change_files": 187,
  "total_hit_files": 54,
  "top_k": 5,
  "overall_recall": 0.2887700534759358
}


# prompt9_varH

''' 
## Role
You are a software architecture expert. Transform GitHub issues into search queries that work across multiple levels of abstraction - from high-level concepts to concrete implementations.

## Strategy: Multi-Level Abstraction
Generate queries that include terms from three levels:
1. **Conceptual Level**: Abstract concepts and design patterns
2. **Interface Level**: Public APIs, interfaces, and abstract classes
3. **Implementation Level**: Concrete classes and method implementations

## Extraction Rules
1. **Conceptual Terms**: Design patterns (Factory, Builder, Strategy), architectural concepts
2. **Interface Terms**: Interface names, abstract class names, public method signatures
3. **Implementation Terms**: Concrete class names, private methods, internal data structures
4. **Bridge Terms**: Words that connect levels (e.g., 'implements', 'extends', 'uses')

## Output Format
Combine all three levels into a comprehensive query:
`Conceptual pattern + Interface definition + Implementation details`

## JSON Output
{{
  "reason": "Multi-level analysis: conceptual patterns, interfaces, and implementations.",
  "category": "BUG|FR|NFR|DOCS|CHORE|QUESTION|INVALID",
  "search_query": "Conceptual design patterns, interface definitions, and concrete implementation details combined"
}}

## Issue Data
Title: """{title}"""
Body: """{body}"""
'''
"statistics": {
  "total_requirements": 66,
  "requirements_with_change_files": 66,
  "requirements_with_at_least_one_hit": 42,
  "total_change_files": 187,
  "total_hit_files": 49,
  "top_k": 5,
  "overall_recall": 0.2620320855614973
}


# prompt9_varI

''' 
## Role
You are a developer intent analyzer. Transform GitHub issues into search queries that capture the underlying developer intent and goals, not just technical details.

## Strategy: Intent Extraction
Understand what the developer wants to achieve and express it in terms that match code structure:
1. **Goal**: What is the developer trying to accomplish?
2. **Action**: What operation needs to be performed?
3. **Target**: What data or object is being operated on?
4. **Constraint**: What limitations or requirements exist?

## Extraction Rules
1. **Goal Phrases**: 'enable X', 'allow Y to Z', 'support W'
2. **Action Verbs**: Add, Remove, Update, Validate, Transform, Convert
3. **Target Objects**: The main class, data structure, or component
4. **Constraint Terms**: Thread-safe, immutable, nullable, async

## Output Format
Express the query as: `[Goal] by [Action] on [Target] with [Constraints]`

## JSON Output
{{
  "reason": "Developer intent: goal, action, target, and constraints analysis.",
  "category": "BUG|FR|NFR|DOCS|CHORE|QUESTION|INVALID",
  "search_query": "Developer intent expressed as goal, action on target with constraints"
}}

## Issue Data
Title: """{title}"""
Body: """{body}"""
'''
"statistics": {
  "total_requirements": 66,
  "requirements_with_change_files": 66,
  "requirements_with_at_least_one_hit": 44,
  "total_change_files": 187,
  "total_hit_files": 51,
  "top_k": 5,
  "overall_recall": 0.2727272727272727
}


# prompt9_varJ

''' 
## Role
You are a semantic role labeling expert for code. Transform GitHub issues into structured queries using semantic roles that map well to code structure.

## Strategy: Semantic Role Extraction
Identify these semantic roles in the issue:
1. **Actor**: Who/what performs the action? (Class, Component, System)
2. **Action**: What is being done? (Method, Operation, Process)
3. **Theme**: What is being acted upon? (Data, Object, Parameter)
4. **Location**: Where does this happen? (Package, Module, Context)
5. **Manner**: How is it done? (Algorithm, Pattern, Strategy)
6. **Purpose**: Why is it done? (Goal, Intent, Use case)

## Extraction Rules
1. **Actor**: Subject of the sentence, usually a class or component name
2. **Action**: Main verb describing the operation
3. **Theme**: Object being processed or modified
4. **Location**: Context, environment, or scope
5. **Manner**: Implementation approach or technique
6. **Purpose**: The benefit or goal being achieved

## Output Format
Combine roles into a natural language query:
`Actor performs Action on Theme in Location using Manner for Purpose`

## JSON Output
{{
  "reason": "Semantic role analysis: Actor, Action, Theme, Location, Manner, Purpose.",
  "category": "BUG|FR|NFR|DOCS|CHORE|QUESTION|INVALID",
  "search_query": "Actor Action Theme Location Manner Purpose combined for semantic code matching"
}}

## Issue Data
Title: """{title}"""
Body: """{body}"""
'''
"statistics": {
  "total_requirements": 66,
  "requirements_with_change_files": 66,
  "requirements_with_at_least_one_hit": 45,
  "total_change_files": 187,
  "total_hit_files": 56,
  "top_k": 5,
  "overall_recall": 0.2994652406417112
}


# prompt9_varK

''' 
## Role
You are a code evolution analyst. Transform GitHub issues into search queries that capture the transformation from current state to desired state.

## Strategy: Evolution-Aware Query Generation
Understand the change as a transition:
1. **Current State**: What exists now (for bugs: problematic code; for features: missing functionality)
2. **Desired State**: What should exist after the change
3. **Transformation**: What operations achieve this change
4. **Impact**: What other code is affected

## Extraction Rules
1. **Before Terms**: Current implementation, existing behavior, problematic code
2. **After Terms**: Desired behavior, new functionality, expected output
3. **Change Operations**: Add, Modify, Remove, Refactor, Optimize
4. **Impact Scope**: Related classes, dependent modules, affected APIs

## Output Format
Describe the evolution: `Transform [Current] to [Desired] by [Operations] affecting [Impact]`

## JSON Output
{{
  "reason": "Code evolution: Current state to desired state transformation analysis.",
  "category": "BUG|FR|NFR|DOCS|CHORE|QUESTION|INVALID",
  "search_query": "Code evolution from current state to desired state with transformation operations and impact scope"
}}

## Issue Data
Title: """{title}"""
Body: """{body}"""
'''
"statistics": {
  "total_requirements": 66,
  "requirements_with_change_files": 66,
  "requirements_with_at_least_one_hit": 42,
  "total_change_files": 187,
  "total_hit_files": 52,
  "top_k": 5,
  "overall_recall": 0.27807486631016043
}