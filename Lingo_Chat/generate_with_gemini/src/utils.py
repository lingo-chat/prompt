import os
import json
import jsonlines
import aiohttp

from datasets import Dataset, DatasetDict


SAFETY_SETTING = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
]


def jsonl_save(dir, json_data):
    with open(dir, "a+", encoding="utf-8") as f:
        json.dump(
            json_data, f, ensure_ascii=False
        )  # ensure_ascii로 한글이 깨지지 않게 저장
        f.write(
            "\n"
        )  # json을 쓰는 것과 같지만, 여러 줄을 써주는 것이므로 "\n"을 붙여준다.


def jsonl_read(file_dir: str):
    """
    jsonl 파일을 읽어서 list로 반환합니다.
    """
    result = []
    with jsonlines.open(file_dir) as f:
        for _data in f.iter():
            result.append(_data)
    return result


async def llm_query(
    model_url: str, api_key: str, _input: list, _generation_config: dict
):
    """
    Gemini_pro API를 이용해서(post) TEMPLATE 에 대한 답변을 리턴.
    """
    async with aiohttp.ClientSession() as session:
        headers = {"Content-Type": "application/json"}

        payload = {
            "contents": _input,
            "generationConfig": _generation_config,
            "safetySettings": SAFETY_SETTING,
        }

        async with session.post(
            model_url + api_key, headers=headers, json=payload
        ) as response:
            data = ""
            try:
                data = await response.json()
                data = data["candidates"][0]["content"]["parts"][0]["text"]
            except Exception as E:
                print(f"\n[ERROR with GEMINI API] error message:{E}\n\n")
            return data


async def stream_response(url, headers, data):
    """
    VLLM 출력 시 asynchronize 하게 print할 수 있도록 구현한 함수입니다.
    chat_comp_response에서 인자 streaming을 True로 전달하면 해당 함수가 호출됩니다.
    """
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=data) as response:
            async for line in response.content:
                try:
                    decoded_line = line.decode("utf-8").strip()
                    if decoded_line.startswith("data: "):
                        json_data = json.loads(decoded_line.split("data: ")[1])
                        chunk = (
                            json_data.get("choices", [])[0]
                            .get("delta", {})
                            .get("content", "")
                        )
                        print(chunk, end="", flush=True)
                except Exception as e:
                    pass


def upload_to_hf(
    _datasetdict,
    directory,
    save_file_name,
    save_directory=None,
    hf_repo_name=None,
    hf_commit_message=None,
):
    """
    Upload to HF
    """
    from dotenv import load_dotenv

    load_dotenv()

    HF_TOKEN = os.getenv("HF_TOKEN")

    # parquet_dir = "parquet"
    # parquet_load_dir = os.path.join(directory, parquet_dir)

    # if not os.path.isdir(parquet_load_dir):
    #     os.makedirs(parquet_load_dir)

    print(
        f"\n\n>> [DatasetDict] ({directory})\n[Num of rows are]: {len(_datasetdict['train'])}\n[Parquet name]: {save_directory}\n\n"
    )
    if hf_commit_message is None:
        hf_commit_message = f"Upload Dataset - {save_file_name}"

    try:
        train_dataset = _datasetdict
        train_dataset.push_to_hub(
            hf_repo_name,
            token=HF_TOKEN,
            config_name=save_file_name,
            commit_message=hf_commit_message,
            private=False,
        )
        print(f">> Upload to HF is done !\n\n")

    except Exception as E:
        print(f"ERROR with saving {directory}, {E}")


def save_into_datadict(
    train_file_dir: str = "",
    test_file_dir: str = "",
    save_directory: str = "",
    save_file_name: str = "",
    hf_repo_name: str = "",
    hf_commit_message: str = "",
):
    """
    jsonl포맷 파일을 Datadict 형태로 변환하여 저장합니다.
    """

    def _gen(_list):
        for item in _list:
            yield item

    train_list = jsonl_read(train_file_dir)
    test_list = None
    if test_file_dir != "" and test_file_dir is not None:
        test_list = jsonl_read(test_file_dir)

    save_directory = "../data/datasets"
    save_file_name = save_file_name
    save_directory = os.path.join(save_directory, save_file_name)

    if not os.path.exists(save_directory):
        os.makedirs(save_directory)

    # datasetdict 으로 변환
    train_converted = Dataset.from_generator(lambda: _gen(train_list))
    if test_list:
        test_converted = Dataset.from_generator(lambda: _gen(test_list))
        _datasetdict = text_converted = DatasetDict(
            {"train": train_converted, "test": test_converted}
        )
    else:
        _datasetdict = text_converted = DatasetDict({"train": train_converted})
    text_converted.save_to_disk(save_directory)

    print(f">> Now Upload to HF . . .")

    upload_to_hf(
        _datasetdict=_datasetdict,
        directory=save_directory,
        save_file_name=save_file_name,
        # save_directory=dataset_dir,
        hf_repo_name=hf_repo_name,
        hf_commit_message=hf_commit_message,
    )


# if __name__ == "__main__":
#     save_into_datadict(
#         train_file_dir="../data/multiturn_data_0625_1_post.jsonl",
#         train_file_dir=None,
#         save_directory="../data/datasets",
#         save_file_name="KoAlpaca_v1.1_orbit_v1.5_multiturn",
#         hf_repo_name="DinoTheLewis/KoAlpaca_persona_multiturn",
#         hf_commit_message="Upload Dataset - KoAlpaca_v1.1_orbit_v1.5_multiturn",
#     )
