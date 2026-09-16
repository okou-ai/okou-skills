---
name: reply-templates
description: Create and use reusable legal response templates for DSARs, subpoenas, NDAs, policies, and similar requests.
---

## Template Architecture

### Required Components for Every Template

Each template in the library must contain:

1. **Label**: A descriptive, searchable name
2. **Category**: The inquiry type it addresses
3. **Applicability criteria**: Conditions under which this template is the right choice
4. **Red flags**: Scenarios where this template must NOT be used
5. **Variable fields**: Placeholders that require per-use customization
6. **Body text**: The response content with embedded placeholders
7. **Post-send checklist**: Standard follow-up tasks after dispatching the response
8. **Review date**: When the template was last verified for legal and factual accuracy

### Template Governance Cycle

1. **Drafting**: Author the template informed by current law and team practices
2. **Approval**: Legal team reviews for accuracy, compliance, and completeness
3. **Activation**: Enter the template into the shared library with full metadata
4. **Deployment**: Use the template to produce tailored responses
5. **Refinement tracking**: Monitor ad-hoc edits made during use to surface improvement opportunities
6. **Revision**: Update when statutes, regulations, or internal policies change
7. **Deprecation**: Remove or archive templates that no longer apply

## Inquiry Categories and Template Guidance

### Category 1: Data Subject Requests

Covers all requests from individuals exercising privacy rights under GDPR, CCPA, and similar frameworks.

**Variants:**
- Receipt acknowledgment
- Identity verification follow-up
- Fulfillment (access, erasure, rectification)
- Partial denial with justification
- Complete denial with justification
- Timeline extension notice

**Mandatory elements in every DSR template:**
- Citation of the governing regulation
- Concrete response deadline
- Verification requirements for the requestor
- Enumeration of the individual's rights (including supervisory authority complaints)
- Team contact details for follow-up

**Skeleton:**
```
Subject: Your Data [Access/Erasure/Rectification] Request -- Ref {{ref_number}}

Dear {{individual_name}},

We received your {{request_date}} request to [access/erase/rectify] personal data under [regulation].

[Acknowledgment / verification instructions / fulfillment summary / denial rationale]

A substantive response will be provided by {{deadline}}.

[Contact details]
[Rights summary]
```

### Category 2: Litigation Hold Notices

Preservation directives issued to custodians when litigation is anticipated or pending.

**Variants:**
- Initial preservation directive
- Periodic reaffirmation reminder
- Scope modification
- Hold release

**Mandatory elements:**
- Matter identifier and reference code
- Explicit preservation duties
- Scope boundaries (date window, data categories, systems, communication channels)
- Spoliation prohibition
- Point of contact for questions
- Acknowledgment requirement and deadline

**Skeleton:**
```
Subject: LITIGATION HOLD -- {{matter_name}} -- Response Required

PRIVILEGED AND CONFIDENTIAL
ATTORNEY-CLIENT COMMUNICATION

Dear {{custodian_name}},

You are receiving this directive because you may hold documents, messages, or electronic data pertinent to the matter identified above.

PRESERVATION REQUIREMENTS:
Starting now, retain all documents and electronically stored information connected to:
- Topic: {{scope_description}}
- Time window: {{date_start}} through present
- Material types: {{material_categories}}

Do NOT alter, discard, or destroy any potentially relevant materials.

[Platform-specific retention instructions]

Confirm receipt by {{ack_deadline}}.

Questions? Contact {{legal_contact}}.
```

### Category 3: Privacy Inquiries

Responses to external questions about organizational data practices.

**Variants:**
- Cookie and tracking technology questions
- Privacy notice clarifications
- Data sharing practice inquiries
- Children's data handling questions
- International transfer inquiries

**Mandatory elements:**
- Pointer to the published privacy notice
- Answers grounded in current, verified practices
- Links to relevant privacy documentation
- Privacy team contact information

### Category 4: Vendor and Contract Inquiries

Responses to legal questions from business partners and suppliers.

**Variants:**
- Contract status updates
- Amendment request handling
- Compliance certification questions
- Audit facilitation responses
- Insurance documentation requests

**Mandatory elements:**
- Reference to the governing agreement
- Precise answer to the vendor's specific question
- Any necessary disclaimers or scope limitations
- Timeline and next steps

### Category 5: Non-Disclosure Agreements

Handling the NDA lifecycle from initiation through renewal.

**Variants:**
- Dispatching the organization's standard NDA form
- Reviewing and marking up a counterparty's NDA
- Declining an NDA request with explanation
- Renewal or extension of an existing NDA

**Mandatory elements:**
- Stated purpose for the confidentiality arrangement
- Summary of key terms
- Signing instructions and process
- Expected timeline

### Category 6: Subpoenas and Legal Process

Responses to compulsory legal demands.

**Variants:**
- Receipt acknowledgment
- Formal objection
- Extension request
- Production cover letter

**Mandatory elements:**
- Case citation and jurisdictional details
- Itemized objections where applicable
- Preservation confirmation
- Compliance timeline
- Privilege log reference if relevant

**Important:** Responses to compulsory legal process nearly always demand individualized attorney review. Templates serve as scaffolding, never as final output.

