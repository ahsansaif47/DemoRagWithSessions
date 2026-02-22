import torch
from PIL import Image
import open_clip

model, _, preprocess = open_clip.create_model_and_transforms(
    "ViT-L-14", pretrained="laion2b_s32b_b82k"
)
tokenizer = open_clip.get_tokenizer("ViT-L-14")

# TODO: Call this function by saving an image to path
# Pass the path of the saved image in this function
def embed_image(image_path: str=""):
    image = Image.open(image_path).convert("RGB")
    image = preprocess(image).unsqueeze(0)

    with torch.no_grad():
        embedding = model.encode_image(image)
        embedding /= embedding.norm(dim=-1, keepdim=True)
    return embedding[0].tolist()

#
# embeddings = embed_image("/home/ahsansaif/projects/DemoRagWithSessions/resources/images/Book_01_Air Law/page_40_vis_0.png")
# print(embeddings)