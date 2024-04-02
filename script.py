import os
import json
from PIL import Image
import argparse

def yolo_to_coco(image_dir, label_dir, classes_file, output_file):
    with open(classes_file, 'r') as f:
        classes = f.read().strip().split('\n')
    
    coco_dataset = {
        "images": [],
        "annotations": [],
        "categories": []
    }
    
    for idx, class_name in enumerate(classes):
        coco_dataset["categories"].append({
            "id": idx + 1,
            "name": class_name,
            "supercategory": "none"
        })
    
    image_id = 1
    annotation_id = 1
    
    for filename in os.listdir(image_dir):
        if not filename.endswith(('.png', '.jpg', '.jpeg')):
            continue
        
        image_path = os.path.join(image_dir, filename)
        with Image.open(image_path) as img:
            width, height = img.size
        
        coco_dataset["images"].append({
            "id": image_id,
            "width": width,
            "height": height,
            "file_name": filename
        })
        
        label_path = os.path.join(label_dir, os.path.splitext(filename)[0] + '.txt')
        
        if os.path.exists(label_path):
            with open(label_path, 'r') as f:
                for line in f:
                    class_id, x_center, y_center, w, h = map(float, line.strip().split())
                    x_min = (x_center - w / 2) * width
                    y_min = (y_center - h / 2) * height
                    abs_width = w * width
                    abs_height = h * height
                    
                    coco_dataset["annotations"].append({
                        "id": annotation_id,
                        "image_id": image_id,
                        "category_id": int(class_id) + 1,
                        "bbox": [x_min, y_min, abs_width, abs_height],
                        "area": abs_width * abs_height,
                        "iscrowd": 0
                    })
                    annotation_id += 1
        
        image_id += 1
    
    with open(output_file, 'w') as f:
        json.dump(coco_dataset, f, indent=4)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert YOLO format annotations to COCO format.")
    parser.add_argument("--images", type=str, help="Directory containing images.")
    parser.add_argument("--labels", type=str, help="Directory containing YOLO format label files.")
    parser.add_argument("--classes", type=str, help="File containing class names, one per line.")
    parser.add_argument("--output", type=str, default="coco_annotations.json", help="Output file for COCO format annotations (default: coco_annotations.json).")

    args = parser.parse_args()

    yolo_to_coco(args.images, args.labels, args.classes, args.output)

    print("Conversion to COCO format completed.")