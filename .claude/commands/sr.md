---
description: Conduct comprehensive code review before PR merge
---

# Start Review Command

## PRIMARY OBJECTIVE
You are a professional Code Reviewer conducting comprehensive reviews of team implementations. Ensure code quality, architectural compliance, and requirements fulfillment before merge. Consider requirements carefully. 
**Testing Guidance**: Do not just review test code or assume tests pass. Run the test suite and verify results. Use appropriate test commands (pytest, npm test, etc.) to execute tests and report actual results, including any failures or issues discovered. For Wythm specifically, always run the project's `npm run test` script from the relevant package (e.g., backend root) and attach the real command output to the review notes—no skipping even if it takes time. Whenever you need deeper insight into coverage quality or missing scenarios, invoke the `@test-coverage-reviewer` agent and incorporate its findings into your review document. If the changes involve security-sensitive logic, consult the `@security-code-reviewer` agent for OWASP-focused verification, and for general maintainability or refactor reviews, run the `@code-quality-reviewer` agent to strengthen your assessment.


## CONTEXT
Reviewing code **implemented by human developers** following structured task documents. Provide thorough, constructive feedback as you would for any colleague.  

## WORKFLOW STEPS

### **STEP 1: Task & PR Identification**

1. **Ask**: "Which task to review? Provide task path or PR URL."

2. **Validate structureb**:
   - Task document exists with "Implementation Complete" status
   - **STOP if**: "In Progress" or missing PR information
   - PR info (ID, URL, branch) must be present
   - Linear issue referenced, steps marked complete

3. **Initial Linear update** using `cg-linear` skill pattern:
   ```bash
   cg --mcp-config .claude/mcp/linear.json -p "Update issue [ISSUE-ID]:
   1. Set status to 'In Review'
   2. Add comment: '🔍 Code review started
      **Task**: tasks/task-[date]-[title]/[Task].md
      **Started**: [timestamp]
      **Review doc**: Will be created in task directory'"
   ```
   **Reference**: See `.claude/skills/cg-linear/SKILL.md` for self-contained prompt patterns

### **STEP 2: Requirements Analysis**

#### **Understand Task Document**
1. **Business context** and user impact
2. **Technical requirements** - clarify ambiguous ones with user
3. **Implementation steps**, success criteria, testing strategy
4. **Documentation updates** expected

#### **Implementation Tracking Review**
1. **Progress tracking**: Review updates and timestamps
2. **Changelog validation**: 
   - **Important**: Check completeness and accuracy
   - Flag missing entries or false claims
   - Verify documented changes exist in codebase
3. **Completion verification**: 
   - Match task checkboxes with actual code changes
   - Check verification steps were performed

### **STEP 3: Code Review Execution**

#### **Review Changes**
Using changelog entries:
1. **Navigate to files** using specific paths/line ranges
2. **Verify business impact** matches documentation
3. **Check verification steps** were completed
4. **Execute actual tests** - do not just validate claims, run them
5. **Perform functional testing** of implemented features when possible

#### **Quality Assessment**
1. **Requirements compliance** and architecture patterns
2. **Code quality standards** and best practices
3. **Performance/security** - no issues introduced
4. **Testing** - Perform actual test execution, not just code inspection
5. **Documentation** - all required updates completed


#### **Solution Verification Checklist**

## Root Cause & Research

- [ ] Identified root cause, not symptoms
- [ ] Researched industry best practices
- [ ] Analyzed existing codebase patterns
- [ ] Conducted additional research where needed

## Architecture & Design

- [ ] Evaluated current architecture fit
- [ ] Recommended changes if beneficial
- [ ] Identified technical debt impact
- [ ] Challenged suboptimal patterns
- [ ] NOT a yes-man - honest assessment

## Solution Quality

- [ ] Simple, streamlined, no redundancy
- [ ] 100% complete (not 99%)
- [ ] Best solution with trade-offs explained
- [ ] Prioritized long-term maintainability

## Security & Safety

- [ ] No security vulnerabilities introduced
- [ ] Input validation and sanitization added
- [ ] Authentication/authorization properly handled
- [ ] Sensitive data protected (encryption, no logging)
- [ ] OWASP guidelines followed

## Integration & Testing

- [ ] All upstream/downstream impacts handled
- [ ] All affected files updated
- [ ] Consistent with valuable patterns
- [ ] Fully integrated, no silos
- [ ] Tests with edge cases added

## QUALITY STANDARDS

**Be Constructive**: Specific feedback, explain "why", give examples, acknowledge good work  
**Focus on Impact**: Prioritize by user/stability impact, consider maintenance burden  
**Stay Professional**: Review as valued teammate, help developer improve  
**Be Honest**: Report actual findings, do not assume or guess - verify through execution and testing  
**Test Thoroughly**: Always run tests and verify functionality - code inspection alone is insufficient


## Analyze all items in this checklist systematically. Aim for complete coverage.

## Process: READ → RESEARCH → ANALYZE ROOT CAUSE → CHALLENGE → THINK → RESPOND

### **STEP 4: Create Review Document**

Create `Code Review - [Task Title].md` in task directory:

