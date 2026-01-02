# WebhookPatchDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**endpoint** | **str** |  | [optional] 
**name** | **str** |  | [optional] 
**settings** | [**DefaultWebhookSettings**](DefaultWebhookSettings.md) |  | [optional] 

## Example

```python
from src.client.generated.models.webhook_patch_dto import WebhookPatchDto

# TODO update the JSON string below
json = "{}"
# create an instance of WebhookPatchDto from a JSON string
webhook_patch_dto_instance = WebhookPatchDto.from_json(json)
# print the JSON string representation of the object
print(WebhookPatchDto.to_json())

# convert the object into a dict
webhook_patch_dto_dict = webhook_patch_dto_instance.to_dict()
# create an instance of WebhookPatchDto from a dict
webhook_patch_dto_from_dict = WebhookPatchDto.from_dict(webhook_patch_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


