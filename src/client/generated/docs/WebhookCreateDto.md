# WebhookCreateDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**endpoint** | **str** |  | 
**name** | **str** |  | 
**project_id** | **int** |  | 
**settings** | [**DefaultWebhookSettings**](DefaultWebhookSettings.md) |  | [optional] 

## Example

```python
from src.client.generated.models.webhook_create_dto import WebhookCreateDto

# TODO update the JSON string below
json = "{}"
# create an instance of WebhookCreateDto from a JSON string
webhook_create_dto_instance = WebhookCreateDto.from_json(json)
# print the JSON string representation of the object
print(WebhookCreateDto.to_json())

# convert the object into a dict
webhook_create_dto_dict = webhook_create_dto_instance.to_dict()
# create an instance of WebhookCreateDto from a dict
webhook_create_dto_from_dict = WebhookCreateDto.from_dict(webhook_create_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


