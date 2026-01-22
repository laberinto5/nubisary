# Gradio Web App Deploy

This guide covers running the Nubisary web app locally and deploying it to Hugging Face Spaces.

## Local Run

```bash
pip install -r requirements.txt
python app.py
```

Open the local URL printed in the console (usually `http://127.0.0.1:7860`).

## Hugging Face Spaces (Gradio)

### Recommended Setup (GitHub repo linked)

1. Create a Space (type: **Gradio**).
2. In the Space settings, link this GitHub repository.
3. Use the `main` branch.
4. Ensure these files exist at repo root:
   - `app.py` (Gradio entrypoint)
   - `requirements.txt`
5. Push changes to `main`; the Space rebuilds automatically.

Space: https://huggingface.co/spaces/laberintos/nubisary  
The public app URL appears in the Space UI after a successful build.

### Notes

- The entrypoint for Gradio Spaces is `app.py` by default.
- Keep the app light and avoid heavy downloads at runtime.
- This Space is synced from the GitHub repository; GitHub is the single source of truth.

