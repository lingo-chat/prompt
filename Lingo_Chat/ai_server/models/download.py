### download model
import torch

from transformers import AutoModelForCausalLM, AutoTokenizer


def _model_download(
    model_path: str = "HEYPAL/PAL_orbit_v0.2.2.3",
    save_path: str = "./PAL_orbit_v0.2.2.3",
):
    """
    모델 다운로드
    """
    tokenizer = AutoTokenizer.from_pretrained(model_path)
    model = AutoModelForCausalLM.from_pretrained(model_path, torch_dtype=torch.bfloat16)
    try:
        # model.save_pretrained(save_path)
        # tokenizer.save_pretrained(save_path)

        print(f"Model Downloaded Successfully!!!\n\n")
    except Exception as E:
        print(f"Error occured in Model Downloaded!!\nError: {E}\n\n")


if __name__ == "__main__":   
    _model_download()