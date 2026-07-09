# V1.5 / Phase 2 Roadmap

## 1. Purpose of V1.5
V1.5 is the next evolution step after the stable V1 MVP. It focuses on making the system more robust, more domain-general, and more suitable for real-world use.

## 2. Current V1 Limitations
V1 is intentionally limited. It does not yet solve:
- strong OCR for scanned PDFs
- multi-provider routing and key rotation
- sophisticated merge logic across providers
- richer confidence models
- production observability and operational resilience

## 3. Planned Improvements
- stronger extraction confidence scoring
- field-by-field merge between local parser and Gemini outputs
- provider router abstraction with multiple provider backends
- multiple free API keys with paid fallback
- domain-specific knowledge growth
- semantic matching for job descriptions and skill relevance
- OCR for scanned resumes and image-heavy PDFs
- partial analysis and graceful degradation

## 4. Proposed Architecture Changes
V1.5 should introduce a provider orchestration service that can:
1. run the local parser first
2. evaluate extraction confidence
3. route to one or more AI providers based on policy
4. normalize all outputs into one canonical schema
5. merge results intelligently
6. continue with ATS and recommendation generation

## 5. Provider Routing Strategy
A provider router should manage:
- provider registration
- per-provider credentials
- rate-limit handling
- fallback policy
- cost tracking
- latency tracking
- failure retry policy

## 6. Knowledge-Learning System
V1.5 can introduce a lightweight learning queue that stores:
- unknown skills
- alias corrections
- field-classification feedback
- model or parser improvement signals

## 7. OCR / Scanned Resume Handling
OCR support should be added through a dedicated extraction stage for scanned and image-only resumes.

## 8. Graceful Failure & Partial Analysis
The system should return partial results when one component fails rather than failing the whole analysis.

## 9. Production Hardening Tasks
- structured logging
- request tracing
- metrics and alerts
- retry policies
- background job support
- secure secret handling

## 10. Suggested Implementation Order
1. confidence model
2. merge engine
3. provider router
4. key pool management
5. OCR support
6. observability and resilience