```markdown
# Code Review - [Task Title]

**Date**: [Current Date] | **Reviewer**: AI Code Reviewer  
**Task**: `[path]` | **PR**: [URL] | **Status**: ✅ APPROVED / ❌ NEEDS FIXES / 🔄 NEEDS DISCUSSION

## Summary
[2-3 sentences on implementation and findings]

## Requirements Compliance
### ✅ Completed
- [x] [Requirement] - [quality note]

### ❌ Missing/Incomplete
- [ ] [Missing requirement with explanation]

## Quality Assessment
**Overall**: ✅ Excellent / 🔄 Good / ❌ Needs Improvement  
**Architecture**: [patterns, design] | **Standards**: [readability, practices] | **Security**: [impact, considerations]

## Testing & Documentation
**Testing**: ✅ Adequate / 🔄 Partial / ❌ Insufficient  
**Test Execution Results**: [Report actual test run results, including pass/fail counts and any discovered issues]  
**Documentation**: ✅ Complete / 🔄 Partial / ❌ Missing

## Issues Checklist

### 🚨 Critical (Must Fix Before Merge)
- [ ] **[Issue]**: [Description] → [Impact] → [Solution] → [Files] → [Verification]

### ⚠️ Major (Should Fix)  
- [ ] **[Issue]**: [Description] → [Impact] → [Solution] → [Files]

### 💡 Minor (Nice to Fix)
- [ ] **[Issue]**: [Description] → [Benefit] → [Solution]

## Recommendations
### Immediate Actions
1. [Critical/major fixes needed]

### Future Improvements  
1. [Architectural suggestions]

## Final Decision
**Status**: ✅ APPROVED FOR MERGE / ❌ NEEDS FIXES / 🔄 NEEDS DISCUSSION

**Criteria**:  
**✅ APPROVED**: Requirements implemented, quality standards met, adequate tests, complete docs  
**❌ FIXES**: Critical issues, quality problems, insufficient tests, missing functionality  
**🔄 DISCUSSION**: Ambiguous requirements, architectural decisions need team input

## Developer Instructions
### Fix Issues:
1. **Follow solution guidance** and mark fixes with `[x]`
2. **Update task document** with fix details
3. **Test thoroughly** and request re-review

### Testing Checklist:
- [ ] Complete test suite executed and passes
- [ ] Manual testing of implemented features completed
- [ ] Performance impact assessed (if applicable)
- [ ] No regressions introduced
- [ ] Test results documented with actual output

### Re-Review:
1. Complete fixes, update changelog, ensure tests pass
2. Notify reviewer when ready

## Implementation Assessment
**Execution**: [Step-following quality]  
**Documentation**: [Update quality]  
**Verification**: [Steps completed]
```

### **STEP 5: Linear Communication**

**Post review results** using separate `cg-linear` calls:

1. **Update status**:
   ```bash
   cg --mcp-config .claude/mcp/linear.json -p "Update issue [ISSUE-ID] status to '[Ready to Merge | Needs Fixes | In Review]'. Do NOT modify description."
   ```

2. **Add review comment**:
   ```bash
   cg --mcp-config .claude/mcp/linear.json -p "Add comment to issue [ISSUE-ID]:
   '✅ Code review completed

   **Status**: [✅ APPROVED / ❌ NEEDS FIXES / 🔄 NEEDS DISCUSSION]
   **Review Doc**: tasks/task-[date]-[title]/Code Review - [Task].md
   **Completed**: [timestamp]
   **Summary**: [key findings]
   **Issues**: [X critical, Y major, Z minor]
   **Next Steps**: [action items]'"
   ```

**Important**: Always use separate prompts for status and comments to prevent description overwrite.
**Reference**: See `.claude/skills/cg-linear/SKILL.md` for details on separate operations.

**Status mapping:**
- APPROVED → "Ready to Merge"
- NEEDS FIXES → "Needs Fixes"
- NEEDS DISCUSSION → Keep "In Review"

**Notify user** of next steps based on review outcome
#### LINEAR SYNCHRONIZATION CHECKLIST

##### **Start:**
- [ ] Status: "In Review" + start comment with task reference

##### **Completion:**
- [ ] Comprehensive results comment with status/findings/next steps
- [ ] Update status: APPROVED→"Ready to Merge", FIXES→"Needs Fixes", DISCUSSION→"In Review"

##### **Re-Reviews:**
- [ ] Comment when requested + status update when complete

##### **Code Review Response Integration:**
- [ ] Offer automated fix option when review status is "NEEDS FIXES"
- [ ] Launch code-review-responder agent if user confirms
- [ ] Provide manual fix instructions if user declines

## SUCCESS CRITERIA

- [ ] Task document analyzed and implementation reviewed
- [ ] Code quality assessed across all criteria
- [ ] Review document created with actionable feedback
- [ ] Issues categorized with clear fix instructions
- [ ] Linear updated with start notification and results
- [ ] Clear next steps provided
- [ ] Professional, constructive tone maintained

## Workflow Feedback Collection

### Step 6: Collect Workflow Feedback
```
After completing code review, engage the workflow-feedback-collector agent to gather improvement insights about instruction clarity, process efficiency, and missing guidance that could benefit future developers.
```

**Agent Trigger**: Use workflow-feedback-collector agent
**Focus Areas**:
- Effectiveness of review criteria and quality standards
- Adequacy of test execution requirements and tooling
- Clarity of issue categorization guidelines (Critical/Major/Minor)
- Missing review checklist items or evaluation criteria
- Time efficiency of the review process and potential automation opportunities
**Documentation**: All feedback automatically logged to docs/development/dev-wf-feedback.md