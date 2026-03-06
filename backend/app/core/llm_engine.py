"""LLM Engine — Ollama integration via LangChain with model switching."""

import logging
from typing import AsyncGenerator, Optional

from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage

from app.config import get_settings
from app.core.prompts import SYSTEM_PROMPT, RAG_CONTEXT_PROMPT, CONVERSATION_TITLE_PROMPT
from app.core.safety import check_safety, add_disclaimer
from app.core.memory import memory
from app.core.rag_pipeline import rag_retriever

logger = logging.getLogger(__name__)
settings = get_settings()

# Track active model per session (default from config)
_active_model: str = settings.DEFAULT_MODEL


def get_active_model() -> str:
    """Get the currently active Ollama model."""
    return _active_model


def set_active_model(model_name: str) -> bool:
    """
    Switch the active Ollama model.
    Accepts both short names (llama3) and full Ollama names (llama3:latest).
    """
    global _active_model
    # Accept any model — Ollama availability is already verified in settings.py
    _active_model = model_name
    logger.info(f"Switched active model to: {model_name}")
    return True


def _create_llm(model: Optional[str] = None, streaming: bool = False) -> ChatOllama:
    """Create a ChatOllama instance."""
    return ChatOllama(
        base_url=settings.OLLAMA_BASE_URL,
        model=model or _active_model,
        temperature=0.7,
        streaming=streaming,
    )


async def chat(
    user_message: str,
    conversation_id: str,
    model: Optional[str] = None,
    user_context: Optional[str] = None,
) -> str:
    """
    Process a user message and return an AI response (non-streaming).

    Steps:
    1. Safety check
    2. Retrieve RAG context
    3. Load conversation history
    4. Generate response via Ollama
    5. Save to memory
    6. Add disclaimer
    """
    # 1. Safety check
    is_safe, override_response, urgency = check_safety(user_message)
    if not is_safe and override_response:
        # Save both messages to memory even for overrides
        await memory.add_message(conversation_id, "human", user_message)
        await memory.add_message(conversation_id, "ai", override_response)
        return override_response

    # 2. Retrieve relevant medical context via RAG
    rag_context = await rag_retriever.retrieve(user_message)

    # 3. Load conversation history
    history = await memory.get_messages(conversation_id)

    # 4. Build message chain with personalized system prompt
    system = SYSTEM_PROMPT
    if user_context:
        system = f"{SYSTEM_PROMPT}\n\n## Patient Profile\n{user_context}"
    messages = [SystemMessage(content=system)]
    messages.extend(history)

    # Inject RAG context if available
    if rag_context:
        augmented_message = RAG_CONTEXT_PROMPT.format(
            context=rag_context, question=user_message
        )
    else:
        augmented_message = user_message

    messages.append(HumanMessage(content=augmented_message))

    # 5. Generate response
    llm = _create_llm(model=model)
    response = await llm.ainvoke(messages)
    response_text = response.content

    # 6. Save to memory
    await memory.add_message(conversation_id, "human", user_message)
    await memory.add_message(conversation_id, "ai", response_text)

    # 7. Add disclaimer
    return add_disclaimer(response_text)


async def chat_stream(
    user_message: str,
    conversation_id: str,
    model: Optional[str] = None,
    user_context: Optional[str] = None,
) -> AsyncGenerator[str, None]:
    """
    Process a user message and stream the AI response token by token.
    Yields response chunks as they arrive from Ollama.
    """
    import time
    t0 = time.perf_counter()

    # Step 1: Safety check (should be instant)
    is_safe, override_response, urgency = check_safety(user_message)
    logger.info(f"⏱ [1] Safety check:     {(time.perf_counter()-t0)*1000:.0f}ms")

    if not is_safe and override_response:
        await memory.add_message(conversation_id, "human", user_message)
        await memory.add_message(conversation_id, "ai", override_response)
        yield override_response
        return

    # Step 2: RAG retrieval (ChromaDB query — may be slow first run)
    t1 = time.perf_counter()
    rag_context = await rag_retriever.retrieve(user_message)
    logger.info(f"⏱ [2] RAG retrieval:    {(time.perf_counter()-t1)*1000:.0f}ms  (got context: {bool(rag_context)})")

    # Step 3: Load conversation history from memory
    t2 = time.perf_counter()
    history = await memory.get_messages(conversation_id)
    logger.info(f"⏱ [3] Memory load:      {(time.perf_counter()-t2)*1000:.0f}ms  ({len(history)} messages)")

    # Build message chain with personalized system prompt
    system = SYSTEM_PROMPT
    if user_context:
        system = f"{SYSTEM_PROMPT}\n\n## Patient Profile\n{user_context}"
    messages = [SystemMessage(content=system)]
    messages.extend(history)

    if rag_context:
        augmented_message = RAG_CONTEXT_PROMPT.format(
            context=rag_context, question=user_message
        )
    else:
        augmented_message = user_message

    messages.append(HumanMessage(content=augmented_message))

    # Step 4: LLM streaming — time to first token is key metric
    t3 = time.perf_counter()
    llm = _create_llm(model=model, streaming=True)
    full_response = ""
    first_token = True

    async for chunk in llm.astream(messages):
        token = chunk.content
        if token:
            if first_token:
                logger.info(f"⏱ [4] Time-to-1st-token:{(time.perf_counter()-t3)*1000:.0f}ms  (model: {model or _active_model})")
                first_token = False
            full_response += token
            yield token

    logger.info(f"⏱ [5] Total LLM time:   {(time.perf_counter()-t3)*1000:.0f}ms  ({len(full_response)} chars)")
    logger.info(f"⏱ [TOTAL] End-to-end:   {(time.perf_counter()-t0)*1000:.0f}ms")

    # Save to memory after streaming completes
    await memory.add_message(conversation_id, "human", user_message)
    await memory.add_message(conversation_id, "ai", full_response)

    # Yield disclaimer at the end
    from app.core.safety import MEDICAL_DISCLAIMER
    if "Disclaimer" not in full_response:
        yield MEDICAL_DISCLAIMER



async def generate_title(message: str, model: Optional[str] = None) -> str:
    """Generate a short conversation title from the first message."""
    try:
        llm = _create_llm(model=model)
        prompt = CONVERSATION_TITLE_PROMPT.format(message=message)
        response = await llm.ainvoke([HumanMessage(content=prompt)])
        title = response.content.strip().strip('"').strip("'")
        return title[:60]  # Cap at 60 chars
    except Exception as e:
        logger.warning(f"Title generation failed: {e}")
        return "Health Inquiry"
