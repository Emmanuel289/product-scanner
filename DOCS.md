# Technical Documentation

## Overview

Product Scanner is a serverless web app that is useful for scanning and analyzing supported beauty products. A user photographs a product label, the backend runs OCR to extract the text from the labels, matches the text against a curated product database, runs a deterministic decision engine, and returns structured product intelligence including a personalised fit score. There are no LLM calls in the critical path - every decision is rule-based and fully explainable.

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                      Frontend (Vercel)                  │
│                    React + Vite (SPA)                   │
└───────────────────────────┬─────────────────────────────┘
                            │ HTTPS POST /scan
                            ▼
┌─────────────────────────────────────────────────────────┐
│              API Gateway (REST)            │
│                     POST /scan                          │
│                     OPTIONS /scan                       │
└───────────────────────────┬─────────────────────────────┘
                            │ AWS_PROXY
                            ▼
┌─────────────────────────────────────────────────────────┐
│               Lambda (Container)                        │
│                                                         │
│  Cold start:                                            │
│  DynamoDB.scan() -> build_products() ->PRODUCTS_BY_BRAND│
│                                                         │
│  Per request:                                           │
│  S3.put_object() ->  Textract.detect_document_text()    │
│   -> match_product() → recommend() → build_result()     │
└──────┬──────────────────────┬───────────────────────────┘
       │                      │
       ▼                      ▼
┌─────────────┐    ┌──────────────────────┐
│  S3 Bucket  │    │  DynamoDB            │
│  incoming/  │    │  product-scanner-    │
│  (uploads)  │    │  products            │
└─────────────┘    └──────────────────────┘
       │
       │ S3 ObjectCreated (incoming/ prefix)
       ▼
┌─────────────────────────────────────────────────────────┐
│               Lambda (S3 event branch)                  │
│               (same function, separate code path)       │
└─────────────────────────────────────────────────────────┘
       │
       ▼
