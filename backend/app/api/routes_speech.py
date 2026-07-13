"""Speech endpoints: local Faster-Whisper transcription and TTS synthesis."""
from __future__ import annotations

import tempfile
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, UploadFile
from fastapi.responses import Response
from starlette.concurrency import run_in_threadpool

from app.logging_config import get_logger
from app.models.api_models import SynthesizeRequest, TranscribeResponse
from app.providers.stt.base import STTProviderError
from app.providers.tts.base import TTSProviderError
from app.state import AppState, get_state

router = APIRouter(tags=["speech"])
logger = get_logger("api.speech")

MAX_UPLOAD_BYTES = 25 * 1024 * 1024


@router.post("/speech/transcribe", response_model=TranscribeResponse)
async def transcribe(audio: UploadFile, state: AppState = Depends(get_state)) -> TranscribeResponse:
    data = await audio.read()
    if len(data) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail="Audio file is too large.")
    if not data:
        raise HTTPException(status_code=400, detail="No audio data received.")

    suffix = Path(audio.filename or "audio.webm").suffix or ".webm"
    # Audio is written to a temp file only for the duration of transcription and then
    # deleted — RIVA does not persist recordings unless explicitly enabled.
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        tmp.write(data)
        tmp_path = tmp.name

    try:
        result = await run_in_threadpool(state.stt_provider.transcribe, tmp_path)
    except STTProviderError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    finally:
        try:
            Path(tmp_path).unlink(missing_ok=True)
        except OSError:
            pass

    return TranscribeResponse(text=result.text, language=result.language, duration_seconds=result.duration_seconds)


@router.post("/speech/synthesize")
async def synthesize(payload: SynthesizeRequest, state: AppState = Depends(get_state)) -> Response:
    try:
        speech = await state.tts_provider.synthesize(payload.text)
    except TTSProviderError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    return Response(content=speech.audio_bytes, media_type=speech.content_type)
