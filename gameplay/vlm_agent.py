import torch
import os
from tqdm import tqdm
from abc import ABC, abstractmethod
from copy import deepcopy


from llava.constants import IMAGE_TOKEN_INDEX, DEFAULT_IMAGE_TOKEN, DEFAULT_IM_START_TOKEN, DEFAULT_IM_END_TOKEN
from llava.conversation import conv_templates, SeparatorStyle
from llava.model.builder import load_pretrained_model
from llava.utils import disable_torch_init
from llava.mm_utils import tokenizer_image_token, process_images, get_model_name_from_path

from PIL import Image


class BaseConverter(ABC):
    def __init__(self):
        self.game_cnt = 0

    def reset(self):
        self.game_cnt += 1
        self.step = 0
        self.conversation = []

    @abstractmethod
    def prepare_user_input(self):
        pass

    @abstractmethod
    def get_input(self, fig_path: str = None) -> dict:
        pass

    @abstractmethod
    def get_action(self, model_output: str) -> str:
        pass



def get_role(role:str, roles):
    if role.lower() == "human" or role.lower() == "user":
        return roles[0]
    elif role.lower() == "assistant" or role.lower() == "gpt" or role.lower() == "bot":
        return roles[1]
    else:
        raise ValueError(f"Role {role} not found.")

class VLMAgent:
    def __init__(
        self, 
        converter: BaseConverter, 
        model_path:str, 
        model_base: str = None,
        conv_mode: str = 'vicuna_v1',
        temperature: float = 0,
        top_p: float = None,
        num_beams: int = 1,
        max_new_tokens: int = 512,
    ):
        self.converter = converter

        disable_torch_init()
        model_path = os.path.expanduser(model_path)
        model_name = get_model_name_from_path(model_path)
        tokenizer, model, image_processor, context_len = load_pretrained_model(model_path, model_base, model_name)

        if 'plain' in model_name and 'finetune' not in model_name.lower() and 'mmtag' not in conv_mode:
            conv_mode = conv_mode + '_mmtag'
            print(f'It seems that this is a plain model, but it is not using a mmtag prompt, auto switching to {conv_mode}.')

        self.tokenizer = tokenizer
        self.model = model
        self.image_processor = image_processor
        self.model_config = model.config
        self.conv_mode = conv_mode
        self.temperature = temperature
        self.top_p = top_p
        self.num_beams = num_beams
        self.max_new_tokens = max_new_tokens

    def tokenize_input(self, line: dict):
        image_file = line.get("image", None)
        conv = conv_templates[self.conv_mode].copy()
        for chat in line["conversations"]:
            role = chat["from"]
            text = chat["value"]
            if self.model_config.mm_use_im_start_end:
                replace_token = DEFAULT_IMAGE_TOKEN
                replace_token = DEFAULT_IM_START_TOKEN + replace_token + DEFAULT_IM_END_TOKEN
                text = text.replace(replace_token, DEFAULT_IMAGE_TOKEN)
            conv.append_message(get_role(role,conv.roles), text)

        if conv.messages[-1][0] != conv.roles[1]:
            conv.append_message(conv.roles[1], None)
        prompt = conv.get_prompt()

        if image_file is not None:
            image = Image.open(image_file).convert('RGB')
            image_tensor = process_images([image], self.image_processor, self.model_config)[0]
        else:
            crop_size = self.image_processor.crop_size
            image = Image.new('RGB', (crop_size['width'], crop_size['height']))
            image_tensor = process_images([image], self.image_processor, self.model_config)[0]

        input_ids = tokenizer_image_token(prompt, self.tokenizer, IMAGE_TOKEN_INDEX, return_tensors='pt')
        return input_ids.unsqueeze(0), image_tensor.unsqueeze(0), [image.size]
    
    def reset(self):
        self.converter.reset()
    
    def take_action(self, img: str) -> str: 
        self.converter.prepare_user_input()
        input_dict = self.converter.get_input(img)
        input_ids, image_tensor, image_sizes = self.tokenize_input(input_dict)
        input_ids = input_ids.to(device='cuda', non_blocking=True)

        with torch.inference_mode():
            output_ids = self.model.generate(
                input_ids,
                images=image_tensor.to(dtype=torch.float16, device='cuda', non_blocking=True),
                image_sizes=image_sizes,
                do_sample=True if self.temperature > 0 else False,
                temperature=self.temperature,
                top_p=self.top_p,
                num_beams=self.num_beams,
                max_new_tokens=self.max_new_tokens,
                use_cache=True)

        outputs = self.tokenizer.batch_decode(output_ids, skip_special_tokens=True)[0].strip()
        action = self.converter.get_action(outputs)
        return action