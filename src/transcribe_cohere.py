# Optimized transcription with Cohere Transcribe model

MODEL_ID = "CohereLabs/cohere-transcribe-03-2026"
MODEL_REVISION = "499888924f5f1313b48ab0686c8f3a94178a4709"

import warnings
import threading
import os
import time
import sys
import torch
import numpy as np
from transformers import AutoProcessor, AutoModelForSpeechSeq2Seq
from huggingface_hub import login

# Filter out various warnings
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", message=".*Init provider bridge failed.*")

# Global variables to hold the preloaded model and processor
_model = None
_processor = None
_model_lock = threading.Lock()

def get_token():
    """Retrieve the token from the HF_TOKEN file, environment, or cache."""
    # 1. Check local HF_TOKEN file in current working directory (important for nix run)
    cwd_token_file = os.path.join(os.getcwd(), "HF_TOKEN")
    if os.path.exists(cwd_token_file):
        try:
            with open(cwd_token_file, "r") as f:
                token = f.read().strip()
                if token:
                    return token
        except Exception as e:
            print(f"⚠️ Error reading {cwd_token_file}: {e}")

    # 2. Check local HF_TOKEN file in project root (relative to script)
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    hf_token_file = os.path.join(root_dir, "HF_TOKEN")
    if os.path.exists(hf_token_file):
        try:
            with open(hf_token_file, "r") as f:
                token = f.read().strip()
                if token:
                    return token
        except Exception as e:
            pass

    # 3. Check if already set via env
    token = os.environ.get("HF_TOKEN")
    if token:
        return token
    
    # 4. Last fallback: HF cache
    token_path = os.path.expanduser("~/.cache/huggingface/token")
    if os.path.exists(token_path):
        try:
            with open(token_path, "r") as f:
                token = f.read().strip()
                if token:
                    return token
        except:
            pass
            
    return None

def check_auth():
    """Check if the user is authenticated with Hugging Face and log in if a token is found."""
    token = get_token()
    
    if token:
        # Mask the token for printing
        masked = token[:6] + "..." + token[-4:] if len(token) > 10 else "******"
        print(f"🔑 Authentication detected (token: {masked})")
        try:
            # Login for the current session
            login(token=token, add_to_git_credential=False)
            # Also ensure it's in os.environ as some libraries expect it there
            os.environ["HF_TOKEN"] = token
            return True
        except Exception as e:
            print(f"⚠️ Error during Hugging Face login: {e}")
            return False

    print("\n🔑 Hugging Face Authentication Info")
    print(f"The model '{MODEL_ID}' is gated and requires access.")
    print("Please ensure one of the following:")
    print(f"  - A file named 'HF_TOKEN' exists in your current directory ({os.getcwd()})")
    print("  - The HF_TOKEN environment variable is set")
    print("  - You have logged in via 'huggingface-cli login'")
    print(f"Access must be granted at: https://huggingface.co/CohereLabs/cohere-transcribe-03-2026\n")
    return False

def load_model(model_id=MODEL_ID, revision=MODEL_REVISION, device="cpu"):
    """Load model with optimized parameters for the current device"""
    token = get_token()
    
    # Use 'dtype' instead of deprecated 'torch_dtype'
    dtype = torch.float16 if device == "cuda" else torch.float32
    
    # Try loading from local cache first to avoid "checking for updates" network hit
    try:
        print(f"🚀 Initializing Cohere model '{model_id}' (from cache)...")
        processor = AutoProcessor.from_pretrained(
            model_id, 
            revision=revision,
            trust_remote_code=True,
            token=token,
            local_files_only=True
        )
        
        # Patch for transformers compatibility issue in CohereAsrTokenizer
        if hasattr(processor, "tokenizer"):
            if not hasattr(processor.tokenizer, "additional_special_tokens"):
                processor.tokenizer.additional_special_tokens = []
        
        model = AutoModelForSpeechSeq2Seq.from_pretrained(
            model_id,
            revision=revision,
            dtype=dtype,
            trust_remote_code=True,
            token=token,
            local_files_only=True
        ).to(device)
        
        print("✅ Loaded from local cache.")
        return model, processor
    except Exception as e:
        # If local loading failed, we probably need to download or verify
        print(f"ℹ️ Model not in cache or update needed: {e}")
        print(f"🚀 Downloading/Verifying Cohere model '{model_id}'...")
        
        # Now check auth and login only when we actually need network
        check_auth()
        token = get_token()
        
        try:
            processor = AutoProcessor.from_pretrained(
                model_id, 
                revision=revision,
                trust_remote_code=True,
                token=token
            )
            
            if hasattr(processor, "tokenizer"):
                if not hasattr(processor.tokenizer, "additional_special_tokens"):
                    processor.tokenizer.additional_special_tokens = []
            
            model = AutoModelForSpeechSeq2Seq.from_pretrained(
                model_id,
                revision=revision,
                dtype=dtype,
                trust_remote_code=True,
                token=token
            ).to(device)
            
            # Optional: compile the encoder for better performance if on Linux/CUDA
            if device == "cuda" and os.name == "posix":
                try:
                    print("Compiling model for faster inference...")
                    model.model.encoder = torch.compile(model.model.encoder)
                except Exception as e:
                    print(f"Compilation skipped: {e}")
                    
            return model, processor
        except Exception as e:
            error_str = str(e).lower()
            if "403" in error_str or "access" in error_str or "unauthorized" in error_str or "401" in error_str:
                print("\n❌ Error: Access denied to gated model.")
                print(f"Make sure you have been granted access at: https://huggingface.co/{model_id}")
                print("Check that your HF_TOKEN is correct and has 'Read' permissions.")
                if token:
                    masked = token[:6] + "..." + token[-4:] if len(token) > 10 else "******"
                    print(f"Current token (masked): {masked}")
            raise e

