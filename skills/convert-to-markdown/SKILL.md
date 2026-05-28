---
name: convert-to-markdown
description: Convert raw text content into clean, properly formatted markdown while preserving all original content
license: MIT
metadata:
  audience: researchers
  workflow: content
---

# Markdown Formatter

Specialized skill for converting raw text content into clean, properly formatted markdown while preserving all original content exactly.

## When to Load This Skill

Load this skill when the user wants to:

- Convert raw text to clean markdown
- Format unstructured content into markdown
- Clean up formatted text
- Convert transcripts into readable markdown
- Reformat articles or documents into markdown

**Trigger phrases**:

- "convert to markdown"
- "format as markdown"
- "clean up this text"
- "format this content"
- "make this into markdown"
- User provides raw unformatted text or transcript

## Content Types Handled

- Articles and blog posts
- Transcripts (videos, podcasts, meetings)
- Documentation
- Research papers
- Email content
- Any raw text content that needs formatting

## How to Use This Skill

1. **Gather content**: Get the raw text content
2. **Identify structure**: Determine the natural organization of the content
3. **Apply prompt template**: Use the following prompt to format the content
4. **Return output**: Provide clean, properly formatted markdown

## Prompt Template

Use this prompt template when converting content to markdown:

```
# Identity

You are an expert format converter specializing in converting content to clean Markdown. Your job is to ensure that the COMPLETE original post is preserved and converted to markdown format, with no exceptions.

# Steps

1. Read through the content multiple times to determine the structure and formatting.
2. Clearly identify the original content within the surrounding noise, such as ads, comments, or other unrelated text.
3. Perfectly and completely replicate the content as Markdown, ensuring that all original formatting, links, and code blocks are preserved.
4. Output the COMPLETE original content in Markdown format.

# Instructions

- DO NOT abridge, truncate, or otherwise alter the original content in any way. Your task is to convert the content to Markdown format while preserving the original content in its entirety.

- DO NOT insert placeholders such as "content continues below" or any other similar text. ALWAYS output the COMPLETE original content.

- When you're done outputting the content in Markdown format, check the original content and ensure that you have not truncated or altered any part of it.

- If the input is just a transcript, INSERT markdown headers so that it is easy to follow along.

# Notes

- Keep all original content wording exactly as it was
- Keep all original punctuation exactly as it is
- Keep all original links
- Keep all original quotes and code blocks
- ONLY convert the content to markdown format
- CRITICAL: Your output will be compared against the work of an expert human performing the same exact task. Do not make any mistakes in your perfect reproduction of the original content in markdown.

{{ input }}
```

## Expected Output Format

The output should be:

- Pure markdown with no preamble or postamble
- Complete original content preserved exactly
- Proper markdown formatting applied
- All links, quotes, and code blocks maintained
- Easy to read with appropriate headers and structure

## Key Principles

1. **Complete Preservation**: Never truncate or summarize content
2. **Exact Wording**: Keep all original words and punctuation
3. **Proper Formatting**: Apply appropriate markdown syntax
4. **Structure Recognition**: Identify and preserve natural sections
5. **Cleanup Only**: Only add markdown formatting, do not edit content

## Integration Notes

- Works with any text content regardless of source
- Preserves URLs and external references
- Handles code blocks and quotes correctly
- Can process very long documents

## Special Features

- **Transcript Handling**: Adds helpful headers to make transcripts readable
- **Content Detection**: Identifies and isolates main content from surrounding noise
- **Link Preservation**: Maintains all original URLs and references
- **Code Block Protection**: Preserves code formatting and syntax highlighting
- **Quote Handling**: Properly formats quotes and blockquotes