┌─────────────┐
│  Textract   │
└─────────────┘
```

---

## Infrastructure

All infrastructure is defined in the `infra/` directory and managed via Terraform.

| Resource | Purpose |
|---|---|
| `aws_s3_bucket` | Stores uploaded product images under `incoming/` prefix |
| `aws_ecr_repository` | Hosts the Lambda container image |
| `aws_lambda_function` | Runs the scanner container image
| `aws_api_gateway_rest_api` | Exposes `POST /scan` and `OPTIONS /scan` |
| `aws_dynamodb_table` | Persistent product store
| `aws_cloudwatch_log_group` | Log group for the Lambda logs
| `aws_iam_role` + `aws_iam_role_policy` | Least-privilege: S3, Textract, DynamoDB, CloudWatch |
| `null_resource` | Builds and pushes Docker image to ECR on Dockerfile change |

### Key infrastructure decisions

**A Lambda source code deployed as a container image** allows full control over the Python environment and dependencies (Pydantic, boto3).

**S3 trigger scoped to `incoming/` prefix**:  the Lambda uploads to `incoming/`, and the S3 trigger only fires on `incoming/`. This prevents the S3 branch from re-triggering when the HTTP branch uploads an image, which would cause every scan to invoke the Lambda twice and double Textract costs.

**DynamoDB `PAY_PER_REQUEST`** - with under 50 products and read-heavy access patterns (full table scan at cold start), on-demand billing stays within free tier indefinitely.

---

## Backend

### Handler (`handler.py`)

The Lambda handler has two branches determined by the event shape:

**HTTP branch** (triggered by API Gateway `POST /scan`):

```
body.product_name present  → name search branch (no Textract)
body.image_base64 present  → image scan branch (Textract)
neither                    → 400
```

**S3 event branch** (triggered by S3 `ObjectCreated` on `incoming/`):

Reads directly from the S3 event record, runs Textract on the uploaded object, matches, and returns a result. Designed for async processing use cases.

### Cold start

At Lambda cold start, the handler scans the entire DynamoDB table and builds `PRODUCTS_BY_BRAND` in memory:

```python
RAW_PRODUCTS    = load_products_from_dynamodb()   # DynamoDB.scan() with pagination
PRODUCTS_BY_BRAND = build_products(RAW_PRODUCTS, BRAND_ALIASES, STOPWORDS)
```

`PRODUCTS_BY_BRAND` is a `Dict[brand_name → List[product_dict]]`. Subsequent warm invocations reuse this in-memory structure with no DynamoDB reads per request.

### Text matching (`match_product`)

The matching engine is a simple, token-based similarity procedure:

```
score = |product_tokens _intersect_ text_tokens| / max(|product_tokens|, 1)
```

1. Textract returns OCR lines from the product label
2. Lines are joined into a single string and normalised (lowercased, aliases resolved, punctuation and digits stripped, stop words removed)
3. The normalised string is tokenised
4. Every product's pre-computed `search_tokens` is compared against the text tokens
5. The product with the highest score wins, provided it clears a set `CONFIDENCE_THRESHOLD`.

**Why token-based matching over other approaches:** The score is directly interpretable (fraction of product tokens matched), handles partial label reads gracefully, and is deterministic and fast with no external dependencies.

**Brand aliases** handle common OCR and user input variations:

```python
BRAND_ALIASES = {
    "la roche posay": "la roche-posay",
    "larocheposay":   "la roche-posay",
    "rarebeauty":     "rare beauty"
}
```

### Decision engine (`decision_engine.py`)

The decision engine is fully deterministic with no LLM calls and no probabilistic outputs. Every decision is traceable to a specific rule:

**`compute_fit_score(product, user_profile) -> int | None`**

Returns `None` when no user profile is provided. Otherwise computes a 0–100 integer:

| Factor | Adjustment |
|---|---|
| Base | +65 |
| User skin type in `skin_types` | +20 |
| User skin type in `avoid_for` | −35 |
| Each matched concern | +5 |
| Each concern in `concerns_not_ideal` | −10 |
| Sensitive user + high `sensitivity_risk` | −20 |
| Oily/combination user + high `comedogenic_risk` | −10 |

Score is normalized to [0, 100].

**`recommend(product, user_profile) → dict`**

Runs attribute-based rules to build the rationale, then applies fit score thresholds to determine the final outcome label:

| Fit score | Outcome |
|---|---|
| ≥ 80 | ✅ Good match |
| 55–79 | ⚠️ Mixed match |
| < 55 | ❌ Not recommended |

Without a user profile, outcome falls back to attribute-only rules (comedogenic risk, sensitivity risk, avoid_for conflicts).

**Why deterministic rules over an LLM:** The deterministic rule-based logic is auditable and every outcome can be traced to a specific product attribute and user profile value. An LLM recommendation cannot be audited in the same way and introduces non-determinism that undermines user trust.

### Alternatives (`explain_alternative`)
Alternatives are sampled from the same brand as the matched product (up to 2). Each alternative is explained by comparing four dimensions against the matched product:

1. **Shared concerns** — `"Targets the same barrier repair goal"`
2. **Texture difference** — `"but balm texture"`
3. **Unique skin types** — `"better suited for sensitive skin"`
4. **Fallback** — finish or `"different formulation approach"`

### Data enrichment (`scripts/enrich_products.py`)

A separate offline script that calls Claude to generate `ingredient_intent`, `pros`, and `cons` for each product in simple language. It writes directly to DynamoDB via `update_item` with no redeployment needed. Supports `--dry-run` and `--brand` flags for safe experimentation.

---

## Frontend

### Stack

- React 18 + Vite
- Inline styles throughout (no CSS framework) — consistent with the dark design system
- Google Fonts: DM Serif Display (headings) + DM Sans (body)
- Deployed on Vercel

### Component architecture

```
App.jsx                   Phase state machine + history navigation
├── ScanStep.jsx          Camera stream, file upload, drag-drop, name search
├── LoadingState.jsx      Animated step-by-step progress indicator
└── ResultView.jsx        Full result page
    ├── FitMeter.jsx      Animated 0–100 arc meter
    ├── PillTag.jsx       Attribute pills (texture, finish, risk)
    ├── SectionTitle.jsx  Section heading atom
    ├── SubLabel.jsx      Sub-section label atom
    └── ReviewLine.jsx    Pros/cons line item
```

### Phase state machine

Navigation is managed as a history stack in `App.jsx`:

```
States: "scan" | "loading" | "result"

scan ──[Analyze Product]──▶ loading ──[response received]──▶ result
 ◀──────────────────────────────────────────────[back arrow]──
 ──────────────────────────────────────────────[fwd arrow]──▶
