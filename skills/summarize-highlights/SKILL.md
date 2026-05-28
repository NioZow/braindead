---
name: summarize-highlights
description: Convert book highlights, Kindle notes, and reading passages into structured comprehensive reference notes
license: MIT
metadata:
  audience: researchers
  workflow: content
---

# Book Highlights Synthesizer

Specialized skill for converting book highlights and reading notes into structured, comprehensive reference notes organized by the book's framework and key concepts.

## When to Load This Skill

Load this skill when the user wants to process:

- Kindle highlights
- Book quotes and passages
- Reading notes from books
- Highlighted passages from practical learning books

**Trigger phrases**:

- "book highlights"
- "kindle highlights"
- "process my highlights"
- "synthesis of notes"
- "book notes"
- "reading notes"
- "summarize these highlights"
- User provides list of book quotes/highlights

## Content Domains Covered

- **Technology & Programming**: Technical books, programming guides, software development
- **Business & Entrepreneurship**: Business strategy, startups, management, leadership
- **Productivity & Self-Development**: Habits, systems, mental models, productivity frameworks
- **Finance**: Investment books, trading strategies, financial literacy
- **Learning & Education**: Learning techniques, skill development, cognitive science
- Any practical, actionable non-fiction content

## How to Use This Skill

1. **Gather content**: Get the list of book highlights or reading notes
2. **Prepare metadata**: Extract book title and author if available
3. **Apply prompt template**: Use the following prompt with the highlights and book information
4. **Research context**: Optionally research the book for better organization
5. **Format output**: Return as book-focused structured markdown notes

## Prompt Template

Use this prompt template when processing book highlights:

````
# Task: Convert Book Highlights to Structured Reference Notes

You are helping process highlights from practical learning books into clean, organized markdown notes. These books cover topics like technology, cybersecurity, entrepreneurship, productivity, self development and business. Your goal is to create a comprehensive reference document that preserves key insights, strategies, and actionable advice.

## Book Information

- **Title**: {{ title }}
- **Author**: {{ author }}

## CRITICAL: Language Instruction

**The highlights below are in a specific language. You MUST write your entire response in the SAME language as the highlights.**

- If the highlights are in French, write all notes in French
- If the highlights are in English, write all notes in English
- If the highlights are in Spanish, write all notes in Spanish
- And so on for any other language

Detect the language from the highlights and match it exactly. Do NOT translate. Do NOT mix languages. The output language must match the input language of the highlights.

## Context Research Instructions

**Before processing the highlights, research this book to understand its context:**

1. Search for "{{ title }}" by {{ author }} to find:
   - Book summary and main themes
   - Chapter structure and organization
   - Key frameworks or methodologies presented
   - Author's background and expertise
   - Reception and key takeaways from reviews

2. Use this context to:
   - Better organize highlights according to the book's actual framework
   - Identify which highlights represent core concepts vs. supporting details
   - Add helpful context where highlights reference frameworks or terms from the book
   - Fill in gaps between highlights that might not be obvious standalone

3. If you find a table of contents or chapter list, use it to structure the notes logically.

**Important**: Conduct this research FIRST before organizing the highlights. If you cannot find information about the book, proceed with organizing highlights by natural themes that emerge from the content.

## Highlights to Process

{{ highlights }}

## Organization Guidelines

1. **Identify the book's framework**: Many practical books have a clear methodology (e.g., "7 habits", "4-step process"). Use this as your primary structure if it exists.

2. **Preserve actionable content**: Keep specific strategies, tactics, formulas, statistics, and step-by-step processes intact.

3. **Maintain data accuracy**: All numbers, percentages, dates, tool names, and technical terms must be preserved exactly.

4. **Create hierarchical structure**: Organize from big concepts down to specific tactics.

5. **Highlight key insights**: Use quotes for particularly powerful principles or frameworks.

6. **Add context where needed**: If your research revealed important context that makes a highlight clearer, add brief clarifying notes in [brackets].

7. **Skip redundancy**: If multiple highlights say the same thing, synthesize into one clear point.

8. **Create reference sections**: Include sections for tools mentioned, key statistics, important formulas, or resource lists.

## CRITICAL: Output Format

**OUTPUT ONLY THE MARKDOWN NOTES. DO NOT include any preamble, explanation, commentary, or concluding remarks. Do not say "Here are your notes" or "I've organized the highlights" or anything similar. Start directly with the markdown heading and end when the notes are complete. Your entire response should be valid markdown that can be saved directly to a .md file.**

**REMEMBER: Write everything in the same language as the highlights!**

Structure your notes based on what you learned about the book's framework. Use this general template but adapt based on the book's actual structure:

```markdown
# [Book Title] by [Author]

## Overview

[2-3 sentence summary of the book's main premise and approach, informed by your research]

## Core Framework

[If the book has a clear methodology/framework, describe it here]

## Key Concepts

### [Major Theme/Chapter 1]

[Brief context about this section if helpful]

- Key principle or insight
- Supporting details or examples
- Actionable tactics

> "[Memorable quote if applicable]"

**Tools/Resources mentioned:**

- Tool name: purpose/use case

### [Major Theme/Chapter 2]

[Continue organizing by the book's structure or natural themes...]

## Strategies & Tactics

### [Specific Area]

**Approach:** [How to do it]

**Steps:**

1. First step
2. Second step

**Key Metrics/Numbers:** [Any benchmarks or statistics]

## Tools & Resources

[Consolidated list of all tools, books, resources mentioned]

## Key Takeaways

[3-5 highest-level insights that capture the essence of the book]

## Action Items

[Concrete next steps you could take based on this book]
````

Please research the book first using available web tools, then process these highlights into well-organized markdown notes. Please process these highlights now, creating well-organized markdown notes.

```

## Expected Output Format

The output should be:
- Pure markdown with no preamble or postamble
- Organized according to the book's framework or chapter structure
- Preserved quotes, numbers, and specific details
- Well-organized sections including strategies, tools, key takeaways
- In the same language as the input highlights
- Saveable directly as a .md file

## Integration Notes

- Works with webfetch to research book context and structure
- Can handle multiple languages properly
- Inherits conversation context about the book
- Sensitive to preserving actionable content and frameworks

## Special Features

- **Framework Detection**: Identifies and uses the book's natural structure
- **Context Enhancement**: Researches book to add helpful context between highlights
- **Actionability Focus**: Preserves strategies, tactics, and step-by-step processes
- **Redundancy Handling**: Synthesizes duplicate points while preserving important details
```
