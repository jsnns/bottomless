import anthropic
from typing import List, Dict, Any, Optional
import base64
import json
from image_utils import process_image
from dataclasses import dataclass

client = anthropic.Anthropic()


def extract_json_from_content(content: str) -> Dict[str, Any]:
    json_block = content.split("```json")[1].split("```")[0]
    return json.loads(json_block)


@dataclass
class ShoppingListItem:
    item_name: str
    category: str
    quantity: int
    unit: Optional[str] = None
    brand_name: Optional[str] = None


def get_shopping_list(
    before_image_path: str, after_image_path: str
) -> List[ShoppingListItem]:

    message = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=1000,
        temperature=0,
        system='You will be provided with images of my Fridge on 7 days ago and now. You should output the consumption this week along with a shopping list based my consumption.\n\nOutput sections:\n\n1. A list of consumed items between both images.\n2. A ```json {}``` block with two keys "consumed" and "shopping_list" each should be a list of objects with "item_name", "category", "quantity", "unit", and "brand_name" keys. Specify unit in the unit most likely to be used by the store. For ex "six pack" and not "can".',
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/jpeg",
                            "data": process_image(before_image_path),
                        },
                    },
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/jpeg",
                            "data": process_image(after_image_path),
                        },
                    },
                    {
                        "type": "text",
                        "text": "\nPlease provide a shopping list based on the current state of the fridge. Output your json in a markdown code block with the language specified as json.",
                    },
                ],
            }
        ],
    )

    d = extract_json_from_content(message.content[0].text)  # type: ignore

    return [ShoppingListItem(**item) for item in d["shopping_list"]]
