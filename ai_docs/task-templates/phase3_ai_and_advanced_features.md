# AI Task Planning Template - Phase 3: AI & Advanced Features

> **About This Task:** This phase integrates AI capabilities including chatbot, voice assistant, OCR document processing, automated policy assignment, claims management, and basic fraud detection.

---

## 1. Task Overview

### Task Title
**Title:** Phase 3: AI & Advanced Features - Intelligent Automation & Claims

### Goal Statement
**Goal:** Implement AI-powered features including a client-facing chatbot, voice assistant, automated document processing with OCR, intelligent policy recommendation engine, comprehensive claims management system with fraud detection, internal communication platform, and task/workflow automation. This phase transforms the platform into an intelligent system that reduces manual work and enhances user experience.

---

## 2. Current State

Phase 1-2 completed:
- ✅ User authentication & client management
- ✅ Policy & quote management
- ✅ Payment processing

Need to build:
- AI chatbot for client support
- Voice commands for policy inquiries
- OCR for document data extraction
- AI-powered policy matching
- Complete claims workflow
- Fraud detection system
- Internal chat for staff
- Task management system

---

## 3. Success Criteria

- [x] AI chatbot responding to client queries
- [x] Voice assistant working for basic commands
- [x] OCR extracting data from IDs, licenses, vehicle docs
- [x] System recommending policies based on client profile
- [x] Claims can be submitted with photo/video evidence
- [x] Claims workflow operational (submission → review → approval → payment)
- [x] Fraud detection flagging suspicious claims
- [x] Internal chat system for staff communication
- [x] Task assignment and tracking functional
- [x] Document classification working automatically

---

## 4. Technical Requirements

### AI Chatbot
- Multi-language support (French primary, English)
- Natural language understanding
- Answer FAQs about policies, claims, payments
- Escalate to human agent when needed
- Learning from conversations
- Integration with knowledge base

### Voice Assistant
- Voice recognition (French accent support)
- Commands: "Check my policy status", "File a claim", "Make a payment"
- Text-to-speech responses
- Integration with mobile app

### OCR & Document Processing
- Extract text from images
- Identify document type automatically
- Extract structured data (name, ID number, dates, etc.)
- Validate extracted data
- Support for:
  - National ID cards
  - Driver's licenses
  - Vehicle registration
  - Property deeds
  - Medical records
  - Income statements

### AI Policy Assignment
- Analyze client profile (age, income, family, assets)
- Analyze uploaded documents
- Calculate risk score
- Recommend suitable policies
- Suggest coverage amounts
- Bundle recommendations
- Cross-sell/upsell suggestions

### Claims Management
- Multi-channel submission (portal, mobile, email, phone)
- Guided claim form with AI assistance
- Photo/video upload for evidence
- Real-time status tracking
- Automated routing to adjusters
- Document verification checklists
- Approval workflows (multi-level)
- Payment processing integration
- Claims diary and activity log

### Fraud Detection (Basic)
- Anomaly detection in claims
- Duplicate claims identification
- Pattern matching across claims
- Risk scoring for claims
- Flag for manual investigation
- Integration with external databases (Phase 7)

---

## 5. Data & Database Changes

### PostgreSQL Tables

```sql
-- Claims table
CREATE TABLE claims (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID REFERENCES companies(id),
    policy_id UUID REFERENCES policies(id),
    client_id UUID REFERENCES clients(id),
    claim_number VARCHAR(50) UNIQUE NOT NULL,
    claim_type VARCHAR(100) NOT NULL,
    incident_date DATE NOT NULL,
    incident_location TEXT,
    description TEXT NOT NULL,
    claimed_amount DECIMAL(15, 2),
    approved_amount DECIMAL(15, 2),
    status VARCHAR(50) DEFAULT 'submitted',
    fraud_score DECIMAL(5, 2),
    is_flagged BOOLEAN DEFAULT FALSE,
    assigned_to UUID REFERENCES users(id),
    evidence_urls JSONB,
    details JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Claim activities table
CREATE TABLE claim_activities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    claim_id UUID REFERENCES claims(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id),
    action VARCHAR(100) NOT NULL,
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- AI conversations table
CREATE TABLE ai_conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    session_id VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    response TEXT NOT NULL,
    intent VARCHAR(100),
    confidence DECIMAL(5, 2),
    escalated BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Tasks table
CREATE TABLE tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID REFERENCES companies(id),
    assigned_to UUID REFERENCES users(id),
    created_by UUID REFERENCES users(id),
    title VARCHAR(255) NOT NULL,
    description TEXT,
    priority VARCHAR(50) DEFAULT 'medium',
    status VARCHAR(50) DEFAULT 'pending',
    due_date DATE,
    related_resource VARCHAR(100),
    related_resource_id UUID,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Chat messages table
CREATE TABLE chat_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID REFERENCES companies(id),
    sender_id UUID REFERENCES users(id),
    channel_id UUID,
    message TEXT NOT NULL,
    attachments JSONB,
    read_by JSONB DEFAULT '[]',
    created_at TIMESTAMP DEFAULT NOW()
);
```

### MongoDB Collections

```javascript
// extracted_documents
{
  _id: ObjectId,
  document_id: String,
  document_type: String,
  extraction_method: "ocr" | "manual",
  confidence_scores: Object,
  extracted_fields: {
    name: String,
    id_number: String,
    date_of_birth: Date,
    // ... other fields depending on document type
  },
  validation_status: "pending" | "verified" | "rejected",
  verified_by: String,
  verified_at: Date,
  created_at: Date
}
```

---

## 6. API Endpoints