### Category 7: Insurance Notifications

Communications with insurers regarding potential or active claims.

**Variants:**
- Initial claim notice
- Supplemental information submission
- Reservation of rights response

**Mandatory elements:**
- Policy number and coverage window
- Factual description of the matter or event
- Chronological narrative
- Request for coverage confirmation

## Customization Requirements

### Mandatory Per-Use Adjustments

No template may be sent without populating:
- Accurate names, dates, and reference identifiers
- Case-specific facts
- Correct jurisdiction and applicable legal framework
- Calculated response deadlines based on receipt date
- Proper signature block and contact coordinates

### Tone Calibration

Adjust register based on:
- **Recipient**: Internal colleague vs. external party, business person vs. attorney, individual vs. regulatory body
- **Relationship**: New counterparty vs. long-term partner vs. adversary
- **Gravity**: Routine matter vs. contested dispute vs. government investigation
- **Time pressure**: Standard processing vs. expedited turnaround

### Jurisdictional Adaptation

- Confirm that all regulatory citations match the requestor's jurisdiction
- Recalculate deadlines according to applicable statutory requirements
- Include jurisdiction-mandated rights disclosures
- Apply locally appropriate legal terminology

## Situations Requiring Escalation Instead of Templates

Before producing any response, scan for conditions that disqualify template use:

### Universal Disqualifiers

- Active or threatened litigation or regulatory proceeding
- Inquiry originates from a regulator, government body, or law enforcement
- The response could create a binding obligation or constitute a waiver
- Potential criminal exposure
- Media involvement is present or foreseeable
- The scenario has no precedent within the team's experience
- Conflicting requirements across multiple jurisdictions
- Executive leadership or board members are involved parties

### Category-Specific Disqualifiers

**Data Subject Requests:**
- Requestor is a minor or acting on behalf of a minor
- Requested data is subject to an active litigation hold
- Requestor is in pending litigation or dispute with the organization
- Requestor is an employee with an open HR investigation
- Request scope appears designed for discovery rather than privacy rights
- Special-category data is implicated (health, biometric, genetic)

**Litigation Holds:**
- Criminal liability is possible
- Preservation scope is contested or ambiguous
- Hold conflicts with regulatory data deletion mandates
- Overlapping holds exist for connected matters
- A custodian challenges the hold parameters

**Vendor Questions:**
- Vendor is challenging contractual terms
- Vendor is threatening legal action or contract termination
- Response could prejudice an active negotiation
- Inquiry involves regulatory compliance rather than contractual interpretation

**Subpoenas / Legal Process:**
- ALWAYS route to counsel (templates are starting frameworks only)
- Privilege concerns are identified
- Third-party data is within scope
- Cross-border production complications exist
- Compliance timeline is unreasonably compressed

### Escalation Protocol When a Disqualifier is Detected

1. **Halt**: Do not produce a template-based response.
2. **Flag**: Notify the requestor that an escalation condition exists.
3. **Detail**: Explain which disqualifier was triggered and its implications.
4. **Direct**: Recommend the appropriate escalation path (senior counsel, outside counsel, specific specialist).
5. **Assist**: Offer a preliminary draft clearly watermarked "DRAFT -- FOR COUNSEL REVIEW ONLY" to accelerate the individualized review.

## Authoring New Templates

### Phase 1: Scope Definition
- What recurring inquiry does this address?
- How often does it arise?
- Who is the typical recipient?
- What is the normal urgency level?

### Phase 2: Content Requirements
- What information is legally required in every response?
- Which regulations or policies govern this response type?
- What organizational standards apply?

### Phase 3: Variable Identification
- Which elements change per use? (names, dates, case-specific facts)
- Which elements remain constant? (statutory language, standard terms)
- Use unambiguous placeholder names: `{{requestor_name}}`, `{{compliance_deadline}}`, `{{matter_id}}`

### Phase 4: Drafting
- Write in clear, professional prose
- Minimize unnecessary legal jargon for business-audience templates
- Incorporate all legally mandated content
- Insert placeholders for every variable element
- Include a subject line template for email-based responses

### Phase 5: Safeguard Definition
- Under what circumstances must this template be set aside?
- What signals indicate the matter needs bespoke handling?
- Specificity matters: vague safeguards provide no protection

### Phase 6: Metadata Completion
- Assign template name and category
- Record version number and last-reviewed date
- Document author and approver
- Attach the post-send checklist

### Standard Template Format

```markdown

## Template: {{template_label}}

**Category**: {{category}}
**Version**: {{version}} | **Reviewed**: {{review_date}}
**Approved By**: {{approver_name}}

### When to Use
- [Condition 1]
- [Condition 2]

### When NOT to Use (Escalation Triggers)
- [Disqualifier 1]
- [Disqualifier 2]

### Variable Fields
| Placeholder | Meaning | Sample Value |
|---|---|---|
| {{var1}} | [description] | [example] |
| {{var2}} | [description] | [example] |

### Subject Line
[Template with {{placeholders}}]

### Body
[Response content with {{placeholders}}]

### Post-Send Actions
1. [Step 1]
2. [Step 2]

### Usage Notes
[Special guidance for anyone deploying this template]
```
