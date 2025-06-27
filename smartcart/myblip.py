from transformers import pipeline
from PIL import Image
from transformers import pipeline, BlipProcessor, BlipForConditionalGeneration

import torch
# def get_blip_caption(image):
# # 🧠 Load the image captioning pipeline
#     captioner = pipeline("image-to-text", model="Salesforce/blip-image-captioning-base")
#
#     # 🖼️ Load your image
#     image = Image.open(image).convert("RGB")
#
#     # 💬 Generate caption
#
#
#     result = captioner(
#         image,
#         max_length=30,
#         no_repeat_ngram_size=2,
#         early_stopping=True,
#         num_beams=4
#     )
#     caption = result[0]['generated_text']
#     return caption

def get_blip_caption(image_path):
    """
    Optimized BLIP using direct model access (RECOMMENDED)
    """
    # Load model and processor directly for full control
    processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
    model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")

    # Load and preprocess image
    #image = Image.open(image_path).convert("RGB")
    inputs = processor(image_path, return_tensors="pt")

    # Generate with proper parameters
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_length=50,
            min_length=10,
            num_beams=4,
            early_stopping=True,
            no_repeat_ngram_size=3,
            repetition_penalty=1.2,
            do_sample=False
        )

    caption = processor.decode(outputs[0], skip_special_tokens=True)
    return caption

