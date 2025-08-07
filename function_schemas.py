pose_detection_function = {
    "name": "extract_pose_names",
    "description": "Extract yoga pose names (English or Sanskrit) mentioned in the answer",
    "parameters": {
        "type": "object",
        "properties": {
            "pose_names": {
                "type": "array",
                "items": {"type": "string"},
                "description": "List of yoga pose names mentioned"
            }
        },
        "required": ["pose_names"],
    },
}

create_sequence_function = {
    "name": "create_yoga_sequence",
    "description": "Create a yoga pose sequence with timings based on user input or style",
    "parameters": {
        "type": "object",
        "properties": {
            "sequence_name": {
                "type": "string",
                "description": "Name or theme of the yoga sequence"
            },
            "poses": {
                "type": "array",
                "items": {"type": "string"},
                "description": "List of yoga poses to include in the sequence"
            },
            "style": {
                "type": "string",
                "enum": ["hatha", "yin", "vinyasa"],
                "description": "Yoga style to determine default pose durations"
            }
        },
        "required": ["poses", "style"]
    }
}

get_pose_benefits_function = {
    "name": "get_pose_benefits",
    "description": "Get benefits and contraindications of yoga poses by searching the knowledge base.",
    "parameters": {
        "type": "object",
        "properties": {
            "pose_names": {
                "type": "array",
                "description": "List of yoga pose names",
                "items": {"type": "string"},
            }
        },
        "required": ["pose_names"],
    },
}

get_yogajournal_pose_image_function = {
    "name": "get_yogajournal_pose_image",
    "description": "Get the Yoga Journal image URL for a yoga pose.",
    "parameters": {
        "type": "object",
        "properties": {
            "pose_name": {"type": "string", "description": "The name of the yoga pose."}
        },
        "required": ["pose_name"],
    }
}