```

Loading is transient - it is not pushed to the history stack. Back/forward arrows only navigate between `scan` and `result`. Scanning a new product clears the forward history, matching standard browser navigation behaviour.

### Personalisation flow

The skin type selector in `ResultView` triggers a second `POST /scan` call with the same `image_base64` and a `user_profile` payload. The response overwrites `personalizedData` in component state — the original scan result is preserved and restored if the user navigates away.

### Name search

The search input debounces at 350ms before firing a `POST /scan` with `product_name` in the body. The backend skips Textract entirely for name queries and runs `match_product` directly against the in-memory `PRODUCTS_BY_BRAND`. Results appear inline as a tappable card — no separate results page.

---

## API

### `POST /scan`

**Request - image scan:**
```json
{
  "image_base64": "<base64-encoded JPEG>",
  "user_profile": {
    "skin_type": "dry",
    "concerns": ["acne"],
    "sensitive": false
  }
}
```

**Request - name search:**
```json
{
  "product_name": "Toleriane Hydrating Gentle Cleanser",
  "user_profile": { ... }
}
```

`user_profile` is optional in both cases. Omitting it returns `fit_score: null` and `personalized: false`.

**Response - matched:**
```json
{
  "status": "✅ Good match",
  "brand": "La Roche-Posay",
  "product_name": "Toleriane Hydrating Gentle Cleanser",
  "product_summary": {
    "outcome": "✅ Good match",
    "fit_score": 85,
    "personalized": true,
    "rationale": [
      "This product is well aligned with your dry skin type.",
      "Targets barrier repair and gentle cleansing."
    ],
    "texture": "cream",
    "finish": "",
    "coverage": null,
    "skin_types": ["dry", "sensitive"],
    "avoid_for": ["very oily"],
    "comedogenic_risk": "low",
    "sensitivity_risk": "low",
    "ingredient_intent": "Ceramide-3 (rebuilds skin barrier) + Glycerin (draws moisture in)",
    "pros": ["Doesn't strip the skin", "Works well for reactive skin"],
    "cons": ["Might feel too rich for oily skin"]
  },
  "alternatives": [
    {
      "name": "Toleriane Double Repair Face Moisturizer",
      "why_different": "Targets the same barrier repair goal - but cream texture"
    },
    {
      "name": "Cicaplast Baume B5",
      "why_different": "Targets the same barrier repair goal - but balm texture - better suited for sensitive skin"
    }
  ]
}
```

**Response - not found:**
```json
{
  "status": "❌ Product Not Found",
  "message": "We couldn't confidently identify this product, so we didn't make a guess."
}
```

---

## Test suite

```
tests/
├── test_compute_fit_score.py   5 tests — scoring math across all skin type permutations
├── test_recommend.py           5 tests — decision engine outcomes and rationale generation
├── test_lambda.py             12 tests — full handler contract (HTTP + S3 branches)
├── test_alternatives.py        7 tests — explain_alternative() across all comparison paths
```

Run unit tests (no AWS required):
```bash
pytest -v
```

Run live integration tests:
```bash
pytest tests/integration/ -v -s
```

---

## Data model

Each product in DynamoDB has the following shape:

```json
{
  "product_id":         "la-roche-posay-toleriane-hydrating-gentle-cleanser",
  "brand":              "La Roche-Posay",
  "name":               "Toleriane Hydrating Gentle Cleanser",
  "category":           "cleanser",
  "texture":            "cream",
  "finish":             "",
  "coverage":           "",
  "skin_types":         ["dry", "sensitive"],
  "best_for":           ["dry", "sensitive"],
  "avoid_for":          ["very oily"],
  "concerns_targeted":  ["barrier repair", "gentle cleansing"],
  "concerns_not_ideal": ["oil stripping"],
  "comedogenic_risk":   "low",
  "sensitivity_risk":   "low",
  "ingredient_intent":  "Ceramide-3 (rebuilds skin barrier) + Glycerin (draws moisture in)",
  "pros":               ["Doesn't strip the skin", "Works well for reactive skin"],
  "cons":               ["Might feel too rich for oily skin"]
}
```

Adding a new product requires only a `put_item` call to DynamoDB.

---

## Expanding the product catalogue

1. Add product attributes to DynamoDB directly (AWS console, script, or API)
2. Run enrichment script to populate `ingredient_intent`, `pros`, `cons`:
   ```bash
   python scripts/enrich_products.py --dry-run --brand "New Brand"
   python scripts/enrich_products.py --brand "New Brand"
   ```
3. The Lambda picks up new products on next cold start — no redeployment needed

CloudWatch logs show every scan that returns "No match found" along with the best score and the OCR text. This is the intended feedback loop for identifying which products to add next.
