---
source: https://github.com/suno-ai/bark
parsed_date: 2026-06-27 01:30:05
domain: github.com
---

Title: GitHub - suno-ai/bark: 🔊 Text-Prompted Generative Audio Model

URL Source: https://github.com/suno-ai/bark

Markdown Content:
> Notice: Bark is Suno's open-source text-to-speech+ model. If you are looking for our text-to-music models, please visit us on our [web page](https://suno.ai/) and join our community on [Discord](https://suno.ai/discord).

[![Image 1](https://camo.githubusercontent.com/0eadd7bcb06faf05a2aeb981a21052ef308975a7c2d2f1beaf9f96b2bff021d6/68747470733a2f2f646362616467652e76657263656c2e6170702f6170692f7365727665722f4a32423276736a4b75453f7374796c653d666c617426636f6d706163743d54727565)](https://suno.ai/discord)[![Image 2: Twitter](https://camo.githubusercontent.com/d7395ca49347f3ba8969ac22bd7aba4c6a636ec78185f9fdb2c77487be0bca25/68747470733a2f2f696d672e736869656c64732e696f2f747769747465722f75726c2f68747470732f747769747465722e636f6d2f464d2e7376673f7374796c653d736f6369616c266c6162656c3d4073756e6f5f61695f)](https://twitter.com/suno_ai_)

> 🔗 [Examples](https://suno.ai/examples/bark-v0) • [Suno Studio Waitlist](https://suno-ai.typeform.com/suno-studio) • [Updates](https://github.com/suno-ai/bark#-updates) • [How to Use](https://github.com/suno-ai/bark#-usage-in-python) • [Installation](https://github.com/suno-ai/bark#-installation) • [FAQ](https://github.com/suno-ai/bark#-faq)

[![Image 3](https://user-images.githubusercontent.com/5068315/235310676-a4b3b511-90ec-4edf-8153-7ccf14905d73.png)](https://user-images.githubusercontent.com/5068315/235310676-a4b3b511-90ec-4edf-8153-7ccf14905d73.png)

Bark is a transformer-based text-to-audio model created by [Suno](https://suno.ai/). Bark can generate highly realistic, multilingual speech as well as other audio - including music, background noise and simple sound effects. The model can also produce nonverbal communications like laughing, sighing and crying. To support the research community, we are providing access to pretrained model checkpoints, which are ready for inference and available for commercial use.

## ⚠ Disclaimer

[](https://github.com/suno-ai/bark#-disclaimer)
Bark was developed for research purposes. It is not a conventional text-to-speech model but instead a fully generative text-to-audio model, which can deviate in unexpected ways from provided prompts. Suno does not take responsibility for any output generated. Use at your own risk, and please act responsibly.

## 📖 Quick Index

[](https://github.com/suno-ai/bark#-quick-index)
*   [🚀 Updates](https://github.com/suno-ai/bark#-updates)
*   [💻 Installation](https://github.com/suno-ai/bark#-installation)
*   [🐍 Usage](https://github.com/suno-ai/bark#-usage-in-python)
*   [🌀 Live Examples](https://suno.ai/examples/bark-v0)
*   [❓ FAQ](https://github.com/suno-ai/bark#-faq)

## 🎧 Demos

[](https://github.com/suno-ai/bark#-demos)
[![Image 4: Open in Spaces](https://camo.githubusercontent.com/473bbf57da7a3f7988bcfedbe1ac9e756cb4acdaa58f9193afd193ef79e72b62/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f2546302539462541342539372d4f70656e253230696e2532305370616365732d626c75652e737667)](https://huggingface.co/spaces/suno/bark)[![Image 5: Open on Replicate](https://camo.githubusercontent.com/d4886903cf3f11518e127194f9b2765ab609e8bdfc6ab1da0b7c1fcd8f404cbb/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f2543322541452545462542382538462d4f70656e2532306f6e2532305265706c69636174652d626c75652e737667)](https://replicate.com/suno-ai/bark)[![Image 6: Open In Colab](https://camo.githubusercontent.com/eff96fda6b2e0fff8cdf2978f89d61aa434bb98c00453ae23dd0aab8d1451633/68747470733a2f2f636f6c61622e72657365617263682e676f6f676c652e636f6d2f6173736574732f636f6c61622d62616467652e737667)](https://colab.research.google.com/drive/1eJfA2XUa-mXwdMy7DoYKVYHI1iTd9Vkt?usp=sharing)

## 🚀 Updates

[](https://github.com/suno-ai/bark#-updates)
**2023.05.01**

*   ©️ Bark is now licensed under the MIT License, meaning it's now available for commercial use!

*   ⚡ 2x speed-up on GPU. 10x speed-up on CPU. We also added an option for a smaller version of Bark, which offers additional speed-up with the trade-off of slightly lower quality.

*   📕 [Long-form generation](https://github.com/suno-ai/bark/blob/main/notebooks/long_form_generation.ipynb), voice consistency enhancements and other examples are now documented in a new [notebooks](https://github.com/suno-ai/bark/blob/main/notebooks) section.

*   👥 We created a [voice prompt library](https://suno-ai.notion.site/8b8e8749ed514b0cbf3f699013548683?v=bc67cff786b04b50b3ceb756fd05f68c). We hope this resource helps you find useful prompts for your use cases! You can also join us on [Discord](https://suno.ai/discord), where the community actively shares useful prompts in the **#audio-prompts** channel.

*   💬 Growing community support and access to new features here:

[![Image 7](https://camo.githubusercontent.com/d989afd3ff6a652f414339663cb99b1c5976e4eb843d72debca4d77386b51899/68747470733a2f2f646362616467652e76657263656c2e6170702f6170692f7365727665722f4a32423276736a4b7545)](https://suno.ai/discord)

*   💾 You can now use Bark with GPUs that have low VRAM (<4GB).

**2023.04.20**

*   🐶 Bark release!

## 🐍 Usage in Python

[](https://github.com/suno-ai/bark#-usage-in-python)

### 🪑 Basics

[](https://github.com/suno-ai/bark#-basics)

from bark import SAMPLE_RATE, generate_audio, preload_models
from scipy.io.wavfile import write as write_wav
from IPython.display import Audio

# download and load all models
preload_models()

# generate audio from text
text_prompt = """
 Hello, my name is Suno. And, uh — and I like pizza. [laughs] 
 But I also have other interests such as playing tic tac toe.
"""
audio_array = generate_audio(text_prompt)

# save audio to disk
write_wav("bark_generation.wav", SAMPLE_RATE, audio_array)
  
# play text in notebook
Audio(audio_array, rate=SAMPLE_RATE)

pizza.webm[Video 17](https://private-user-images.githubusercontent.com/34592747/238155864-cfa98e54-721c-4b9c-b962-688e09db684f.webm?jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3ODI0OTg5MDMsIm5iZiI6MTc4MjQ5ODYwMywicGF0aCI6Ii8zNDU5Mjc0Ny8yMzgxNTU4NjQtY2ZhOThlNTQtNzIxYy00YjljLWI5NjItNjg4ZTA5ZGI2ODRmLndlYm0_WC1BbXotQWxnb3JpdGhtPUFXUzQtSE1BQy1TSEEyNTYmWC1BbXotQ3JlZGVudGlhbD1BS0lBVkNPRFlMU0E1M1BRSzRaQSUyRjIwMjYwNjI2JTJGdXMtZWFzdC0xJTJGczMlMkZhd3M0X3JlcXVlc3QmWC1BbXotRGF0ZT0yMDI2MDYyNlQxODMwMDNaJlgtQW16LUV4cGlyZXM9MzAwJlgtQW16LVNpZ25hdHVyZT1lZjEzODQyZmVjODA1NTgxYWVlMjI1ZWMxMTE1MzM3Y2I0YzRkM2M3OTBlYjVhYWFiNTJkMjA5Y2YxMWZiYjkwJlgtQW16LVNpZ25lZEhlYWRlcnM9aG9zdCZyZXNwb25zZS1jb250ZW50LXR5cGU9dmlkZW8lMkZ3ZWJtIn0.UVjUaNwAhkokIX9JCz8Gzy17cdb_-KllWLnWJ6pw96I)

### 🌎 Foreign Language

[](https://github.com/suno-ai/bark#-foreign-language)

 Bark supports various languages out-of-the-box and automatically determines language from input text. When prompted with code-switched text, Bark will attempt to employ the native accent for the respective languages. English quality is best for the time being, and we expect other languages to further improve with scaling. 

text_prompt = """
 추석은 내가 가장 좋아하는 명절이다. 나는 며칠 동안 휴식을 취하고 친구 및 가족과 시간을 보낼 수 있습니다.
"""
audio_array = generate_audio(text_prompt)

suno_korean.webm[Video 18](https://private-user-images.githubusercontent.com/32879321/235313033-dc4477b9-2da0-4b94-9c8b-a8c2d8f5bb5e.webm?jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3ODI0OTg5MDMsIm5iZiI6MTc4MjQ5ODYwMywicGF0aCI6Ii8zMjg3OTMyMS8yMzUzMTMwMzMtZGM0NDc3YjktMmRhMC00Yjk0LTljOGItYThjMmQ4ZjViYjVlLndlYm0_WC1BbXotQWxnb3JpdGhtPUFXUzQtSE1BQy1TSEEyNTYmWC1BbXotQ3JlZGVudGlhbD1BS0lBVkNPRFlMU0E1M1BRSzRaQSUyRjIwMjYwNjI2JTJGdXMtZWFzdC0xJTJGczMlMkZhd3M0X3JlcXVlc3QmWC1BbXotRGF0ZT0yMDI2MDYyNlQxODMwMDNaJlgtQW16LUV4cGlyZXM9MzAwJlgtQW16LVNpZ25hdHVyZT0zMTkyOTZlNTJkZmY4YTQxZjM4MDk2ZmFjNDdhZjIzN2Y1YzE1MmVlNDJkY2M1N2VkMTdjY2EyNzgyZDBkYTZlJlgtQW16LVNpZ25lZEhlYWRlcnM9aG9zdCZyZXNwb25zZS1jb250ZW50LXR5cGU9dmlkZW8lMkZ3ZWJtIn0.eJIt8qKM6m0Yucu6_LwitsbKVYZucrrrO_BDI7FN7nM)

_Note: since Bark recognizes languages automatically from input text, it is possible to use, for example, a german history prompt with english text. This usually leads to english audio with a german accent._

text_prompt = """
 Der Dreißigjährige Krieg (1618-1648) war ein verheerender Konflikt, der Europa stark geprägt hat.
 This is a beginning of the history. If you want to hear more, please continue.
"""
audio_array = generate_audio(text_prompt)

suno_german_accent.webm[Video 19](https://private-user-images.githubusercontent.com/34592747/238156830-3f96ab3e-02ec-49cb-97a6-cf5af0b3524a.webm?jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3ODI0OTg5MDMsIm5iZiI6MTc4MjQ5ODYwMywicGF0aCI6Ii8zNDU5Mjc0Ny8yMzgxNTY4MzAtM2Y5NmFiM2UtMDJlYy00OWNiLTk3YTYtY2Y1YWYwYjM1MjRhLndlYm0_WC1BbXotQWxnb3JpdGhtPUFXUzQtSE1BQy1TSEEyNTYmWC1BbXotQ3JlZGVudGlhbD1BS0lBVkNPRFlMU0E1M1BRSzRaQSUyRjIwMjYwNjI2JTJGdXMtZWFzdC0xJTJGczMlMkZhd3M0X3JlcXVlc3QmWC1BbXotRGF0ZT0yMDI2MDYyNlQxODMwMDNaJlgtQW16LUV4cGlyZXM9MzAwJlgtQW16LVNpZ25hdHVyZT05N2RmMjMwMGZlOTFlM2YzMzdkNGUxOTZmNmFkMzVkNjEwNWYxMTZlMTEzODQ3MmQzMDM4YmRjMTEyMTY2MjQ3JlgtQW16LVNpZ25lZEhlYWRlcnM9aG9zdCZyZXNwb25zZS1jb250ZW50LXR5cGU9dmlkZW8lMkZ3ZWJtIn0.QWRSCVr6L7kFOEi3sRnWfS7-YeATWf2mP9nIDSwPSbg)

### 🎶 Music

[](https://github.com/suno-ai/bark#-music) Bark can generate all types of audio, and, in principle, doesn't see a difference between speech and music. Sometimes Bark chooses to generate text as music, but you can help it out by adding music notes around your lyrics. 

text_prompt = """
 ♪ In the jungle, the mighty jungle, the lion barks tonight ♪
"""
audio_array = generate_audio(text_prompt)

lion.webm[Video 20](https://private-user-images.githubusercontent.com/5068315/230684766-97f5ea23-ad99-473c-924b-66b6fab24289.webm?jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3ODI0OTg5MDMsIm5iZiI6MTc4MjQ5ODYwMywicGF0aCI6Ii81MDY4MzE1LzIzMDY4NDc2Ni05N2Y1ZWEyMy1hZDk5LTQ3M2MtOTI0Yi02NmI2ZmFiMjQyODkud2VibT9YLUFtei1BbGdvcml0aG09QVdTNC1ITUFDLVNIQTI1NiZYLUFtei1DcmVkZW50aWFsPUFLSUFWQ09EWUxTQTUzUFFLNFpBJTJGMjAyNjA2MjYlMkZ1cy1lYXN0LTElMkZzMyUyRmF3czRfcmVxdWVzdCZYLUFtei1EYXRlPTIwMjYwNjI2VDE4MzAwM1omWC1BbXotRXhwaXJlcz0zMDAmWC1BbXotU2lnbmF0dXJlPWM5MTQwNjU4MjY4NzQ5OTFiN2E3ZjliMDQwNDAzYTQ0M2M3ZGYyZjk3ODJiZGI2MjYwNjQ0NjFkOTA4ODRkZjgmWC1BbXotU2lnbmVkSGVhZGVycz1ob3N0JnJlc3BvbnNlLWNvbnRlbnQtdHlwZT12aWRlbyUyRndlYm0ifQ.XJ33J2SY1OOp3xWHIMd2NkVyOjSXnTXD9W0gQM-yunc)

### 🎤 Voice Presets

[](https://github.com/suno-ai/bark#-voice-presets)
Bark supports 100+ speaker presets across [supported languages](https://github.com/suno-ai/bark#supported-languages). You can browse the library of supported voice presets [HERE](https://suno-ai.notion.site/8b8e8749ed514b0cbf3f699013548683?v=bc67cff786b04b50b3ceb756fd05f68c), or in the [code](https://github.com/suno-ai/bark/blob/main/bark/assets/prompts). The community also often shares presets in [Discord](https://discord.gg/J2B2vsjKuE).

> Bark tries to match the tone, pitch, emotion and prosody of a given preset, but does not currently support custom voice cloning. The model also attempts to preserve music, ambient noise, etc.

text_prompt = """
 I have a silky smooth voice, and today I will tell you about 
 the exercise regimen of the common sloth.
"""
audio_array = generate_audio(text_prompt, history_prompt="v2/en_speaker_1")

sloth.webm[Video 21](https://private-user-images.githubusercontent.com/5068315/230684883-a344c619-a560-4ff5-8b99-b4463a34487b.webm?jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3ODI0OTg5MDMsIm5iZiI6MTc4MjQ5ODYwMywicGF0aCI6Ii81MDY4MzE1LzIzMDY4NDg4My1hMzQ0YzYxOS1hNTYwLTRmZjUtOGI5OS1iNDQ2M2EzNDQ4N2Iud2VibT9YLUFtei1BbGdvcml0aG09QVdTNC1ITUFDLVNIQTI1NiZYLUFtei1DcmVkZW50aWFsPUFLSUFWQ09EWUxTQTUzUFFLNFpBJTJGMjAyNjA2MjYlMkZ1cy1lYXN0LTElMkZzMyUyRmF3czRfcmVxdWVzdCZYLUFtei1EYXRlPTIwMjYwNjI2VDE4MzAwM1omWC1BbXotRXhwaXJlcz0zMDAmWC1BbXotU2lnbmF0dXJlPWZlMmMyMDc5Y2ZhYzAwNDllZjVhNjJiMmE1MjMxOWIxMzFiMWQxYTRiOGI0M2Q0MDhkNTc4MTk4ZWZiOTQ2NTEmWC1BbXotU2lnbmVkSGVhZGVycz1ob3N0JnJlc3BvbnNlLWNvbnRlbnQtdHlwZT12aWRlbyUyRndlYm0ifQ.W-ylUoKvdTykKIDFarxSlcMdzMlXG2X894NSwhZLsSY)

### 📃 Generating Longer Audio

[](https://github.com/suno-ai/bark#-generating-longer-audio)
By default, `generate_audio` works well with around 13 seconds of spoken text. For an example of how to do long-form generation, see 👉 **[Notebook](https://github.com/suno-ai/bark/blob/main/notebooks/long_form_generation.ipynb)** 👈

Click to toggle example long-form generations (from the example notebook)

dialog.webm[Video 22](https://private-user-images.githubusercontent.com/2565833/235463539-f57608da-e4cb-4062-8771-148e29512b01.webm?jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3ODI0OTg5MDMsIm5iZiI6MTc4MjQ5ODYwMywicGF0aCI6Ii8yNTY1ODMzLzIzNTQ2MzUzOS1mNTc2MDhkYS1lNGNiLTQwNjItODc3MS0xNDhlMjk1MTJiMDEud2VibT9YLUFtei1BbGdvcml0aG09QVdTNC1ITUFDLVNIQTI1NiZYLUFtei1DcmVkZW50aWFsPUFLSUFWQ09EWUxTQTUzUFFLNFpBJTJGMjAyNjA2MjYlMkZ1cy1lYXN0LTElMkZzMyUyRmF3czRfcmVxdWVzdCZYLUFtei1EYXRlPTIwMjYwNjI2VDE4MzAwM1omWC1BbXotRXhwaXJlcz0zMDAmWC1BbXotU2lnbmF0dXJlPTliZmQ3OTNiMWU2YzAyMTUzMmUxYTk2NjA2YmY0MDdmOTg4MWQ0YzM3ZmEyYWZmN2Q3ZDE5MGVmNDNkNjM3ZGMmWC1BbXotU2lnbmVkSGVhZGVycz1ob3N0JnJlc3BvbnNlLWNvbnRlbnQtdHlwZT12aWRlbyUyRndlYm0ifQ.cgnfwyOwe8fGAHs0RPJnXGK-jv7eSjvgTI5FTVE6o5U)

longform_advanced.webm[Video 23](https://private-user-images.githubusercontent.com/2565833/235463547-1c0d8744-269b-43fe-9630-897ea5731652.webm?jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3ODI0OTg5MDMsIm5iZiI6MTc4MjQ5ODYwMywicGF0aCI6Ii8yNTY1ODMzLzIzNTQ2MzU0Ny0xYzBkODc0NC0yNjliLTQzZmUtOTYzMC04OTdlYTU3MzE2NTIud2VibT9YLUFtei1BbGdvcml0aG09QVdTNC1ITUFDLVNIQTI1NiZYLUFtei1DcmVkZW50aWFsPUFLSUFWQ09EWUxTQTUzUFFLNFpBJTJGMjAyNjA2MjYlMkZ1cy1lYXN0LTElMkZzMyUyRmF3czRfcmVxdWVzdCZYLUFtei1EYXRlPTIwMjYwNjI2VDE4MzAwM1omWC1BbXotRXhwaXJlcz0zMDAmWC1BbXotU2lnbmF0dXJlPTQzZjZiYTMxMjFjZGM5ZTJhMDdiMTVjMmRjY2M0YzQyMTk4ZmY4Y2QyM2YwZjVkOTc0ZDc5NDRjNDZmYzEwYWImWC1BbXotU2lnbmVkSGVhZGVycz1ob3N0JnJlc3BvbnNlLWNvbnRlbnQtdHlwZT12aWRlbyUyRndlYm0ifQ.SDH9h4HBsjxaixnXvINBNnEENb9Qv1ImECo3NLwxBqw)

longform_basic.webm[Video 24](https://private-user-images.githubusercontent.com/2565833/235463559-87efe9f8-a2db-4d59-b764-57db83f95270.webm?jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3ODI0OTg5MDMsIm5iZiI6MTc4MjQ5ODYwMywicGF0aCI6Ii8yNTY1ODMzLzIzNTQ2MzU1OS04N2VmZTlmOC1hMmRiLTRkNTktYjc2NC01N2RiODNmOTUyNzAud2VibT9YLUFtei1BbGdvcml0aG09QVdTNC1ITUFDLVNIQTI1NiZYLUFtei1DcmVkZW50aWFsPUFLSUFWQ09EWUxTQTUzUFFLNFpBJTJGMjAyNjA2MjYlMkZ1cy1lYXN0LTElMkZzMyUyRmF3czRfcmVxdWVzdCZYLUFtei1EYXRlPTIwMjYwNjI2VDE4MzAwM1omWC1BbXotRXhwaXJlcz0zMDAmWC1BbXotU2lnbmF0dXJlPTM3ODVhMDM2ZDZkNmNjN2E4MmUxOTI2NmVjZjAzNzQ0NTgzYmRhNjJmZDYzN2QxOWVkZGFiZGQ1ODY5YmJhYjImWC1BbXotU2lnbmVkSGVhZGVycz1ob3N0JnJlc3BvbnNlLWNvbnRlbnQtdHlwZT12aWRlbyUyRndlYm0ifQ.8o5XIu2q1GAgYFkbrUjGfLsXL0Ho9w_VQcgNTx9RVX8)

## Command line

[](https://github.com/suno-ai/bark#command-line)

```
python -m bark --text "Hello, my name is Suno." --output_filename "example.wav"
```

## 💻 Installation

[](https://github.com/suno-ai/bark#-installation)
_‼️ CAUTION ‼️ Do NOT use `pip install bark`. It installs a different package, which is not managed by Suno._

pip install git+https://github.com/suno-ai/bark.git

or

git clone https://github.com/suno-ai/bark
cd bark && pip install . 

## 🤗 Transformers Usage

[](https://github.com/suno-ai/bark#-transformers-usage)
Bark is available in the 🤗 Transformers library from version 4.31.0 onwards, requiring minimal dependencies and additional packages. Steps to get started:

1.   First install the 🤗 [Transformers library](https://github.com/huggingface/transformers) from main:

```
pip install git+https://github.com/huggingface/transformers.git
```

1.   Run the following Python code to generate speech samples:

from transformers import AutoProcessor, BarkModel

processor = AutoProcessor.from_pretrained("suno/bark")
model = BarkModel.from_pretrained("suno/bark")

voice_preset = "v2/en_speaker_6"

inputs = processor("Hello, my dog is cute", voice_preset=voice_preset)

audio_array = model.generate(**inputs)
audio_array = audio_array.cpu().numpy().squeeze()

1.   Listen to the audio samples either in an ipynb notebook:

from IPython.display import Audio

sample_rate = model.generation_config.sample_rate
Audio(audio_array, rate=sample_rate)

Or save them as a `.wav` file using a third-party library, e.g. `scipy`:

import scipy

sample_rate = model.generation_config.sample_rate
scipy.io.wavfile.write("bark_out.wav", rate=sample_rate, data=audio_array)

For more details on using the Bark model for inference using the 🤗 Transformers library, refer to the [Bark docs](https://huggingface.co/docs/transformers/main/en/model_doc/bark) or the hands-on [Google Colab](https://colab.research.google.com/drive/1dWWkZzvu7L9Bunq9zvD-W02RFUXoW-Pd?usp=sharing).

## 🛠️ Hardware and Inference Speed

[](https://github.com/suno-ai/bark#%EF%B8%8F-hardware-and-inference-speed)
Bark has been tested and works on both CPU and GPU (`pytorch 2.0+`, CUDA 11.7 and CUDA 12.0).

On enterprise GPUs and PyTorch nightly, Bark can generate audio in roughly real-time. On older GPUs, default colab, or CPU, inference time might be significantly slower. For older GPUs or CPU you might want to consider using smaller models. Details can be found in out tutorial sections here.

The full version of Bark requires around 12GB of VRAM to hold everything on GPU at the same time. To use a smaller version of the models, which should fit into 8GB VRAM, set the environment flag `SUNO_USE_SMALL_MODELS=True`.

If you don't have hardware available or if you want to play with bigger versions of our models, you can also sign up for early access to our model playground [here](https://suno-ai.typeform.com/suno-studio).

## ⚙️ Details

[](https://github.com/suno-ai/bark#%EF%B8%8F-details)
Bark is fully generative text-to-audio model devolved for research and demo purposes. It follows a GPT style architecture similar to [AudioLM](https://arxiv.org/abs/2209.03143) and [Vall-E](https://arxiv.org/abs/2301.02111) and a quantized Audio representation from [EnCodec](https://github.com/facebookresearch/encodec). It is not a conventional TTS model, but instead a fully generative text-to-audio model capable of deviating in unexpected ways from any given script. Different to previous approaches, the input text prompt is converted directly to audio without the intermediate use of phonemes. It can therefore generalize to arbitrary instructions beyond speech such as music lyrics, sound effects or other non-speech sounds.

Below is a list of some known non-speech sounds, but we are finding more every day. Please let us know if you find patterns that work particularly well on [Discord](https://suno.ai/discord)!

*   `[laughter]`
*   `[laughs]`
*   `[sighs]`
*   `[music]`
*   `[gasps]`
*   `[clears throat]`
*   `—` or `...` for hesitations
*   `♪` for song lyrics
*   CAPITALIZATION for emphasis of a word
*   `[MAN]` and `[WOMAN]` to bias Bark toward male and female speakers, respectively

### Supported Languages

[](https://github.com/suno-ai/bark#supported-languages)
| Language | Status |
| --- | --- |
| English (en) | ✅ |
| German (de) | ✅ |
| Spanish (es) | ✅ |
| French (fr) | ✅ |
| Hindi (hi) | ✅ |
| Italian (it) | ✅ |
| Japanese (ja) | ✅ |
| Korean (ko) | ✅ |
| Polish (pl) | ✅ |
| Portuguese (pt) | ✅ |
| Russian (ru) | ✅ |
| Turkish (tr) | ✅ |
| Chinese, simplified (zh) | ✅ |

Requests for future language support [here](https://github.com/suno-ai/bark/discussions/111) or in the **#forums** channel on [Discord](https://suno.ai/discord).

## 🙏 Appreciation

[](https://github.com/suno-ai/bark#-appreciation)
*   [nanoGPT](https://github.com/karpathy/nanoGPT) for a dead-simple and blazing fast implementation of GPT-style models
*   [EnCodec](https://github.com/facebookresearch/encodec) for a state-of-the-art implementation of a fantastic audio codec
*   [AudioLM](https://github.com/lucidrains/audiolm-pytorch) for related training and inference code
*   [Vall-E](https://arxiv.org/abs/2301.02111), [AudioLM](https://arxiv.org/abs/2209.03143) and many other ground-breaking papers that enabled the development of Bark

## © License

[](https://github.com/suno-ai/bark#-license)
Bark is licensed under the MIT License.

## 📱Community

[](https://github.com/suno-ai/bark#community)
*   [Twitter](https://twitter.com/suno_ai_)
*   [Discord](https://suno.ai/discord)

## 🎧Suno Studio (Early Access)

[](https://github.com/suno-ai/bark#suno-studio-early-access)
We’re developing a playground for our models, including Bark.

If you are interested, you can sign up for early access [here](https://suno-ai.typeform.com/suno-studio).

## ❓ FAQ

[](https://github.com/suno-ai/bark#-faq)
#### How do I specify where models are downloaded and cached?

[](https://github.com/suno-ai/bark#how-do-i-specify-where-models-are-downloaded-and-cached)
*   Bark uses Hugging Face to download and store models. You can see find more info [here](https://huggingface.co/docs/huggingface_hub/package_reference/environment_variables#hfhome).

#### Bark's generations sometimes differ from my prompts. What's happening?

[](https://github.com/suno-ai/bark#barks-generations-sometimes-differ-from-my-prompts-whats-happening)
*   Bark is a GPT-style model. As such, it may take some creative liberties in its generations, resulting in higher-variance model outputs than traditional text-to-speech approaches.

#### What voices are supported by Bark?

[](https://github.com/suno-ai/bark#what-voices-are-supported-by-bark)
*   Bark supports 100+ speaker presets across [supported languages](https://github.com/suno-ai/bark#supported-languages). You can browse the library of speaker presets [here](https://suno-ai.notion.site/8b8e8749ed514b0cbf3f699013548683?v=bc67cff786b04b50b3ceb756fd05f68c). The community also shares presets in [Discord](https://suno.ai/discord). Bark also supports generating unique random voices that fit the input text. Bark does not currently support custom voice cloning.

#### Why is the output limited to ~13-14 seconds?

[](https://github.com/suno-ai/bark#why-is-the-output-limited-to-13-14-seconds)
*   Bark is a GPT-style model, and its architecture/context window is optimized to output generations with roughly this length.

#### How much VRAM do I need?

[](https://github.com/suno-ai/bark#how-much-vram-do-i-need)
*   The full version of Bark requires around 12Gb of memory to hold everything on GPU at the same time. However, even smaller cards down to ~2Gb work with some additional settings. Simply add the following code snippet before your generation:

import os
os.environ["SUNO_OFFLOAD_CPU"] = "True"
os.environ["SUNO_USE_SMALL_MODELS"] = "True"

#### My generated audio sounds like a 1980s phone call. What's happening?

[](https://github.com/suno-ai/bark#my-generated-audio-sounds-like-a-1980s-phone-call-whats-happening)
*   Bark generates audio from scratch. It is not meant to create only high-fidelity, studio-quality speech. Rather, outputs could be anything from perfect speech to multiple people arguing at a baseball game recorded with bad microphones.
