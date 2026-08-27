# Embedded AI Platform 121XML Integration Template
## For Document-Centric & Design-Centric Platforms (Grammarly, Canva, etc.)

**Use this template for platforms that don't have standalone conversation architecture but are embedded in workflows.**

---

## ARCHITECTURE TYPE: DOCUMENT/ARTIFACT-CENTRIC

Unlike standalone AI platforms, embedded platforms operate on:
- Documents (Grammarly)
- Designs (Canva)
- Spreadsheets (Excel formula AI)
- Presentations (PowerPoint Design)

**Challenge:** State is tied to artifact, not conversation

**121XML Solution:** Artifact-attached inference objects

---

## CORE PROFILE PATTERN

### Profile Type A: Artifact State Profile
```xml
<map profile="urn:121xml:embedded-artifact-state/1.0">
  <str name="artifact_id">UUID</str>
  <str name="artifact_address">data://sha256:COMPUTED:artifact</str>
  <str name="artifact_type">document | design | spreadsheet</str>
  <str name="user_id">USER_ID</str>
  
  <!-- Artifact content reference -->
  <str name="artifact_content_reference">data://sha256:CONTENT:raw</str>
  <str name="artifact_version">1.5</str>
  <str name="last_modified">2026-08-06T10:30:00Z</str>
  
  <!-- All AI suggestions/modifications -->
  <seq name="ai_inferences" of="str">
    <str>data://sha256:inf001:inference</str>
    <str>data://sha256:inf002:inference</str>
  </seq>
  
  <!-- Accepted modifications -->
  <seq name="accepted_modifications" of="str">
    <str>data://sha256:mod001:modification</str>
  </seq>
  
  <!-- Permission to access artifact -->
  <str name="permission_grant_id">grant_001</str>
</map>
```

### Profile Type B: AI Suggestion/Inference Profile
```xml
<map profile="urn:121xml:embedded-ai-suggestion/1.0">
  <str name="inference_id">UUID</str>
  <str name="inference_address">data://sha256:COMPUTED:inference</str>
  <str name="created_by">platform_ai | user_feedback</str>
  <str name="created_timestamp">2026-08-06T10:30:15Z</str>
  
  <!-- What artifact this suggestion applies to -->
  <str name="artifact_reference">data://sha256:ARTIFACT:artifact</str>
  
  <!-- Type of suggestion -->
  <str name="suggestion_type">grammar | style | clarity | design | optimization</str>
  
  <!-- Suggestion details -->
  <map name="suggestion">
    <str name="location">paragraph_2, sentence_3</str>
    <str name="original_text">The original text</str>
    <str name="suggested_text">The improved text</str>
    <str name="reason">Why this change improves it</str>
    <float name="confidence">0.95</float>
  </map>
  
  <!-- User action -->
  <str name="status">suggested | accepted | rejected | modified</str>
  <str name="user_action_timestamp">2026-08-06T10:30:30Z</str>
  
  <!-- For learning -->
  <str name="user_approved_change">YES | NO | PARTIAL</str>
</map>
```

### Profile Type C: Modification History Profile
```xml
<map profile="urn:121xml:embedded-modification-history/1.0">
  <str name="artifact_reference">data://sha256:ARTIFACT:artifact</str>
  
  <seq name="modifications" of="map">
    <map>
      <str name="modification_id">UUID</str>
      <str name="modified_timestamp">2026-08-06T10:30:45Z</str>
      <str name="modified_by">user | ai_system</str>
      <str name="change_type">text | style | structure | design</str>
      
      <map name="change">
        <str name="before">Original content</str>
        <str name="after">Modified content</str>
        <str name="location">Specific location in artifact</str>
      </map>
      
      <!-- Link to AI inference that suggested this -->
      <str name="from_inference_reference">data://sha256:inf001:inference</str>
      
      <!-- User's feedback -->
      <str name="user_approved">YES</str>
      <str name="user_comment">Why they accepted/rejected</str>
    </map>
  </seq>
</map>
```

---

## IMPLEMENTATION PATTERN

### For Grammarly (Writing Assistance)

**1. grammarly_document_state.121xml**
- Document content (by reference)
- All grammar/style suggestions
- User corrections
- Learning signals

**2. grammarly_suggestion.121xml**
- Grammar issue identified
- Suggested correction
- Confidence score
- Reasoning

**3. grammarly_modification_history.121xml**
- All document changes
- Which were AI-suggested
- User feedback
- Learning dataset

**4. grammarly_enterprise_team.121xml**
- Team writing style profile
- Custom rules
- Shared document access
- Audit trail

