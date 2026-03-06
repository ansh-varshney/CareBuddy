"""Knowledge base ingestion service."""

import logging
from typing import Optional

from app.core.rag_pipeline import rag_retriever

logger = logging.getLogger(__name__)


# ── Sample Medical Knowledge Base ─────────────────────────
# This provides initial medical reference data for RAG retrieval.
# In production, this would be replaced with ingestion from
# MedlinePlus, Mayo Clinic, clinical guidelines, etc.

SAMPLE_MEDICAL_KNOWLEDGE = [
    {
        "id": "headache-overview",
        "source": "Medical Reference",
        "category": "symptoms",
        "content": (
            "Headaches are one of the most common medical complaints. Most headaches are not "
            "caused by serious medical conditions. Types include tension headaches (feeling like "
            "a tight band around the head), migraines (throbbing pain often on one side with "
            "nausea and light sensitivity), and cluster headaches (severe pain around one eye). "
            "Seek immediate care if headache is sudden and severe ('thunderclap'), accompanied "
            "by fever, stiff neck, confusion, seizures, double vision, weakness, numbness, or "
            "difficulty speaking. Common triggers include stress, poor posture, dehydration, "
            "lack of sleep, caffeine withdrawal, and eye strain."
        ),
    },
    {
        "id": "fever-overview",
        "source": "Medical Reference",
        "category": "symptoms",
        "content": (
            "A fever is a temporary increase in body temperature, often due to illness. A body "
            "temperature of 100.4°F (38°C) or higher is generally considered a fever. For adults, "
            "a fever may be uncomfortable but usually is not dangerous unless it reaches 103°F "
            "(39.4°C) or higher. For infants and toddlers, even a slightly elevated temperature "
            "may indicate a serious infection. Seek emergency care for: temperature above 103°F, "
            "fever lasting more than 3 days, fever with severe headache, unusual skin rash, "
            "stiff neck, confusion, persistent vomiting, or difficulty breathing. Rest, stay "
            "hydrated, and take over-the-counter fever reducers like acetaminophen or ibuprofen."
        ),
    },
    {
        "id": "chest-pain-overview",
        "source": "Medical Reference - Emergency",
        "category": "emergency",
        "content": (
            "Chest pain can have many causes. Some are serious and require immediate medical "
            "attention. CALL EMERGENCY SERVICES (911) if chest pain: feels like pressure, "
            "squeezing, or tightness; spreads to the jaw, left arm, or back; comes with "
            "shortness of breath, cold sweat, nausea, or dizziness; occurs suddenly during "
            "physical activity. Other causes include: GERD (burning sensation after eating), "
            "muscle strain (pain that worsens with movement), anxiety/panic attacks (rapid "
            "heartbeat, tingling, feeling of doom), and costochondritis (inflammation of rib "
            "cartilage). Always err on the side of caution with chest pain."
        ),
    },
    {
        "id": "cold-flu-overview",
        "source": "Medical Reference",
        "category": "conditions",
        "content": (
            "The common cold and flu are both respiratory illnesses but caused by different "
            "viruses. Cold symptoms develop gradually: runny/stuffy nose, sore throat, sneezing, "
            "mild cough. Flu symptoms come on suddenly: high fever, body aches, fatigue, dry "
            "cough, headache. Self-care for colds: rest, fluids, over-the-counter decongestants "
            "and pain relievers. See a doctor for flu if: symptoms are severe, you are in a "
            "high-risk group (over 65, pregnant, chronic conditions), or symptoms improve then "
            "return with fever and worse cough. Antiviral medications like oseltamivir (Tamiflu) "
            "work best when started within 48 hours of symptom onset."
        ),
    },
    {
        "id": "mental-health-overview",
        "source": "Medical Reference - Mental Health",
        "category": "mental_health",
        "content": (
            "Mental health is an essential part of overall health. Common conditions include: "
            "Depression (persistent sadness, loss of interest, fatigue, changes in sleep/appetite), "
            "Anxiety disorders (excessive worry, restlessness, difficulty concentrating), "
            "Panic disorder (sudden intense fear with physical symptoms). Seek help if symptoms "
            "persist for more than 2 weeks or interfere with daily life. Treatment options include "
            "therapy (CBT is highly effective), medication, lifestyle changes (exercise, sleep "
            "hygiene, stress management), and support groups. If you or someone you know is in "
            "crisis, contact the 988 Suicide & Crisis Lifeline (call or text 988) or go to the "
            "nearest emergency room."
        ),
    },
    {
        "id": "diabetes-overview",
        "source": "Medical Reference",
        "category": "chronic_conditions",
        "content": (
            "Diabetes is a chronic condition affecting how the body processes blood sugar. "
            "Type 1: The body doesn't produce insulin (autoimmune, usually diagnosed in childhood). "
            "Type 2: The body doesn't use insulin effectively (most common, linked to lifestyle). "
            "Symptoms include increased thirst, frequent urination, unexplained weight loss, "
            "fatigue, blurred vision, and slow-healing wounds. Management includes: regular blood "
            "sugar monitoring, medication/insulin as prescribed, balanced diet (limit refined carbs "
            "and sugars), regular exercise (150 min/week), and annual eye, kidney, and foot exams. "
            "See a doctor immediately for: blood sugar over 300 mg/dL, fruity-smelling breath, "
            "nausea/vomiting with high blood sugar, or confusion."
        ),
    },
    {
        "id": "back-pain-overview",
        "source": "Medical Reference",
        "category": "symptoms",
        "content": (
            "Back pain is extremely common and one of the leading causes of missed work. Most "
            "back pain improves within a few weeks with self-care. Causes include muscle/ligament "
            "strain, bulging or ruptured discs, arthritis, skeletal irregularities, and "
            "osteoporosis. Self-care: stay active (bed rest can worsen it), apply ice for the "
            "first 48-72 hours then switch to heat, over-the-counter pain relievers, and gentle "
            "stretching. See a doctor if back pain: persists beyond a few weeks, is severe and "
            "doesn't improve with rest, spreads down one or both legs (especially below the knee), "
            "causes weakness/numbness/tingling, or is accompanied by unexplained weight loss. "
            "Seek emergency care if back pain occurs after a fall/injury or with bowel/bladder problems."
        ),
    },
    {
        "id": "allergies-overview",
        "source": "Medical Reference",
        "category": "conditions",
        "content": (
            "Allergies occur when the immune system reacts to a foreign substance. Common "
            "allergens: pollen, dust mites, mold, pet dander, certain foods (nuts, shellfish, "
            "eggs), insect stings, and medications. Symptoms vary by type: Hay fever (sneezing, "
            "itchy eyes/nose, runny nose), food allergies (tingling mouth, hives, swelling, "
            "digestive issues), insect sting allergies (swelling, hives, anaphylaxis risk). "
            "ANAPHYLAXIS IS A MEDICAL EMERGENCY — symptoms include: difficulty breathing, "
            "swelling of throat/tongue, rapid pulse, dizziness, drop in blood pressure. Use "
            "epinephrine (EpiPen) immediately and call 911. Management: avoid known allergens, "
            "antihistamines for mild symptoms, immunotherapy (allergy shots) for long-term relief."
        ),
    },
    {
        "id": "hypertension-overview",
        "source": "Medical Reference",
        "category": "chronic_conditions",
        "content": (
            "High blood pressure (hypertension) is often called the 'silent killer' because it "
            "usually has no symptoms. Normal BP: less than 120/80 mmHg. Elevated: 120-129/<80. "
            "Stage 1 hypertension: 130-139/80-89. Stage 2: 140+/90+. Hypertensive crisis: "
            "180+/120+ (seek emergency care). Risk factors: age, family history, obesity, "
            "sedentary lifestyle, high sodium diet, excessive alcohol, stress. Management: "
            "DASH diet (rich in fruits, vegetables, whole grains, lean proteins), limit sodium "
            "to 1,500-2,300 mg/day, regular exercise (30 min most days), maintain healthy weight, "
            "limit alcohol, manage stress, take prescribed medications consistently. Regular "
            "monitoring is essential."
        ),
    },
    {
        "id": "sleep-disorders-overview",
        "source": "Medical Reference",
        "category": "conditions",
        "content": (
            "Sleep disorders affect the quality, timing, and amount of sleep. Common types: "
            "Insomnia (difficulty falling/staying asleep), Sleep Apnea (breathing repeatedly "
            "stops during sleep — snoring, gasping, daytime fatigue), Restless Leg Syndrome "
            "(uncomfortable sensations in legs at rest). Good sleep hygiene: maintain consistent "
            "sleep/wake times, keep bedroom dark/cool/quiet, avoid screens 1 hour before bed, "
            "limit caffeine after noon, exercise regularly (but not close to bedtime), avoid "
            "large meals before sleep. See a doctor if: difficulty sleeping most nights for more "
            "than 3 weeks, loud snoring with gasping/choking, excessive daytime sleepiness "
            "affecting daily activities, or falling asleep at inappropriate times."
        ),
    },
]


def seed_knowledge_base() -> dict:
    """
    Seed the ChromaDB vector store with sample medical knowledge.

    Returns stats about the ingestion.
    """
    documents = [item["content"] for item in SAMPLE_MEDICAL_KNOWLEDGE]
    metadatas = [
        {"source": item["source"], "category": item["category"]}
        for item in SAMPLE_MEDICAL_KNOWLEDGE
    ]
    ids = [item["id"] for item in SAMPLE_MEDICAL_KNOWLEDGE]

    # Check if already seeded
    stats = rag_retriever.get_stats()
    if stats["total_documents"] >= len(documents):
        logger.info(f"Knowledge base already has {stats['total_documents']} documents, skipping seed")
        return stats

    rag_retriever.add_documents(
        documents=documents,
        metadatas=metadatas,
        ids=ids,
    )

    updated_stats = rag_retriever.get_stats()
    logger.info(f"✅ Seeded knowledge base with {updated_stats['total_documents']} documents")
    return updated_stats
