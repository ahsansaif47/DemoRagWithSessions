from sentence_transformers import SentenceTransformer
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


class E5EmbeddingService:
    def __init__(self, model_name: str= "intfloat/e5-base-v2", device="cpu"):
        self.model = SentenceTransformer(model_name, device=device)

    # NOTE: query_or_passage will be hardcoded in the ingestion/retrieval APIs.
    # Note: query for retrieval and passage for ingestion
    def embed_query(self, text: str, query_or_passage: str):
        embedding_text = ""
        if query_or_passage == "query":
            embedding_text += f"query: {text}"
        else:
            embedding_text += f"passage: {text}"

        return self.model.encode(
            embedding_text,
            normalize_embeddings=True,
            convert_to_numpy=True,
        )




text_embedder = E5EmbeddingService()
embeddings = text_embedder.embed_query("I love to play cricket", "query")
print(embeddings)




#
# embeddings = embed_image("/home/ahsansaif/projects/DemoRagWithSessions/resources/images/Book_01_Air Law/page_40_vis_0.png")
# print(embeddings)