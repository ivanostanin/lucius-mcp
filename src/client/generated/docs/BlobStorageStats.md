# BlobStorageStats


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**available_space** | **int** |  | [optional] 
**total_space** | **int** |  | [optional] 
**used_space** | **int** |  | [optional] 

## Example

```python
from src.client.generated.models.blob_storage_stats import BlobStorageStats

# TODO update the JSON string below
json = "{}"
# create an instance of BlobStorageStats from a JSON string
blob_storage_stats_instance = BlobStorageStats.from_json(json)
# print the JSON string representation of the object
print(BlobStorageStats.to_json())

# convert the object into a dict
blob_storage_stats_dict = blob_storage_stats_instance.to_dict()
# create an instance of BlobStorageStats from a dict
blob_storage_stats_from_dict = BlobStorageStats.from_dict(blob_storage_stats_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


