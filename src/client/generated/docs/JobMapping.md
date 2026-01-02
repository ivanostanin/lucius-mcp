# JobMapping


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**from_id** | **int** |  | [optional] 
**to_id** | **int** |  | 

## Example

```python
from src.client.generated.models.job_mapping import JobMapping

# TODO update the JSON string below
json = "{}"
# create an instance of JobMapping from a JSON string
job_mapping_instance = JobMapping.from_json(json)
# print the JSON string representation of the object
print(JobMapping.to_json())

# convert the object into a dict
job_mapping_dict = job_mapping_instance.to_dict()
# create an instance of JobMapping from a dict
job_mapping_from_dict = JobMapping.from_dict(job_mapping_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