def get_model(model_id=MODEL_ID, revision=MODEL_REVISION, device="cpu"):
    """Get or initialize the model and processor singleton"""
    global _model, _processor
    
    with _model_lock:
        if _model is None:
            start_time = time.time()
            _model, _processor = load_model(model_id, revision, device)
            elapsed = time.time() - start_time
            print(f"✅ Model loaded and ready in {elapsed:.2f} seconds")
    
    return _model, _processor

def preload_model(device="cpu"):
    """Preload the model in a background thread with a warmup call"""
    def _preload():
        try:
            model, processor = get_model(device=device)
            
            # Warmup call with 0.1s of silence to trigger compilation/optimization
            print("🔥 Warming up model (this may take a moment if compiling)...")
            warmup_audio = np.zeros(int(16000 * 0.1), dtype=np.float32)
            
            model.transcribe(
                processor=processor,
                audio_arrays=[warmup_audio],
                sample_rates=[16000],
                language="en",
                compile=True if device == "cuda" else False,
                pipeline_detokenization=True if os.name == "posix" else False
            )
            print("✨ Warmup complete! Ready for instant transcription.")
        except Exception as e:
            print(f"⚠️ Preload/Warmup error: {e}")
    
    thread = threading.Thread(target=_preload)
    thread.daemon = True
    thread.start()
    return thread

def transcribe_audio(audio_data=None, audio_path=None, sample_rate=16000, device="cpu", language="en"):
    """Transcribe audio with Cohere model"""
    try:
        model, processor = get_model(device=device)
    except Exception as e:
        return f"Error loading model: {e}"
    
    start_time = time.time()
    
    try:
        if audio_data is not None:
            if hasattr(audio_data, "flatten"):
                audio_data = audio_data.flatten()
            
            results = model.transcribe(
                processor=processor,
                audio_arrays=[audio_data],
                sample_rates=[sample_rate],
                language=language,
                compile=True if device == "cuda" else False,
                pipeline_detokenization=True if os.name == "posix" else False
            )
        else:
            results = model.transcribe(
                processor=processor,
                audio_files=[audio_path],
                language=language,
                compile=True if device == "cuda" else False,
                pipeline_detokenization=True if os.name == "posix" else False
            )
        
        if isinstance(results, list):
            transcription = " ".join(results)
        else:
            transcription = str(results)
            
    except Exception as e:
        print(f"Transcription error: {e}")
        transcription = ""
    
    elapsed = time.time() - start_time
    print(f"Transcription completed in {elapsed:.2f} seconds")
    
    return transcription

def unload_model():
    """Unload the model to free up memory"""
    global _model, _processor
    with _model_lock:
        if _model is not None:
            print("📤 Unloading Cohere model...")
            _model.cpu()
            del _model
            _model = None
            del _processor
            _processor = None
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            import gc
            gc.collect()
            print("✅ Cohere model unloaded.")
            
            # Force CUDA synchronization for complete cleanup
            try:
                if torch.cuda.is_available():
                    torch.cuda.synchronize()
            except:
                pass