### AI Endpoints
- `POST /api/v1/ai/chat` - Send message to chatbot
- `POST /api/v1/ai/voice` - Process voice command
- `GET /api/v1/ai/suggestions` - Get policy suggestions

### OCR Endpoints
- `POST /api/v1/ocr/process` - Process document with OCR
- `GET /api/v1/ocr/results/{id}` - Get OCR results
- `POST /api/v1/ocr/verify` - Verify extracted data

### Claims Endpoints
- `POST /api/v1/claims` - Submit claim
- `GET /api/v1/claims` - List claims
- `GET /api/v1/claims/{id}` - Get claim details
- `PUT /api/v1/claims/{id}` - Update claim
- `POST /api/v1/claims/{id}/approve` - Approve claim
- `POST /api/v1/claims/{id}/reject` - Reject claim
- `POST /api/v1/claims/{id}/activity` - Add activity

### Task Endpoints
- `POST /api/v1/tasks` - Create task
- `GET /api/v1/tasks` - List tasks
- `PUT /api/v1/tasks/{id}` - Update task

### Chat Endpoints
- `POST /api/v1/chat/messages` - Send message
- `GET /api/v1/chat/messages` - Get messages
- `POST /api/v1/chat/channels` - Create channel

---

## 7. Implementation Plan

### Week 1-2: AI Infrastructure
- [ ] Setup OpenAI API integration
- [ ] Create chatbot service
- [ ] Implement conversation context management
- [ ] Create knowledge base
- [ ] Test chatbot responses

### Week 3-4: Voice Assistant
- [ ] Integrate speech-to-text service
- [ ] Implement voice command parser
- [ ] Create text-to-speech responses
- [ ] Test voice flows

### Week 5-6: OCR Implementation
- [ ] Integrate Google Vision API / Tesseract
- [ ] Create document classification logic
- [ ] Implement data extraction per document type
- [ ] Create validation rules
- [ ] Test with real documents

### Week 7-8: Automated Policy Assignment
- [ ] Build recommendation engine
- [ ] Implement risk scoring algorithm
- [ ] Create bundle suggestion logic
- [ ] Test recommendations

### Week 9-12: Claims Management
- [ ] Create claims database schema
- [ ] Implement claims CRUD endpoints
- [ ] Create claims submission UI
- [ ] Implement adjuster assignment logic
- [ ] Create approval workflow
- [ ] Build claims dashboard

### Week 13-14: Fraud Detection
- [ ] Implement anomaly detection
- [ ] Create duplicate detection logic
- [ ] Build fraud scoring model
- [ ] Create investigation workflow

### Week 15-16: Communication & Tasks
- [ ] Build internal chat system
- [ ] Create task management
- [ ] Implement notifications
- [ ] Test workflows

---

## 8. AI Service Configuration

### OpenAI Integration

```python
# backend/services/ai_service.py
import openai

class AIService:
    def __init__(self):
        self.client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
    
    async def chat(self, message: str, context: List[dict]):
        response = await self.client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful insurance assistant..."},
                *context,
                {"role": "user", "content": message}
            ]
        )
        return response.choices[0].message.content
```

### OCR Configuration

```python
# backend/services/ocr_service.py
from google.cloud import vision

class OCRService:
    def __init__(self):
        self.client = vision.ImageAnnotatorClient()
    
    async def extract_text(self, image_url: str):
        image = vision.Image()
        image.source.image_uri = image_url
        response = self.client.text_detection(image=image)
        return response.text_annotations[0].description if response.text_annotations else ""
    
    async def classify_document(self, text: str):
        # Use AI to classify document type
        pass
    
    async def extract_fields(self, text: str, document_type: str):
        # Extract structured data based on document type
        pass
```

---

## 9. Frontend Components

### AI Chat Components
- `components/ai/chat-widget.tsx`
- `components/ai/chat-message.tsx`
- `components/ai/voice-button.tsx`

### Claims Components
- `app/(dashboard)/claims/page.tsx`
- `app/(dashboard)/claims/new/page.tsx`
- `app/(dashboard)/claims/[id]/page.tsx`
- `components/claims/claim-form.tsx`
- `components/claims/claim-table.tsx`
- `components/claims/evidence-upload.tsx`
- `components/claims/fraud-indicator.tsx`

### Task Components
- `app/(dashboard)/tasks/page.tsx`
- `components/tasks/task-list.tsx`
- `components/tasks/task-card.tsx`

---

## 10. Mandatory Rules & Best Practices

Follow ALL rules from Phase 1 and `ai_task_template_skeleton.md`.

### New Mandatory Rules

#### Analyze Build Failures (MANDATORY)
**File:** `analyze_build_failure.mdc`

**Checklist:**
- [ ] If build fails with exit code 1, capture full logs (`npm run build > log.txt 2>&1`)
- [ ] Read the full log file
- [ ] Run `npx tsc --noEmit` to isolate TypeScript errors

#### Zod Resolver Type Mismatch
**File:** `zod_resolver_type_mismatch.mdc`

**Checklist:**
- [ ] Remove `.default()` from schema for controlled form fields
- [ ] Provide explicit `defaultValues` in `useForm`
- [ ] Verify `z.infer<typeof schema>` matches `useForm<Type>`

---

## 11. Definition of Done

- ✅ Chatbot answering common questions
- ✅ Voice assistant processing commands
- ✅ OCR extracting data from uploaded documents
- ✅ System recommending policies to clients
- ✅ Claims submitted and tracked
- ✅ Fraud detection flagging suspicious claims
- ✅ Internal chat working for staff
- ✅ Tasks assigned and tracked
- ✅ All tests passing
- ✅ Deployed to staging

---

**Task Version**: 1.0  
**Estimated Duration**: 16 weeks (~4 months)  
**Status**: Ready for Implementation
