import json

def modify_and_extend_json(file_path):
    # Load data from the JSON file
    with open(file_path, 'r') as file:
        data = json.load(file)
    
    # Modify existing entries and increment territoryId starting from 2601
    for index, entry in enumerate(data):
        entry['HMAC'] = ""  # Set HMAC to an empty string
        entry['territoryId'] = 2601 + index  # Increment territoryId starting from 2601
    
    # Adding new entries for 'monkey' region
    new_entries = [{
        'territoryId': 2679 + i, 
        'region': 'monkey', 
        'nodeNumber': i + 1, 
        'reward': 'banana', 
        'HMAC': ''
    } for i in range(26)]
    
    # Extend the existing data with the new entries
    data.extend(new_entries)
    
    # Save the modified data back to the same JSON file
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=2)
        
    print(json.dumps(data, indent=2))

# Example usage
file_path = 'siegeData.json'  # Update this to the path of your JSON file
modify_and_extend_json(file_path)