### For Canva (Design Assistance)

**1. canva_design_state.121xml**
- Design file (by reference)
- All Magic Suite suggestions
- Applied changes
- Design history

**2. canva_design_suggestion.121xml**
- Design issue identified
- Suggested improvement
- Visual rationale
- Alternative options

**3. canva_design_history.121xml**
- All design iterations
- AI vs. manual changes
- User approvals
- Design evolution

**4. canva_template_library.121xml**
- User's template collection
- Personalization via inferences
- Suggestion history
- Reusability tracking

---

## SPECIFIC IMPLEMENTATIONS

### GRAMMARLY Implementation Path

```
Week 1-2: Profile Design
- Document state profile
- Suggestion/correction profiles
- Modification tracking

Week 3-4: Extension Development
- Browser extension changes
- Document state persistence
- Real-time suggestion updates

Week 5-6: Team Features
- Shared document state
- Team style guidelines
- Audit logging

Week 7-8: Learning & Analytics
- Aggregate user corrections (for model improvement)
- Style trend analysis
- ROI measurements

Files to Create:
├─ /Grammarly/
│  ├─ grammarly_document_state.121xml
│  ├─ grammarly_suggestion.121xml
│  ├─ grammarly_modification_history.121xml
│  └─ grammarly_enterprise_profile.121xml
```

### CANVA Implementation Path

```
Week 1-2: Design State Profile
- Design file reference
- Suggestion tracking
- Change history

Week 3-4: Magic Suite Integration
- Text suggestion inferences
- Image recommendation inferences
- Layout improvement inferences

Week 5-6: Template Personalization
- User preference learning
- Design style tracking
- Personalized suggestions

Week 7-8: Analytics
- Design trend analysis
- User preference patterns
- ROI for design improvements

Files to Create:
├─ /Canva/
│  ├─ canva_design_state.121xml
│  ├─ canva_design_suggestion.121xml
│  ├─ canva_design_history.121xml
│  └─ canva_template_preference.121xml
```

---

## DATA SOVEREIGNTY FOR EMBEDDED PLATFORMS

### User Control Points

1. **Artifact Storage**
   - Grammarly: Document stays on user's device/cloud
   - Canva: Design stays in Canva (but encrypted, user-controlled)

2. **Suggestion Acceptance**
   - User decides which suggestions to accept
   - All rejections recorded (learning signal)

3. **Data Export**
   - Export all documents with suggestion history
   - Export all design files with modification logs
   - Full data portability

4. **Learning Opt-Out**
   - User can disable AI learning from their content
   - Inferences still generated, just not aggregated for model improvement

---

## CRITICAL BOUNDARIES (EMBEDDED PLATFORMS)

**Boundary 01: No Centralization** ✓ PASS
- Each user's artifacts/suggestions stay decentralized
- No central "best practices" repository

**Boundary 02: No Data Copying** ✓ PASS
- Only references to artifacts shared
- Raw content stays with user/platform
- Suggestions are lightweight objects

**Boundary 03: No Single Vendor** ✓ PASS
- Suggestion format portable to other writing/design tools
- Same 121XML for Microsoft Word AI, Canva alternatives, etc.

**Boundary 04: No Context Loss** ✓ PASS
- All suggestions immutable (history preserved)
- Full artifact evolution tracked
- User learning captured

---

## MEASUREMENT FRAMEWORK

### For Grammarly
```
Metrics:
- Suggestions offered vs. accepted (conversion rate)
- Types of corrections most useful to user
- Writing improvement over time
- Team style consistency gains
```

### For Canva
```
Metrics:
- Design suggestions offered vs. accepted
- Time saved per design (with/without Magic Suite)
- User design skill growth
- Template personalization accuracy
```

---

## TEMPLATE SUMMARY

**Use this template for:**
- Grammarly (grammar/style suggestions)
- Canva (design suggestions)
- Microsoft Word/Excel AI (writing/formula suggestions)
- Any platform with artifact + suggestions model

**Core 121XML Profiles Needed:**
1. `artifact_state.121xml` (document/design/file + all inferences)
2. `ai_suggestion.121xml` (specific suggestion + reasoning)
3. `modification_history.121xml` (all changes + user feedback)
4. `platform_enterprise_profile.121xml` (team/organization settings)

**Key Insight:**
Embedded platforms don't need conversation management (like ChatGPT/Gemini).
They need **artifact management + suggestion tracking + user learning**.

---

**Status:** TEMPLATE READY - Use for Grammarly, Canva, and similar platforms
