# Qualitative Codebook: VC Questionnaire Analysis

_Digital Presence in the German Startup Ecosystem_

---

## **1. Digital Infrastructure**

**Definition**: Aspects related to the technical/strategic components of digital presence.

| Code                | Description                                | Example Quote                                                                 |
| ------------------- | ------------------------------------------ | ----------------------------------------------------------------------------- |
| `DEFINITION`        | How respondents define "digital presence"  | _"Sum of all ways you appear online: website, social media, content sharing"_ |
| `COMPONENTS`        | Key elements of effective digital presence | _"LinkedIn connections, press coverage, GitHub activity"_                     |
| `PLATFORM_PRIORITY` | Valued platforms (LinkedIn > Instagram)    | _"A big LinkedIn network compensates; Instagram cannot"_                      |

---

## **2. Cultural Nuances**

**Definition**: German-specific cultural factors influencing digital presence evaluation.

| Code               | Description                              | Example Quote                                             |
| ------------------ | ---------------------------------------- | --------------------------------------------------------- |
| `PROFESSIONALISM`  | Emphasis on polished, factual content    | _"Germans value error-free profiles and expertise"_       |
| `MODESTY`          | Avoidance of self-promotion              | _"Overhyped claims are seen critically"_                  |
| `RISK_AVERSION`    | Conservative approach to digital signals | _"We analyze extensively but still prefer track records"_ |
| `INPERSON_NETWORK` | Preference for offline validation        | _"Final decisions always involve personal meetings"_      |

---

## **3. Evaluation Criteria**

**Definition**: How digital presence is assessed in funding decisions.

| Code               | Description                          | Example Quote                                           |
| ------------------ | ------------------------------------ | ------------------------------------------------------- |
| `VERIFICATION`     | Methods to validate online claims    | _"We check LinkedIn, read articles, view social media"_ |
| `RED_FLAGS`        | Negative digital presence indicators | _"Inconsistent info across platforms raises concerns"_  |
| `POSITIVE_SIGNALS` | Factors that enhance credibility     | _"Thought leadership via blogs/podcasts adds value"_    |

---

## **4. Evolving Trends**

**Definition**: Perceptions of digital presence's changing role.

| Code                  | Description                               | Example Quote                                       |
| --------------------- | ----------------------------------------- | --------------------------------------------------- |
| `CHANGING_IMPORTANCE` | Shifts in relevance over time             | _"Digital presence acts as an initial filter now"_  |
| `FUTURE_PREDICTION`   | Expectations for 3-5 years                | _"Importance will increase slightly with AI tools"_ |
| `DRIVERS_OF_CHANGE`   | Forces shaping digital presence evolution | _"Global competition and Gen Z expectations"_       |

---

## **5. Sentiment Codes**

**Definition**: Emotional valence toward digital presence.

| Code       | Description                        | Example Quote                                           |
| ---------- | ---------------------------------- | ------------------------------------------------------- |
| `POSITIVE` | Clear endorsement of digital value | _"Digital identity is essential for long-term success"_ |
| `NEUTRAL`  | Ambivalent or conditional support  | _"It matters, but depends on the industry"_             |
| `NEGATIVE` | Skepticism about digital influence | _"Can’t compensate for weak unit economics"_            |

---

## **6. Demographic & Contextual Codes**

**Definition**: Respondent characteristics shaping perspectives.

| Code                  | Description                       | Example Entry                 |
| --------------------- | --------------------------------- | ----------------------------- |
| `ROLE`                | Position (Partner, Analyst, etc.) | _"Senior Investment Manager"_ |
| `EXPERIENCE`          | Years in VC (1-3, 3-5, 5+)        | _"More than 5 years"_         |
| `CULTURAL_BACKGROUND` | National/cultural identity        | _"German"_                    |

---

## **Code Application Guidelines**

1. **Ambiguous Responses**: Use `NEUTRAL` if sentiment is unclear.
2. **Multiple Codes**: Assign all applicable codes (e.g., a quote about _"LinkedIn professionalism in Germany"_ gets `PROFESSIONALISM` + `PLATFORM_PRIORITY`).
3. **Negative Cases**: Note when respondents explicitly reject a theme (e.g., _"We don’t care about Instagram"_ → `PLATFORM_PRIORITY` with negative sentiment).
4. **Cross-Code Analysis**: Compare `CULTURAL_BACKGROUND` with `PLATFORM_PRIORITY` to identify German vs. non-German patterns.

---
